# zeroscale

[![Build Status](https://travis-ci.org/Rycieos/zeroscale.svg?branch=master)](https://travis-ci.org/Rycieos/zeroscale)
[![Coverage Status](https://coveralls.io/repos/github/Rycieos/zeroscale/badge.svg?branch=master)](https://coveralls.io/github/Rycieos/zeroscale?branch=master)
[![Requirements Status](https://requires.io/github/Rycieos/zeroscale/requirements.svg?branch=master)](https://requires.io/github/Rycieos/zeroscale/requirements/?branch=master)

[![PyPI Package latest release](https://img.shields.io/pypi/v/zeroscale.svg)](https://pypi.python.org/pypi/zeroscale)
[![PyPI Wheel](https://img.shields.io/pypi/wheel/zeroscale.svg)](https://pypi.python.org/pypi/zeroscale)
[![Supported versions](https://img.shields.io/pypi/pyversions/zeroscale.svg)](https://pypi.python.org/pypi/zeroscale)

Scale-to-zero any server

Some servers don't idle well. Either they constantly compute things (like Minecraft keeping spawn chunks always loaded), or they do things you don't want them to. `zeroscale` sits in front of a server and only spins it up when someone tries to connect to it, proxying the connection.

This won't save you any cost if you pay for uptime, but it will save CPU cycles.

## Usage
```
usage: zeroscale [-h] [--idle_shutdown IDLE_SHUTDOWN]
                 [--working_directory WORKING_DIRECTORY]
                 [--plugin_argument PLUGIN_ARGUMENT] [--info] [--debug]
                 server_plugin listen_port server_port

Scale a server to zero.

positional arguments:
  server_plugin         Package name of the server plugin. Must be in plugins
                        dir.
  listen_port           Port for the proxy server, where clients will connect.
  server_port           Port that the real server will be listening on.

optional arguments:
  -h, --help            show this help message and exit
  --idle_shutdown IDLE_SHUTDOWN, -t IDLE_SHUTDOWN
                        Time in seconds after last client disconects to kill
                        the server.
  --working_directory WORKING_DIRECTORY, -w WORKING_DIRECTORY
                        Directory to start the server process.
  --plugin_argument PLUGIN_ARGUMENT, -a PLUGIN_ARGUMENT
                        Arguments to pass to the Server() constructor in the
                        plugin. Can be called multiple times.
  --info, -i            Enable info logging.
  --debug, -d           Enable debug logging. Default is WARNING
```

## Example
```
$ zeroscale minecraft 25565 25575 --debug
DEBUG:zeroscale.zeroscale:Listening on ('::', 25565, 0, 0)
DEBUG:zeroscale.zeroscale:Listening on ('0.0.0.0', 25565)
...
DEBUG:zeroscale.zeroscale:New connection, server is stopped
DEBUG:zeroscale.zeroscale:Sending fake response  # Actually shows valid message in client!
INFO:zeroscale.plugins.minecraft:Starting Minecraft server
...
INFO:zeroscale.plugins.minecraft:Minecraft server online
DEBUG:zeroscale.zeroscale:Scheduling Server server stop
...
DEBUG:zeroscale.zeroscale:New connection, server is running
DEBUG:zeroscale.zeroscale:New connection, total clients: 1
DEBUG:zeroscale.zeroscale:Canceling Server server stop
...
DEBUG:zeroscale.zeroscale:Lost connection, total clients: 0
DEBUG:zeroscale.zeroscale:Scheduling Server server stop
...
DEBUG:zeroscale.zeroscale:No clients online for 15 seconds
INFO:zeroscale.plugins.minecraft:Stopping Minecraft server
INFO:zeroscale.plugins.minecraft:Minecraft server offline
```

## Plugins
Any server can run behind the proxy, simply fill out the template for a package in the "plugins/" directory:

```
class Server():
    def __init__(self,
            # Any other parameters, will come from --plugin_argument params
            working_directory: str = None):

        self.working_directory = working_directory

        self.status = Status.stopped

    async def start(self):
        if self.status is not Status.stopped:
            return

        logger.info('Starting server')
        self.status = Status.starting

        # Whatever to run the server, probably an await asyncio.create_subprocess_exec()

        logger.info('Server online')
        self.status = Status.running

    async def stop(self):
        if self.status is not Status.running:
            return

        logger.info('Stopping server')
        self.status = Status.stopping

        # Whatever to stop the server

        logger.info('Server offline')
        self.status = Status.stopped

    def fake_status(self) -> bytes:
        return # Some bytes for when a client tries to connect and the server is not online
```

## Systemd
Example systemd configs are located in systemd/ to accompany the plugins.
