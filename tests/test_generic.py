import asyncio
import pytest
from signal import Signals

from zeroscale.plugins.generic import Server as Generic
from zeroscale.status import Status

@pytest.mark.asyncio
async def test_init(unused_tcp_port):
    with pytest.raises(ValueError):
        Generic()

    server = Generic('tests/echo_server.py', str(unused_tcp_port))
    await server.start()

    # Wait for the server to bind to port.
    await asyncio.sleep(.5)

    reader, writer = await asyncio.open_connection(port=unused_tcp_port)

    data = b'some test stringi\n'
    writer.write(data)

    assert data == await reader.readline()

    writer.close()
    server.close()
    await server.proc.wait()
    assert server.proc.returncode is not None

    # Close is no-op if already stopped.
    server.close()
    assert server.proc.returncode is not None

@pytest.mark.asyncio
async def test_cycle(unused_tcp_port):
    server = Generic('tests/echo_server.py', str(unused_tcp_port))
    assert server.status is Status.stopped

    await server.start()
    assert server.status is Status.running
    assert server.proc.returncode is None

    # Start is no-op if already running.
    await server.start()
    assert server.status is Status.running
    assert server.proc.returncode is None

    await server.stop()
    assert server.status is Status.stopped
    assert server.proc.returncode is not None

    # Stop is no-op if already stopped.
    await server.stop()
    assert server.status is Status.stopped
    assert server.proc.returncode is not None

@pytest.mark.asyncio
async def test_pausing(unused_tcp_port):
    server = Generic('tests/echo_server.py', str(unused_tcp_port))
    assert server.status is Status.stopped

    await server.start()
    assert server.status is Status.running
    assert server.proc.returncode is None

    # Wait for the server to bind to port.
    await asyncio.sleep(.5)

    reader, writer = await asyncio.open_connection(port=unused_tcp_port)

    data = b'some test stringi\n'
    writer.write(data)

    assert data == await reader.readline()
    writer.close()

    await server.pause()
    assert server.status is Status.paused
    assert server.proc.returncode is None

    # Pause is no-op if already paused.
    await server.pause()
    assert server.status is Status.paused
    assert server.proc.returncode is None

    await server.unpause()
    assert server.status is Status.running
    assert server.proc.returncode is None

    reader, writer = await asyncio.open_connection(port=unused_tcp_port)

    data = b'a different test stringi\n'
    writer.write(data)

    assert data == await reader.readline()
    writer.close()

    # Unpause is no-op if already unpaused.
    await server.unpause()
    assert server.status is Status.running
    assert server.proc.returncode is None

    await server.stop()
    assert server.status is Status.stopped
    assert server.proc.returncode is not None

def test_setters():
    server = Generic('tests/echo_server.py', 'none')

    server.set_working_directory('a/path')
    assert server.working_directory == 'a/path'

    server.set_stop_signal(Signals.SIGKILL)
    assert server.stop_signal == Signals.SIGKILL

    server.set_pause_signal(Signals.SIGHUP)
    assert server.pause_signal == Signals.SIGHUP

    server.set_unpause_signal(Signals.SIGTERM)
    assert server.unpause_signal == Signals.SIGTERM
