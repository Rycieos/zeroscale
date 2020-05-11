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
    add_common_options(parser)

    parser.add_argument(
        "container_id",
        type=str,
        help="ID or name of the Docker container to control. Must already exist. Will also try to connect to this container as the server to proxy unless server_host is set.",
    )
    parser.add_argument(
        "--disable_exit_stop",
        action="store_true",
        help="Disable stopping the controlled container on exit.",
    )

    args = parser.parse_args(*argv)

    logging.basicConfig(level=args.log_level)

    wrapped_server = None
    if args.plugin:
        try:
            plugin = import_module("." + args.plugin, package="zeroscale.plugins")
        except (ModuleNotFoundError, ImportError):
            logger.exception("Could not load plugin '%s'", args.plugin)
            return 1

        wrapped_server = plugin.Server(
            *args.plugin_argument
        )

    server = DockerProxyServer(args.container_id, wrapped_server)

    if args.disable_exit_stop:
        async def no_stop():
            pass
        server.stop = no_stop

    ZeroScale(
        server=server,
        listen_port=args.listen_port,
        server_host=args.server_host or args.container_id,
        server_port=args.server_port or args.listen_port,
        method_pause=not args.method_stop,
        server_idle_shutdown=args.idle_shutdown,
        server_shutdown_timeout=args.shutdown_timeout,
        ignore_bad_clients=args.ignore_bad_clients
    ).start_server()

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
