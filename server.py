import asyncio
import random
from datetime import datetime


class Server:
    def __init__(self, logfile_name, host='127.0.0.1', port=8080):
        self.logfile_name = logfile_name
        self.host = host
        self.port = port

        self.server = None
        self.writers = list()
        self.response_number = 0

        self.logs = list()

    async def send_keepalive(self):
        while self.server.is_serving:
            await asyncio.sleep(5)
            for writer in self.writers:
                data = f"{self.response_number} keepalive\n"
                self.response_number += 1

                self.logs.append({
                    "req_time": "",
                    "req_data": "",
                    "resp_time": datetime.now().time(),
                    "resp_data": data[:-1]
                })

                writer.write(data.encode())
                await writer.drain()

    async def handle_connection(self, reader, writer):
        self.writers.append(writer)
        cli_number = len(self.writers)

        while self.server.is_serving:
            data = (await reader.read(256)).decode()
            req_time = datetime.now().time()

            for req_data in data.split('\n'):
                if req_data == '':
                    continue

                response = None
                if random.random() > 0.1:
                    await asyncio.sleep(random.randint(100, 1000) / 1000)
                    response = f"[{self.response_number}/{req_data.split(' ')[0]}] PONG {cli_number}\n"
                    self.response_number += 1
                    writer.write(response.encode())
                    await writer.drain()
                    response = response[:-1]

                self.logs.append({
                    "req_time": req_time,
                    "req_data": req_data,
                    "resp_time": datetime.now().time(),
                    "resp_data": response
                })

        self.writers.remove(writer)
        writer.close()
        await writer.wait_closed()

    async def run(self):
        self.server = await asyncio.start_server(
            self.handle_connection,
            self.host,
            self.port
        )
        asyncio.create_task(self.send_keepalive())
        async with self.server:
            await self.server.serve_forever()

    async def stop(self):
        self.server.close()
        await self.server.wait_closed()
        with open(self.logfile_name, "w+") as f:
            now_date = datetime.now().date()
            for log in self.logs:
                if log["resp_data"] is None:
                    log_str = f"{now_date}; {log['req_time']}; {log['req_data']}; (проигнорировано)\n"
                else:
                    log_str = f"{now_date}; {log['req_time']}; {log['req_data']}; {log['resp_time']}; {log['resp_data']}\n"
                f.write(log_str)
