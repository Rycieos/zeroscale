import asyncio
import pytest

from zeroscale.base_server import BaseServer

@pytest.mark.asyncio
async def test_base():
    server = BaseServer()

    with pytest.raises(NotImplementedError):
        await server.start()
    with pytest.raises(NotImplementedError):
        await server.stop()
    with pytest.raises(NotImplementedError):
        await server.pause()
    with pytest.raises(NotImplementedError):
        await server.unpause()
    with pytest.raises(NotImplementedError):
        server.close()

    assert await server.is_valid_connection(None)

    assert type(server.fake_status()) is bytes
