import asyncio
import logging
from signal import Signals

from zeroscale.status import Status

logger = logging.getLogger(__name__)


class Server:
    def __init__(self, *server_args, working_directory: str = None):
        if not server_args:
            raise ValueError("Need a server command to run")

        self.server_command = server_args
        self.working_directory = working_directory
        self.name = server_args[0]

        self.proc = None
        self.status = Status.stopped
        self.stop_signal = Signals.SIGINT

    def set_stop_signal(self, signal: Signals):
        self.stop_signal = signal

    async def start(self):
        if self.status is not Status.stopped:
            return

        logger.info("Starting %s server", self.name)
        self.status = Status.starting

        self.proc = await asyncio.create_subprocess_exec(
            *self.server_command, cwd=self.working_directory
        )

        logger.info("%s server online", self.name)
        self.status = Status.running

    async def stop(self):
        if self.status is not Status.running:
            return

        logger.info("Stopping %s server", self.name)
        self.status = Status.stopping

        self.proc.send_signal(self.stop_signal)
        await self.proc.wait()

        logger.info("%s server offline", self.name)
        self.status = Status.stopped

    def fake_status(self) -> bytes:
        return b"Server starting up..."
