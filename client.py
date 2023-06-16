import asyncio
import random
from datetime import datetime
import re


class Client:

    def __init__(self, logfile_name, host='127.0.0.1', port=8080):
        self.logfile_name = logfile_name
        self.host = host
        self.port = port

        self.running = False
        self.request_number = 0

        self.logs = list()

    async def read(self, reader):
        while self.running:
            data = (await reader.read(256)).decode()[:-1]
            for resp_data in data.split("\n"):
                if resp_data == '':
                    continue
                if "keepalive" in resp_data:
                    self.logs.append({"req_data": "",
                                      "req_time": "",
                                      "resp_data": resp_data,
                                      "resp_time": datetime.now().time()})
                else:
                    resp_num = re.findall(r"\d+", resp_data)[1]
                    for log in self.logs:
                        if log['req_data'] == "":
                            continue
                        req_num = log["req_data"].split(' ')[0]
                        if req_num == resp_num:
                            log["resp_data"] = resp_data
                            log["resp_time"] = datetime.now().time()
                            break

            await asyncio.sleep(0.05)

    async def write(self, writer):
        while self.running:
            data = f"{self.request_number} PING\n"
            self.logs.append({"req_data": data[:-1],
                              "req_time": datetime.now().time()})
            self.request_number += 1

            writer.write(data.encode())
            await writer.drain()
            await asyncio.sleep(random.randint(300, 3000) / 1000)

        writer.close()
        await writer.wait_closed()

    async def run(self):
        reader, writer = await asyncio.open_connection(self.host, self.port)
        self.running = True
        asyncio.create_task(self.read(reader))
        asyncio.create_task(self.write(writer))

    def stop(self):
        self.running = False
        with open(self.logfile_name, "w+") as f:
            now_date = datetime.now().date()
            for log in self.logs:
                if "resp_data" not in log:
                    log_str = f"{now_date}; {log['req_time']}; {log['req_data']}; (таймаут)\n"
                else:
                    log_str = f"{now_date}; {log['req_time']}; {log['req_data']}; {log['resp_time']}; {log['resp_data']}\n"
                f.write(log_str)

