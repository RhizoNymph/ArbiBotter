from web3 import Web3
from configparser import ConfigParser
from ratelimit import sleep_and_retry, limits

import asyncio
import json
import websockets
import redis

@sleep_and_retry
@limits(calls=150, period=1)
async def newBlockFilter(uri):
    async with websockets.connect(uri) as websocket:
        request_data = {"jsonrpc":"2.0","id":"1","method":"eth_newBlockFilter","params":[],"id": 1}
        await websocket.send(json.dumps(request_data))

        result = await websocket.recv()
        return json.loads(result)['result']

@sleep_and_retry
@limits(calls=150, period=1)
async def getFilterChanges(uri, filter_hash):
    async with websockets.connect(uri) as websocket:
        request_data = {"jsonrpc":"2.0","id":"1","method":"eth_getFilterChanges","params":[filter_hash], "id": 1}
        await websocket.send(json.dumps(request_data))

        result = await websocket.recv()
        return json.loads(result)['result']

@sleep_and_retry
@limits(calls=150, period=1) 
async def getTransactionByHash(uri, tx_hash):
    async with websockets.connect(uri) as websocket:
        request_data = {"jsonrpc":"2.0","id":"1","method":"eth_getTransactionByHash","params":[tx_hash], "id": 1}
        await websocket.send(json.dumps(request_data))

        result = await websocket.recv()
        return json.loads(result)['result']    

@sleep_and_retry
@limits(calls=150, period=1)
async def getBlockTransactionsByHash(uri, block_hash):
    async with websockets.connect(uri) as websocket:
        request_data = {"jsonrpc":"2.0","id":"1","method":"eth_getBlockByHash","params":[block_hash, True], "id": 1}
        await websocket.send(json.dumps(request_data))

        result = await websocket.recv()
        return json.loads(result)['result']['transactions']

def is_arbibots_mint(tx):
    if tx == None:
        return False
    if (tx['to'] == '0xc1fCf330b4B4C773fA7e6835f681E8F798E9eBff') & ('data' in tx.keys()):
        if (tx['data'][0:10] == '0x1249c58b'):
            return True

def mints_in_block(txs):
    bools = [is_arbibots_mint(tx) for tx in txs]

    return bools.count(True)

def mints_in_blocks(blocks):
    counts = [mints_in_block(txs) for txs in blocks]

    return sum(counts)

if __name__ == "__main__":
    cfg = ConfigParser()
    cfg.read('config.cfg')

    filter_hash = asyncio.get_event_loop().run_until_complete(newBlockFilter(cfg['NodeURLs']['arbitrum_wss']))
    mempool = asyncio.get_event_loop().run_until_complete(getFilterChanges(cfg['NodeURLs']['arbitrum_wss'], filter_hash))
    
    contract_address = "0xc1fCf330b4B4C773fA7e6835f681E8F798E9eBff"

    r0 = redis.StrictRedis(host='localhost', port=6379, password=cfg['PASSWORDS']['redis'], db=0)
    
    while True:
        try:
            filter_changes = asyncio.get_event_loop().run_until_complete(getFilterChanges(cfg['NodeURLs']['arbitrum_wss'], filter_hash))
        except :
            filter_hash = asyncio.get_event_loop().run_until_complete(newBlockFilter(cfg['NodeURLs']['arbitrum_wss']))
            continue
                
        if len(filter_changes) > 0:
            for change in filter_changes:
                blocks = [asyncio.get_event_loop().run_until_complete(getBlockTransactionsByHash(cfg['NodeURLs']['arbitrum_wss'], tx)) for tx in filter_changes]

                inc = mints_in_blocks(blocks)
                
                if inc > 0:
                    current = int(r0.get(0))
                    if current >= 25:
                        r0.set(0, 0)
                    r0.set(0, current + inc)