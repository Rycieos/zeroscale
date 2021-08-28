import asyncio
import logging

logger = logging.getLogger(__name__)


async def pipe(reader, writer):
    try:
        while not reader.at_eof():
            writer.write(await reader.read(2048))
            await writer.drain()
    finally:
        writer.close()


async def proxy(client_reader, client_writer, server_host, server_port):
    try:
        remote_reader, remote_writer = await asyncio.wait_for(
            asyncio.open_connection(host=server_host, port=server_port), timeout=20
        )
        await asyncio.gather(
            pipe(client_reader, remote_writer),
            pipe(remote_reader, client_writer)
        )
    except (ConnectionError, IOError, EOFError) as e:
        logger.debug("Connection from %s lost", client_writer.get_extra_info('peername'), exc_info=e)
    finally:
        client_writer.close()
