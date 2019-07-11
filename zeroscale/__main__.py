import argparse
import logging
from importlib import import_module

from zeroscale.zeroscale import ZeroScale

logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Scale a server to zero.")

    parser.add_argument('server_plugin', type=str,
            help="Package name of the server plugin. Must be in plugins dir.")
    parser.add_argument('listen_port', type=int,
            help="Port for the proxy server, where clients will connect.")
    parser.add_argument('server_port', type=int,
            help="Port that the real server will be listening on.")
    parser.add_argument('--idle_shutdown', '-t', type=int, default=15,
            help="Time in seconds after last client disconects to kill the server.")
    parser.add_argument('--plugin_argument', '-a', type=str, action='append', default=[],
            help="Arguments to pass to the Server() constructor in the plugin. Can be called multiple times.")
    parser.add_argument('--info', '-i', action='store_const',
            dest='log_level', const=logging.INFO,
            help="Enable info logging.")
    parser.add_argument('--debug', '-d', action='store_const',
            dest='log_level', const=logging.DEBUG, default=logging.WARNING,
            help="Enable debug logging. Default is WARNING")

    args = parser.parse_args()

    logging.basicConfig(level=args.log_level)

    try:
        plugin = import_module('.' + args.server_plugin, package='zeroscale.plugins')
    except (ModuleNotFoundError, ImportError):
        logger.exception("Could not load plugin '%s'", args.server_plugin)
        return

    ZeroScale(
        server=plugin.Server(*args.plugin_argument),
        listen_port=args.listen_port,
        server_port=args.server_port,
        server_idle_shutdown=args.idle_shutdown
    ).start_server()

if __name__ == "__main__":
    main()
