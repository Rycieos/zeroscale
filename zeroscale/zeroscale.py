import asyncio
import logging
import sys

from .proxy import proxy
from .status import Status

logger = logging.getLogger(__name__)


class ZeroScale:
    """ZeroScale proxy server that spins up a server when a client connects"""

    def __init__(
        self,
        server,
        listen_port: int,
        server_port: int,
        server_host: str = None,
        method_pause: bool = True,
        server_idle_shutdown: int = 15,
        server_shutdown_timeout: int = 15,
        ignore_bad_clients: bool = False,
    ):
        self.server = server
        self.listen_port = listen_port
        self.server_port = server_port
        self.server_host = server_host
        self.method_pause = method_pause
        self.server_idle_shutdown = server_idle_shutdown
        self.server_shutdown_timeout = server_shutdown_timeout
        self.ignore_bad_clients = ignore_bad_clients

        self.live_connections = 0
        self.kill_task = None

    async def create_connection(self, client_reader, client_writer):
        """Handle an incoming client connection, by proxying to the plugin server"""

        self.cancel_stop()
        self.live_connections += 1
        logger.debug("New connection, total clients: %i", self.live_connections)

        try:
            await proxy(client_reader, client_writer,
                    self.server_host, self.server_port)
        except (ConnectionError, TimeoutError, asyncio.TimeoutError):
            logger.debug("Proxy connection error", exc_info=True)
        finally:
            self.live_connections -= 1
            logger.debug("Lost connection, total clients: %i", self.live_connections)
            if self.live_connections <= 0:
                self.schedule_stop()

    async def handle_unready(self, client_reader, client_writer):
        try:
            if self.ignore_bad_clients or await self.server.is_valid_connection(client_reader):
                logger.debug("Sending fake response")
                client_writer.write(self.server.fake_status())
                client_writer.close()
                await self.start_then_schedule_stop()
            else:
                logger.debug("Invalid client attempted connection")
        except (ConnectionError, TimeoutError, asyncio.TimeoutError):
            logger.debug("Invalid client; connection error")
        finally:
            client_writer.close()

    async def handle_client_pausing(self, client_reader, client_writer):
        """Handle an incoming client connection, by proxying after unpausing"""

        if self.server.status is Status.starting:
            await self.handle_unready(client_reader, client_writer)
            return

        if self.server.status is Status.paused:
            await self.server.unpause()

        await self.create_connection(client_reader, client_writer)

    async def handle_client_stopping(self, client_reader, client_writer):
        """Handle an incoming client connection, either by proxying or sending a status"""

        if self.server.status is Status.running:
            await self.create_connection(client_reader, client_writer)

        else:
            await self.handle_unready(client_reader, client_writer)

    async def handle_client(self, client_reader, client_writer):
        """Handle an incoming client connection, depending on our manage method"""

        logger.debug("New connection, server is %s", self.server.status.name)

        if self.method_pause:
            await self.handle_client_pausing(client_reader, client_writer)
        else:
            await self.handle_client_stopping(client_reader, client_writer)

    async def start_then_schedule_stop(self):
        await self.server.start()
        # In case no one connects after starting
        self.schedule_stop()

    def schedule_stop(self):
        """Schedule a run of the delay_stop() call"""

        if self.server.status is not Status.running:
            return

        self.cancel_stop()
        logger.debug("Scheduling %s server stop", type(self.server).__name__)
        self.kill_task = asyncio.ensure_future(self.delay_stop())

    def cancel_stop(self):
        """Kill the scheduled run of delay_stop() before it actually stops"""

        if self.kill_task and not self.kill_task.done():
            logger.debug("Canceling %s server stop", type(self.server).__name__)
            self.kill_task.cancel()

    async def delay_stop(self):
        """Stop the plugin server, but wait first"""

        await asyncio.sleep(self.server_idle_shutdown)

        logger.debug("No clients online for %i seconds", self.server_idle_shutdown)
        if self.method_pause:
            await self.server.pause()
        else:
            await self.server.stop()

    def start_server(self):
        """Start the proxy server"""

        loop = asyncio.get_event_loop()

        if sys.platform == 'win32':
            # See https://docs.python.org/3/library/asyncio-platforms.html#subprocess-support-on-windows
            loop = asyncio.ProactorEventLoop()

        if self.method_pause:
            # If the managing method is pausing, then we need to do two things:
            # 1. Make sure the server is actually running
            # 2. Make sure the server is paused after that
            loop.create_task(self.start_then_schedule_stop())

        coro = asyncio.start_server(self.handle_client, port=self.listen_port)
        proxy_server = loop.run_until_complete(coro)

        for socket in proxy_server.sockets:
            logger.debug("Listening on %s", socket.getsockname())

        # Serve requests until Ctrl+C is pressed
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            loop.run_until_complete(
                asyncio.wait_for(
                    self.server.stop(), timeout=self.server_shutdown_timeout
                )
            )
        finally:
            self.cancel_stop()
            self.server.close()
            proxy_server.close()
            loop.run_until_complete(proxy_server.wait_closed())
            loop.close()
