import logging
import sys
from zeroscale.zeroscale import ZeroScale
from zeroscale.plugins.minecraft import Minecraft

def main(args=None):
    if args is None:
        args = sys.argv[1:]

    logging.basicConfig(level=logging.DEBUG)

    ZeroScale(listen_port=25566, server_port=25575, server=Minecraft(jar_name='minecraft_server.1.14.3.jar')).start_server()

if __name__ == "__main__":
    main()
