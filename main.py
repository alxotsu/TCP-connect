import asyncio
from server import Server
from client import Client


async def main():
    server = Server("logs/serv.txt")
    client1 = Client("logs/cli-1.txt")
    client2 = Client("logs/cli-2.txt")

    async def start():
        asyncio.create_task(server.run())
        await client1.run()
        await client2.run()

    async def stop():
        client1.stop()
        client2.stop()
        await server.stop()

    asyncio.create_task(start())
    await asyncio.sleep(300)
    await stop()


asyncio.get_event_loop().run_until_complete(main())
