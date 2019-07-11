#!/usr/bin/env python3

import asyncio
import logging
import time
from zeroscale.status import Status
from zeroscale.plugins.minecraft import Minecraft

class ZeroScale:
    def __init__(self, server,
            listen_port: int,
            server_port: int,
            server_idle_shutdown: int = 15):
        self.server = server
        self.listen_port = listen_port
        self.server_port = server_port
        self.server_idle_shutdown = server_idle_shutdown

        self.live_connections = 0
        self.kill_task = None

    async def handle_client(self, client_reader, client_writer):
        logging.debug('New connection, server is %s', self.server.status.name)
        if self.server.status is Status.running:
            await self.proxy(client_reader, client_writer)
        else:
            await self.send_server_status(client_reader, client_writer)
            await self.server.start()
            # In case no one connects after starting
            self.schedule_stop()

    async def send_server_status(self, client_reader, client_writer):
        logging.debug('Sending fake response')

        try:
            client_writer.write(self.server.fake_status())
        finally:
            client_writer.close()

    @staticmethod
    async def pipe(reader, writer):
        try:
            while not reader.at_eof():
                writer.write(await reader.read(2048))
        finally:
            writer.close()

    async def proxy(self, client_reader, client_writer):
        try:
            self.live_connections += 1
            logging.info('New connection, total clients: %i', self.live_connections)
            if self.live_connections > 0:
                self.cancel_stop()

            remote_reader, remote_writer = await asyncio.wait_for(
                    asyncio.open_connection(port=self.server_port), timeout=20)
            await asyncio.gather(
                ProxyServer.pipe(client_reader, remote_writer),
                ProxyServer.pipe(remote_reader, client_writer)
            )
        finally:
            client_writer.close()

            self.live_connections -= 1
            logging.info('Lost connection, total clients: %i', self.live_connections)
            if self.live_connections <= 0:
                self.schedule_stop()

    def schedule_stop(self):
        self.cancel_stop()
        logging.debug('Scheduling %s server stop', type(self.server).__name__)
        self.kill_task = asyncio.ensure_future(self.delay_stop())

    def cancel_stop(self):
        if self.kill_task and not self.kill_task.cancelled():
            logging.debug('Canceling %s server stop', type(self.server).__name__)
            self.kill_task.cancel()

    async def delay_stop(self):
        await asyncio.sleep(self.server_idle_shutdown)

        logging.debug('No clients online for %i seconds', self.server_idle_shutdown)
        await self.server.stop()

    def start_server(self):
        loop = asyncio.get_event_loop()
        coro = asyncio.start_server(self.handle_client, port=self.listen_port)
        server = loop.run_until_complete(coro)

        for socket in server.sockets:
            logging.info('Listening on %s', socket.getsockname())

        # Serve requests until Ctrl+C is pressed
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass

        # Close the server
        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.close()
