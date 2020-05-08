#!/usr/bin/env python3
# Copied from the example in PEP-492

import asyncio
import sys

async def handle_connection(reader, writer):
    while True:
        data = await reader.read(8192)

        if not data:
            break

        writer.write(data)

def main(args):
    port = 8000
    if len(args) > 1:
        port = int(args[1])

    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.start_server(handle_connection, port=port))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()

if __name__ == "__main__":
    sys.exit(main(sys.argv))
