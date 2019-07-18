import asyncio
import pytest
from zeroscale.plugins.generic import Server as Generic

@pytest.mark.asyncio
async def test_init(unused_tcp_port):
    server = Generic('tests/echo_server.py', str(unused_tcp_port))
    await server.start()

    # Wait for the server to bind to port
    await asyncio.sleep(.5)

    reader, writer = await asyncio.open_connection(port=unused_tcp_port)

    data = b'some test stringi\n'
    writer.write(data)

    assert data == await reader.readline()

    await server.stop()
