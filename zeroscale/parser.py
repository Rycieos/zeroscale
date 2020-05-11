import logging

logger = logging.getLogger(__name__)


def add_common_options(parser):
    parser.add_argument(
        "--listen_port",
        "-p",
        type=int,
        default=8080,
        help="Port for the proxy server, where clients will connect. Defaults to 8080",
    )
    parser.add_argument(
        "--server_host",
        "-H",
        type=str,
        help="Hostname that the real server will be listening on. Defaults to localhost.",
    )
    parser.add_argument(
        "--server_port",
        "-P",
        type=int,
        help="Port that the real server will be listening on. Defaults to the value of listen_port",
    )
    parser.add_argument(
        "--plugin",
        type=str,
        default="generic",
        help="Package name of the server plugin. Must be in plugins dir. Defaults to the generic provider.",
    )
    parser.add_argument(
        "--method_stop",
        "-m",
        action="store_true",
        help="Instead of pausing the process, stop it completely. This isn't recommended since extra startup time will be needed.",
    )
    parser.add_argument(
        "--idle_shutdown",
        "-t",
        type=int,
        default=15,
        help="Time in seconds after last client disconects to shutdown the server. Default 15.",
    )
    parser.add_argument(
        "--shutdown_timeout",
        "-s",
        type=int,
        default=15,
        help="Time in seconds after proxy server gets SIGINT to kill the server. Default 15.",
    )
    parser.add_argument(
        "--plugin_argument",
        "-a",
        type=str,
        action="append",
        default=[],
        help="Arguments to pass to the Server() constructor in the plugin. Can be called multiple times.",
    )
    parser.add_argument(
        "--ignore_bad_clients",
        "-b",
        action="store_true",
        help="""Disable checking for a bad client connection.
                This would prevent port scanners from starting servers, but if
                your real clients are failing the check, you can disable it.
                This is implemented by each server plugin. The default plugin
                has no check.""",
    )
    parser.add_argument(
        "--info",
        "-i",
        action="store_const",
        dest="log_level",
        const=logging.INFO,
        help="Enable info logging.",
    )
    parser.add_argument(
        "--debug",
        "-d",
        action="store_const",
        dest="log_level",
        const=logging.DEBUG,
        default=logging.WARNING,
        help="Enable debug logging. Default is WARNING",
    )

    return parser
