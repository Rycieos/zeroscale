import asyncio
import logging
from signal import Signals

from zeroscale.status import Status
from zeroscale.base_server import BaseServer

logger = logging.getLogger(__name__)


class Server(BaseServer):
    def __init__(self, *server_args):
        if not server_args:
            raise ValueError("Need a server command to run")

        self.server_command = server_args
        self.name = server_args[0]

        self.proc = None
        self.status = Status.stopped
        self.working_directory = None
        self.stop_signal = Signals.SIGINT
        self.pause_signal = Signals.SIGTSTP
        self.unpause_signal = Signals.SIGCONT

    def set_working_directory(self, working_directory: str):
        self.working_directory = working_directory

    def set_stop_signal(self, signal: Signals):
        self.stop_signal = signal

    def set_pause_signal(self, signal: Signals):
        self.pause_signal = signal

    def set_unpause_signal(self, signal: Signals):
        self.unpause_signal = signal

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

    async def pause(self):
        if self.status is not Status.running:
            return

        logger.info("Pausing %s server", self.name)
        self.status = Status.paused
        self.proc.send_signal(self.pause_signal)

    async def unpause(self):
        if self.status is not Status.paused:
            return

        logger.info("Unpausing %s server", self.name)
        self.status = Status.running
        self.proc.send_signal(self.unpause_signal)

    def close(self):
        if self.proc:
            try:
                self.proc.kill()
            except ProcessLookupError:
                pass
