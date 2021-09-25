from web3 import Web3
from configparser import ConfigParser

import asyncio
import json
import websockets
import redis

async def newPendingTransactionFilter(uri):
    async with websockets.connect(uri) as websocket:
        request_data = {"jsonrpc":"2.0","id":"1","method":"eth_newPendingTransactionFilter","params":[],"id": 1}
        await websocket.send(json.dumps(request_data))

        result = await websocket.recv()
        return json.loads(result)['result']

async def getFilterChanges(uri, filter_hash):
    async with websockets.connect(uri) as websocket:
        request_data = {"jsonrpc":"2.0","id":"1","method":"eth_getFilterChanges","params":[filter_hash], "id": 1}
        await websocket.send(json.dumps(request_data))

        result = await websocket.recv()
        return json.loads(result)['result']
    
async def getTransactionByHash(uri, tx_hash):
    async with websockets.connect(uri) as websocket:
        request_data = {"jsonrpc":"2.0","id":"1","method":"eth_getTransactionByHash","params":[tx_hash], "id": 1}
        await websocket.send(json.dumps(request_data))

        result = await websocket.recv()
        return json.loads(result)['result']    

if __name__ == "__main__":
    cfg = ConfigParser().read('config.cfg')

    filter_hash = asyncio.get_event_loop().run_until_complete(newPendingTransactionFilter(cfg['NodeURLs']['arbitrum_wss']))
    mempool = asyncio.get_event_loop().run_until_complete(getFilterChanges(cfg['NodeURLs']['arbitrum_wss'], filter_hash))
    
    contract_address = "0xc1fCf330b4B4C773fA7e6835f681E8F798E9eBff"

    r0 = redis.StrictRedis(host='localhost', port=6379, password=cfg['PASSWORDS']['redis'], db=0)

    id = 0
    while True:
        mempool_changes = asyncio.get_event_loop().run_until_complete(getFilterChanges(cfg['NodeURLs']['arbitrum_wss'], filter_hash))
        
        if len(mempool_changes) > 0:
            txs = [asyncio.get_event_loop().run_until_complete(getTransactionByHash(cfg['NodeURLs']['arbitrum_wss'], tx)) for tx in mempool_changes]
            
            for tx in txs:
                if tx == None:
                    continue
                if (tx['to'] == contract_address) & (tx['data'][0:10] == '0x1249c58b'):
                    r0.set(id, Web3.toInt(hexstr=tx['gasPrice']))
                    id += 1
