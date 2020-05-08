import asyncio
import logging

from .status import Status

logger = logging.getLogger(__name__)


class BaseServer:

    async def start(self):
        raise NotImplementedError

    async def stop(self):
        raise NotImplementedError

    async def pause(self):
        raise NotImplementedError

    async def unpause(self):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError

    async def is_valid_connection(self, client_reader):
        return True

    def fake_status(self) -> bytes:
        return b"Server starting up..."
