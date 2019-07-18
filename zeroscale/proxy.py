import asyncio


async def pipe(reader, writer):
    try:
        while not reader.at_eof():
            writer.write(await reader.read(2048))
    finally:
        writer.close()


async def proxy(client_reader, client_writer, server_port):
    try:
        remote_reader, remote_writer = await asyncio.wait_for(
            asyncio.open_connection(port=server_port), timeout=20
        )
        await asyncio.gather(
            pipe(client_reader, remote_writer),
            pipe(remote_reader, client_writer)
        )
    finally:
        client_writer.close()
