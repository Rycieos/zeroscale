# zeroscale

[![Build Status](https://img.shields.io/github/workflow/status/Rycieos/zeroscale/build-ghcr-image/main)](https://github.com/Rycieos/zeroscale/actions/workflows/build-ghcr-image.yml)
[![Tests Status](https://img.shields.io/github/workflow/status/Rycieos/zeroscale/tests/main?label=tests)](https://github.com/Rycieos/zeroscale/actions/workflows/tests.yml)
[![Coverage Status](https://codecov.io/gh/Rycieos/zeroscale/branch/main/graph/badge.svg?token=KQZDCZ2D60)](https://codecov.io/gh/Rycieos/zeroscale)
[![Dependencies Status](https://img.shields.io/librariesio/release/pypi/zeroscale)](https://libraries.io/pypi/zeroscale)

[![PyPI Package latest release](https://img.shields.io/pypi/v/zeroscale.svg)
 ![PyPI Wheel](https://img.shields.io/pypi/wheel/zeroscale.svg)
 ![Supported versions](https://img.shields.io/pypi/pyversions/zeroscale.svg)](https://pypi.python.org/pypi/zeroscale)

Scale-to-zero any server

Some servers don't idle well. Either they constantly suck CPU doing nothing
(like Minecraft keeping spawn chunks always loaded), or they do things you
don't want them to while no clients are connected. If you have control over
the program, you could design it to do nothing while no clients are connected,
but if you don't, how can you prevent this waste?

`zeroscale` sits in front of a server and only spins it up when someone tries
to connect to it, proxying the connection. It can pause a server when no
clients are connected, and unpause it on connection, completely transparently
proxying the connection. It also supports shutting down the server when no
clients are connected, and while starting it up, send a message to the client
telling the user to wait.

## Usage
```
usage: zeroscale [-h] [--listen_port LISTEN_PORT] [--server_host SERVER_HOST]
                 [--server_port SERVER_PORT] [--plugin PLUGIN] [--method_stop]
                 [--idle_shutdown IDLE_SHUTDOWN]
                 [--shutdown_timeout SHUTDOWN_TIMEOUT]
                 [--plugin_argument PLUGIN_ARGUMENT] [--ignore_bad_clients]
                 [--info] [--debug] [--working_directory WORKING_DIRECTORY]
                 [--pause_signal PAUSE_SIGNAL]
                 [--unpause_signal UNPAUSE_SIGNAL] [--stop_signal STOP_SIGNAL]

Scale a server to zero.

optional arguments:
  -h, --help            show this help message and exit
  --listen_port LISTEN_PORT, -p LISTEN_PORT
                        Port for the proxy server, where clients will connect.
                        Defaults to 8080
  --server_host SERVER_HOST, -H SERVER_HOST
                        Hostname that the real server will be listening on.
                        Defaults to localhost.
  --server_port SERVER_PORT, -P SERVER_PORT
                        Port that the real server will be listening on.
                        Defaults to the value of listen_port
  --plugin PLUGIN       Package name of the server plugin. Must be in plugins
                        dir. Defaults to the generic provider.
  --method_stop, -m     Instead of pausing the process, stop it completely.
                        This isn't recommended since extra startup time will
                        be needed.
  --idle_shutdown IDLE_SHUTDOWN, -t IDLE_SHUTDOWN
                        Time in seconds after last client disconects to
                        shutdown the server. Default 15.
  --shutdown_timeout SHUTDOWN_TIMEOUT, -s SHUTDOWN_TIMEOUT
                        Time in seconds after proxy server gets SIGINT to kill
                        the server. Default 15.
  --plugin_argument PLUGIN_ARGUMENT, -a PLUGIN_ARGUMENT
                        Arguments to pass to the Server() constructor in the
                        plugin. Can be called multiple times.
  --ignore_bad_clients, -b
                        Disable checking for a bad client connection. This
                        would prevent port scanners from starting servers, but
                        if your real clients are failing the check, you can
                        disable it. This is implemented by each server plugin.
                        The default plugin has no check.
  --info, -i            Enable info logging.
  --debug, -d           Enable debug logging. Default is WARNING
  --working_directory WORKING_DIRECTORY, -w WORKING_DIRECTORY
                        Directory to start the server process.
  --pause_signal PAUSE_SIGNAL
                        Signal to send to the server process to pause it. In
                        int form. Default 20 (SIGTSTP)
  --unpause_signal UNPAUSE_SIGNAL
                        Signal to send to the server process to unpause it. In
                        int form. Default 18 (SIGCONT)
  --stop_signal STOP_SIGNAL
                        Signal to send to the server process to stop it. In
                        int form. Default 2 (SIGINT). Note that some plugins
                        will use stdin to stop their process, in which case
                        this flag will be ignored.
```

## Example
```
$ zeroscale --plugin minecraft -p 25565 -P 25575 --debug
INFO:zeroscale.plugins.minecraft:Starting Minecraft server
INFO:zeroscale.plugins.minecraft:Minecraft server online
DEBUG:zeroscale.zeroscale:Scheduling Minecraft server stop
DEBUG:zeroscale.zeroscale:Listening on ('::', 25565, 0, 0)
DEBUG:zeroscale.zeroscale:Listening on ('0.0.0.0', 25565)
DEBUG:zeroscale.zeroscale:No clients online for 15 seconds
INFO:zeroscale.plugins.minecraft:Pausing Minecraft server
...
DEBUG:zeroscale.zeroscale:New connection, server is paused
DEBUG:zeroscale.zeroscale:Invalid client attempted connection  # Detects invalid client
...
DEBUG:zeroscale.zeroscale:New connection, server is paused
INFO:zeroscale.plugins.minecraft:Unpausing Minecraft server
DEBUG:zeroscale.zeroscale:New connection, total clients: 1     # Proxies connection transparently
...
DEBUG:zeroscale.zeroscale:Lost connection, total clients: 0
DEBUG:zeroscale.zeroscale:Scheduling Server server stop
...
DEBUG:zeroscale.zeroscale:No clients online for 15 seconds
INFO:zeroscale.plugins.minecraft:Pausing Minecraft server
```
And an example of the stopping method:
```
$ zeroscale --plugin minecraft -p 25565 -P 25575 -method_stop --debug
DEBUG:zeroscale.zeroscale:Listening on ('::', 25565, 0, 0)
DEBUG:zeroscale.zeroscale:Listening on ('0.0.0.0', 25565)
...
DEBUG:zeroscale.zeroscale:New connection, server is stopped
DEBUG:zeroscale.zeroscale:Invalid client attempted connection  # Detects invalid client
...
DEBUG:zeroscale.zeroscale:New connection, server is stopped
DEBUG:zeroscale.zeroscale:Sending fake response                # Actually shows valid server message in client!
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

## Docker
There is also a Docker version that can control docker containers. Instead of
starting and stopping the process, it starts, stops, and pauses the container.

### Usage
```
usage: docker-zeroscale [-h] [--listen_port LISTEN_PORT]
                        [--server_host SERVER_HOST]
                        [--server_port SERVER_PORT] [--plugin PLUGIN]
                        [--method_stop] [--idle_shutdown IDLE_SHUTDOWN]
                        [--shutdown_timeout SHUTDOWN_TIMEOUT]
                        [--plugin_argument PLUGIN_ARGUMENT]
                        [--ignore_bad_clients] [--info] [--debug]
                        [--disable_exit_stop]
                        container_id

Scale a container to zero.

positional arguments:
  container_id          ID or name of the Docker container to control. Must
                        already exist. Will also try to connect to this
                        container as the server to proxy unless server_host is
                        set.

optional arguments:
  -h, --help            show this help message and exit
  --listen_port LISTEN_PORT, -p LISTEN_PORT
                        Port for the proxy server, where clients will connect.
                        Defaults to 8080
  --server_host SERVER_HOST, -H SERVER_HOST
                        Hostname that the real server will be listening on.
                        Defaults to localhost.
  --server_port SERVER_PORT, -P SERVER_PORT
                        Port that the real server will be listening on.
                        Defaults to the value of listen_port
  --plugin PLUGIN       Package name of the server plugin. Must be in plugins
                        dir. Defaults to the generic provider.
  --method_stop, -m     Instead of pausing the process, stop it completely.
                        This isn't recommended since extra startup time will
                        be needed.
  --idle_shutdown IDLE_SHUTDOWN, -t IDLE_SHUTDOWN
                        Time in seconds after last client disconects to
                        shutdown the server. Default 15.
  --shutdown_timeout SHUTDOWN_TIMEOUT, -s SHUTDOWN_TIMEOUT
                        Time in seconds after proxy server gets SIGINT to kill
                        the server. Default 15.
  --plugin_argument PLUGIN_ARGUMENT, -a PLUGIN_ARGUMENT
                        Arguments to pass to the Server() constructor in the
                        plugin. Can be called multiple times.
  --ignore_bad_clients, -b
                        Disable checking for a bad client connection. This
                        would prevent port scanners from starting servers, but
                        if your real clients are failing the check, you can
                        disable it. This is implemented by each server plugin.
                        The default plugin has no check.
  --info, -i            Enable info logging.
  --debug, -d           Enable debug logging. Default is WARNING
  --disable_exit_stop   Disable stopping the controlled container on exit.
```

### Docker usage
If you want to run `docker-zeroscale` in its own container, there is an image
for that, but you will need to make a few changes.
 * The `docker.sock` must be mounted in the container, so that it can control
   the proxied container.
 * The port that the proxy server will listen on needs to be specified twice:
   once as an argument to Docker to tell it to open the port, and once to the
   proxy server to tell it to listen on that port.
 * Since you don't want the non-proxied port exposed externally, make the
   proxied server listen on a non published port (don't use `-p` when starting
   it), and connect the zeroscale proxy server to the same Docker network.

All together, the run command would look like this:
```
docker run \
  --network my_network \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  -p 25565:25565 \
  rycieos/zeroscale \
  proxied_container_id \
  --listen_port=25565
```
`docker-zeroscale` assumes that the container it is controlling is listening
on the hostname of the container and the same port as the proxy server is
listening on by default.

### Docker compose
Since two containers need to work closely together, it's probably best to use
docker-compose to spin them up.
```yml
version: '3'
services:
  my_server:
    image: my_server
    container_name: my_server
    restart: always
    networks:
      - network
  zeroscale:
    image: rycieos/zeroscale
    restart: always
    ports:
      - 25565:25565
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
    command:
      - my_server
      - --listen_port=25565
    depends_on:
      - my_server
    networks:
      - network
networks:
  network:
    driver: bridge
```

## Plugins

### Minecraft
The original problem server that spawned this project. Should just work,
but if using the pausing method (which is the default), you will need to set
the `max-tick-time` option in the `server.properties` to `-1` to prevent the
server crashing on unpause. While it is possible for a process to detect that
it was paused, Minecraft does not, and it sees a tick as having taken way too
long, and force restarts the server.

If the server needs to be started up (using method stop), it will correctly
show the server as online, but with a message that it is unavailable.

### Terraria
Terraria server. Just works. Shows an error message if the server isn't online.

### Custom plugins
Any server can run behind the proxy, simply override any methods of the
`GenericServer` in your own module in the "plugins/" directory. The only
methods you need to override are `is_valid_connection()` and `fake_status()`.
If you don't override those, you are probably better off just using the
`generic` plugin.

```
from .generic import Server as GenericServer

class Server(GenericServer):
    def __init__(self,
            # Any parameters, will come from --plugin_argument params
        ):
        super().__init__(True)

        self.name = "Plugin name"

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

    async def is_valid_connection(self, client_reader):
        return # If the connection is from a valid client (to stop port scanners)

    def fake_status(self) -> bytes:
        return # Some bytes for when a client tries to connect and the server is not online
```

## Systemd
Example systemd configs are located in systemd/ to accompany the plugins.

## Known issues
* Plugins that use subprocess pipes to read stdin, stdout, or stderr don't work
  on Cygwin, as the OS is seen as posix and thus doesn't ship with the
  ProactorEventLoop, but since the backend OS is Windows, the default event
  loop won't work. This is a bug in the Cygwin Python package.
