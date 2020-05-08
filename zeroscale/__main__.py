#!/usr/bin/env python

import argparse
import logging
import signal
import sys
from importlib import import_module

from .parser import add_common_options
from .zeroscale import ZeroScale

logger = logging.getLogger(__name__)


def parse_signal(signal):
    try:
        return signal.Signals(signal)
    except ValueError:
        logger.error("Signal '%i' is not a valid signal number", signal)
        raise

def main(*argv):
    """Load arguments and start a Zeroscale proxy server"""

    parser = argparse.ArgumentParser(description="Scale a server to zero.")

    parser.add_argument(
        "server_plugin",
        type=str,
        help="Package name of the server plugin. Must be in plugins dir.",
    )
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
        "--working_directory",
        "-w",
        type=str,
        help="Directory to start the server process.",
    )
    parser.add_argument(
        "--pause_signal",
        type=int,
        help="Signal to send to the server process to pause it. In int form. Default 20 (SIGTSTP)",
    )
    parser.add_argument(
        "--unpause_signal",
        type=int,
        help="Signal to send to the server process to unpause it. In int form. Default 18 (SIGCONT)",
    )
    parser.add_argument(
        "--stop_signal",
        type=int,
        help="""Signal to send to the server process to stop it. In int form.
                Default 2 (SIGINT).
                Note that some plugins will use stdin to stop their process, in
                which case this flag will be ignored.""",
    )

    add_common_options(parser)

    args = parser.parse_args(*argv)

    logging.basicConfig(level=args.log_level)

    try:
        plugin = import_module("." + args.server_plugin, package="zeroscale.plugins")
    except (ModuleNotFoundError, ImportError):
        logger.exception("Could not load plugin '%s'", args.server_plugin)
        raise

    server = plugin.Server(*args.plugin_argument)

    if args.working_directory:
        server.set_working_directory(args.working_directory)
    if args.pause_signal:
        server.set_pause_signal(parse_signal(args.pause_signal))
    if args.unpause_signal:
        server.set_unpause_signal(parse_signal(args.unpause_signal))
    if args.stop_signal:
        server.set_stop_signal(parse_signal(args.stop_signal))

    ZeroScale(
        server=server,
        listen_port=args.listen_port,
        server_host=args.server_host,
        server_port=args.server_port,
        method_pause=not args.method_stop,
        server_idle_shutdown=args.idle_shutdown,
        server_shutdown_timeout=args.shutdown_timeout,
        ignore_bad_clients=args.ignore_bad_clients
    ).start_server()

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
