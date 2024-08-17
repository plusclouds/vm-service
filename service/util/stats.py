from multiprocessing import Process
import asyncio
import websockets
import psutil
import time

async def websocket_handler(websocket, path):
    try:
        while True:
            cpu_percentages = psutil.cpu_percent(interval=1, percpu=True)
            memory = psutil.virtual_memory()[2]

            io_read = psutil.disk_io_counters()[3]
            io_write = psutil.disk_io_counters()[4]
            time.sleep(1)
            io_read = (psutil.disk_io_counters()[3] - io_read)/1048576
            io_write = (psutil.disk_io_counters()[4] - io_write )/1048576
            

            await websocket.send(f'{{"cpu" : {cpu_percentages}, "ram" : {memory}, "io" : [{io_read:.2f}, {io_write:.2f}] }}')
            
            await asyncio.sleep(1)
    except websockets.ConnectionClosed:
        pass

def init_websocket():
    start_websocket = websockets.serve(websocket_handler, "0.0.0.0", 5050)
    
    asyncio.get_event_loop().run_until_complete(start_websocket)
    asyncio.get_event_loop().run_forever()

def init_stats_process():
    proc = Process(target=init_websocket)
    proc.start()
