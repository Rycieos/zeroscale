#!/usr/bin/env python

import argparse
import asyncio
import logging
import sys
from importlib import import_module

from .docker import DockerProxyServer
from .parser import add_common_options
from .zeroscale import ZeroScale

logger = logging.getLogger(__name__)


def main(*argv):
    """Load arguments and start a Zeroscale proxy server"""

    parser = argparse.ArgumentParser(description="Scale a container to zero.")

    parser.add_argument(
        "listen_port",
        type=int,
        help="Port for the proxy server, where clients will connect.",
    )
    parser.add_argument(
        "server_port",
        type=int,
        help="Port that the real server will be listening on.",
    )
    parser.add_argument(
        "container_id",
        type=str,
        help="ID or name of the Docker container to control. Must already exist.",
    )
    parser.add_argument(
        "--server_plugin",
        "-p",
        type=str,
        help="Package name of the server plugin. Must be in plugins dir. Only used for client validation and client fake status.",
    )
    parser.add_argument(
        "--disable_exit_stop",
        action="store_true",
        help="Disable stopping the controlled container on exit.",
    )

    add_common_options(parser)

    args = parser.parse_args(*argv)

    logging.basicConfig(level=args.log_level)

    server = None
    if args.server_plugin:
        try:
            plugin = import_module("." + args.server_plugin, package="zeroscale.plugins")
        except (ModuleNotFoundError, ImportError):
            logger.exception("Could not load plugin '%s'", args.server_plugin)
            return 1

        server = plugin.Server(
            *args.plugin_argument
        )

    server = DockerProxyServer(args.container_id, server)

    if args.disable_exit_stop:
        async def no_stop():
            pass
        server.stop = no_stop

    ZeroScale(
        server=server,
        listen_port=args.listen_port,
        server_port=args.server_port,
        server_host=args.server_host,
        method_pause=not args.method_stop,
        server_idle_shutdown=args.idle_shutdown,
        server_shutdown_timeout=args.shutdown_timeout,
        ignore_bad_clients=args.ignore_bad_clients
    ).start_server()

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
