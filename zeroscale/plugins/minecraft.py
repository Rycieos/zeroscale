import asyncio
import json
import logging
import re
from typing import List
from zeroscale.status import Status

encoding = 'utf-8'
ready_pattern = re.compile('.*\\[Server thread/INFO\\]: Done \\([0-9.]*s\\).*', re.IGNORECASE)

class Minecraft():
    def __init__(self,
            jar_name: str = "minecraft_server.jar",
            server_command: List[str] = None):

        if server_command is None:
            self.server_command = [
                'java',
                '-jar',
                self.jar_name,
                'nogui'
            ]
        else:
            self.server_command = server_command

        self.status = Status.stopped
        self.startup_task = None

    async def start(self):
        if self.status is not Status.stopped:
            return

        logging.info('Starting Minecraft server')
        self.status = Status.starting
        self.proc = await asyncio.create_subprocess_exec(
            *self.server_command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE
        )

        self.startup_task = asyncio.ensure_future(self.await_server_ready())

    async def await_server_ready(self):
        while not self.proc.stdout.at_eof():
            line = await self.proc.stdout.readline()
            if ready_pattern.match(line.decode(encoding)):
                logging.info('Minecraft server online')
                self.status = Status.running
                return

    async def stop(self):
        if self.status is not Status.running:
            return

        logging.info('Stopping Minecraft server')
        self.status = Status.stopping
        self.proc.stdin.write('/stop\n'.encode(encoding))

        # Wait for shutdown
        await self.proc.communicate()
        logging.info('Minecraft server offline')
        self.status = Status.stopped

    def fake_status(self) -> bytes:
        json_data = json.dumps({
            "description": {"text": "Server starting up..."},
            "players": {"max": 0, "online": 0},
            "version": {"name": "loading", "protocol": 0}
        }, separators=(',', ':')).encode(encoding)

        data = bytearray()
        # Total packet length
        data.extend((len(json_data) + 2).to_bytes(1, byteorder='big'))
        # Ping enum
        data.extend(b'\x00')
        # Payload length
        data.extend(len(json_data).to_bytes(1, byteorder='big'))
        data.extend(json_data)

        return data
