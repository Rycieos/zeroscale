import asyncio
import json
import logging
import re
from typing import List

from zeroscale.status import Status

encoding = 'utf-8'
ready_pattern = re.compile('.*\\[Server thread/INFO\\]: Done \\([0-9.]*s\\).*', re.IGNORECASE)

logger = logging.getLogger(__name__)

class Server():
    def __init__(self,
            jar_name: str = "server.jar",
            server_command: List[str] = None):

        if server_command is None:
            self.server_command = [
                'java',
                '-jar',
                jar_name,
                'nogui'
            ]
        else:
            self.server_command = server_command

        self.status = Status.stopped
        self.fake_status_bytes = self._compile_fake_status_bytes()

    async def start(self):
        if self.status is not Status.stopped:
            return

        logger.info('Starting Minecraft server')
        self.status = Status.starting

        self.proc = await asyncio.create_subprocess_exec(
            *self.server_command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE
        )

        await self.await_server_ready()

    async def await_server_ready(self):
        while not self.proc.stdout.at_eof():
            line = await self.proc.stdout.readline()
            if ready_pattern.match(line.decode(encoding)):
                logger.info('Minecraft server online')
                self.status = Status.running
                return

    async def stop(self):
        if self.status is not Status.running:
            return

        logger.info('Stopping Minecraft server')
        self.status = Status.stopping
        self.proc.stdin.write('/stop\n'.encode(encoding))

        # Wait for shutdown
        await self.proc.communicate()
        logger.info('Minecraft server offline')
        self.status = Status.stopped

    def fake_status(self) -> bytes:
        return self.fake_status_bytes

    @staticmethod
    def _compile_fake_status_bytes() -> bytes:
        json_data = json.dumps({
            "description": {"text": "Server starting up..."},
            "players": {"max": 0, "online": 0},
            "version": {"name": "loading", "protocol": 0}
        }, separators=(',', ':')).encode(encoding)

        data = bytearray()
        # Total packet length
        # Seems to not work if above 0x80
        data.extend((len(json_data) + 2).to_bytes(1, byteorder='big'))
        # Ping enum
        data.extend(b'\x00')
        # Payload length
        data.extend(len(json_data).to_bytes(1, byteorder='big'))
        data.extend(json_data)

        return data
