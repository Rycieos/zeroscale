import asyncio
import logging
import re

from zeroscale.status import Status

ENCODING = "utf-8"
READY_PATTERN = re.compile(
    "^Server started$", re.IGNORECASE
)

logger = logging.getLogger(__name__)


class Server:
    """Terraria server wrapper"""
    def __init__(self, *server_args, working_directory: str = None):

        if not server_args:
            self.server_command = ("TerrariaServer.bin.x86_64")
        else:
            self.server_command = server_args

        self.working_directory = working_directory

        self.fake_status_bytes = self._compile_fake_status_bytes()
        self.proc = None
        self.startup_task = None
        self.status = Status.stopped

    async def start(self):
        """Start the Terraria server"""

        if self.status is not Status.stopped:
            return

        logger.info("Starting Terraria server")
        self.status = Status.starting

        self.proc = await asyncio.create_subprocess_exec(
            *self.server_command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            cwd=self.working_directory,
        )

        self.startup_task = asyncio.ensure_future(self.await_server_ready())
        await self.startup_task

    async def await_server_ready(self):
        """Wait for the Terraria server to be ready to accept connections"""

        while not self.proc.stdout.at_eof():
            line = await self.proc.stdout.readline()
            if READY_PATTERN.match(line.decode(ENCODING)):
                logger.info("Terraria server online")
                self.status = Status.running
                return

    async def stop(self):
        """Stop the Terraria server"""

        # Stop if running or still starting up
        if self.status is Status.starting:
            # If we communicate() with the server before it is running,
            # The readline() from the start watcher will conflict
            # Do we need to check if the cancel is done?
            self.startup_task.cancel()
        elif self.status is not Status.running:
            return

        logger.info("Stopping Terraria server")
        self.status = Status.stopping
        self.proc.stdin.write("exit\n".encode(ENCODING))

        # Wait for shutdown
        # This needs to be communicate() and not wait() to avoid
        # blocking on filled stdout pipe
        # If the server runs long enough, can it actually fill the pipe
        # enough to block?
        await self.proc.communicate()
        logger.info("Terraria server offline")
        self.status = Status.stopped

    def fake_status(self) -> bytes:
        """Return the byte data with the starting up message"""

        return self.fake_status_bytes

    @staticmethod
    def _compile_fake_status_bytes() -> bytes:
        """Build the server error to send to a client to show it's starting up
            See https://seancode.com/terrafirma/net.html
            Send a $02 message to show the server isn't ready"""

        message = "Server is starting up... Please wait and try again".encode(ENCODING)

        data = bytearray()
        # Total packet length
        data.extend((len(message) + 6).to_bytes(2, byteorder="little"))
        # Server error enum (twice for some reason)
        data.extend(b"\x02\x02")
        # Message length
        data.extend(len(message).to_bytes(1, byteorder="little"))
        # Payload
        data.extend(message)
        # Null byte at the end to terminate the string
        data.extend(b"\x00")

        return data
