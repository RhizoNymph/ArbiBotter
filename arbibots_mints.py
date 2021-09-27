import multiprocessing
from eth_utils.address import to_checksum_address
from web3 import Web3
from configparser import ConfigParser
from ratelimit import sleep_and_retry, limits
from concurrent.futures import ThreadPoolExecutor, as_completed
from multiprocessing import cpu_count

import numpy as np
import asyncio
import json
import websockets
import redis

@sleep_and_retry
@limits(calls=150, period=1)
async def socket_send(websocket, request_data):
    await websocket.send(json.dumps(request_data))
    result = await websocket.recv()

    return json.loads(result)['result']

async def fn(pool, uri):
    async with websockets.connect(uri) as websocket:
        # grab new block filter
        request_data = {"jsonrpc":"2.0","id":"1","method":"eth_newBlockFilter","params":[],"id": 1}
        
        filter_hash = await socket_send(websocket, request_data)
        
        # grab new blocks loop
        while True:
            request_data = {"jsonrpc":"2.0","id":"1","method":"eth_getFilterChanges","params":[filter_hash], "id": 1}
            filter_changes = await socket_send(websocket, request_data)
            
            if len(filter_changes) > 0:                
                for block_hash in filter_changes:
                    request_data = {"jsonrpc":"2.0","id":"1","method":"eth_getBlockByHash","params":[block_hash, True], "id": 1}
                    
                    txs = await socket_send(websocket, request_data)                    

                    pool.map(is_arbibots_mint, txs['transactions'])                

def is_arbibots_mint(tx):
    cfg = ConfigParser()
    cfg.read('config.cfg')
    r0 = redis.StrictRedis(host='localhost', port=6379, password=cfg['PASSWORDS']['redis'], db=0)        
    tries = int(r0.get(1))
    r0.set(1, tries + 1)

    if tx == None:
        return
    
    if (tx['to'] == '0xc1fcf330b4b4c773fa7e6835f681e8f798e9ebff'):
        if ('input' in tx.keys()):
            if (tx['input'].lower()[0:10] == '0x1249c58b'):                
                current = int(r0.get(0))
                if current == 24: 
                    r0.set(0, 0)
                else:
                    r0.set(0, current+1)
    return

def offchain_mintPrice(secondsSinceAuctionStart):    
    if (secondsSinceAuctionStart < 18000):
        return Web3.fromWei(2 * 10**19 - (2 * 10**19 * secondsSinceAuctionStart) / 18305, 'ether')
    elif (secondsSinceAuctionStart < 21492):
        return Web3.fromWei(2 * 10**18 - (2 * 10**18 * secondsSinceAuctionStart) / 21600, 'ether')
    else:
        return Web3.fromWei(10**16, 'ether')

def offchain_secondsSinceAuctionStart(buy_price):
    if np.float64(buy_price) > offchain_mintPrice(18000):
        return 18305 - (3661 * Web3.toWei(buy_price, 'ether'))/4000000000000000000
    elif np.float64(buy_price) > offchain_mintPrice(21492):
        return 21600 - (27 * Web3.toWei(buy_price, 'ether'))/2500000000000000
    else:
        return 21492

def tokenid_exists(contract, tokenid):
	try:
		contract.functions.ownerOf(tokenid).call()
		return tokenid
	except:
		return 0

async def highest_tokenid(contract, maxId):
	with ThreadPoolExecutor(max_workers=cpu_count()-2) as pool:
		successful_tokenids = []
		futures = []
		for tokenid in range(maxId, -1, -1):
			futures.append(pool.submit(tokenid_exists, contract, tokenid))	
		for future in as_completed(futures):
			if future.result() > 0:
				successful_tokenids.append(future.result())

	return max(successful_tokenids)

def mints_this_auction(uri):
    node = Web3(Web3.WebsocketProvider(uri))
    abi = json.loads('[{"inputs":[],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"approved","type":"address"},{"indexed":true,"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"operator","type":"address"},{"indexed":false,"internalType":"bool","name":"approved","type":"bool"}],"name":"ApprovalForAll","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"uint256","name":"tokenId","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"price","type":"uint256"}],"name":"Mint","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Redeem","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":true,"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"Transfer","type":"event"},{"inputs":[],"name":"MAX_BOTS","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"TOTAL_REWARD_POOLS","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"approve","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"bodies","outputs":[{"internalType":"bytes","name":"","type":"bytes"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"burn","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"eyes","outputs":[{"internalType":"bytes","name":"","type":"bytes"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"getApproved","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"headgears","outputs":[{"internalType":"bytes","name":"","type":"bytes"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"heads","outputs":[{"internalType":"bytes","name":"","type":"bytes"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"operator","type":"address"}],"name":"isApprovedForAll","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"mint","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[],"name":"mintPrice","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"mouths","outputs":[{"internalType":"bytes","name":"","type":"bytes"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"ownerOf","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"uint256","name":"","type":"uint256"}],"name":"palettes","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"redeem","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"redeemable","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"uint256","name":"","type":"uint256"}],"name":"redeemed","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"rewardPools","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"safeTransferFrom","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"},{"internalType":"bytes","name":"_data","type":"bytes"}],"name":"safeTransferFrom","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"seeds","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"operator","type":"address"},{"internalType":"bool","name":"approved","type":"bool"}],"name":"setApprovalForAll","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes4","name":"interfaceId","type":"bytes4"}],"name":"supportsInterface","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"index","type":"uint256"}],"name":"tokenByIndex","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"uint256","name":"index","type":"uint256"}],"name":"tokenOfOwnerByIndex","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"tokenURI","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalRewards","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"transferFrom","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"}]')
    contract_address = Web3.toChecksumAddress("0xc1fcf330b4b4c773fa7e6835f681e8f798e9ebff")
    contract =  node.eth.contract(address=contract_address, abi=abi)

    highest = asyncio.get_event_loop().run_until_complete(highest_tokenid(contract, 2000))

    return (highest + 1) % 25

if __name__ == "__main__":
    cfg = ConfigParser()
    cfg.read('config.cfg')

    pool = ThreadPoolExecutor(max_workers=cpu_count()-2)

    r0 = redis.StrictRedis(host='localhost', port=6379, password=cfg['PASSWORDS']['redis'], db=0)

    r0.set(0, 0)
    r0.set(1, 0)

    print('Getting current mints in auction...')
    current_mints = mints_this_auction(cfg['NodeURLs']['arbitrum_wss'])
    print('{} mints found...'.format(current_mints))
    r0.set(0, current_mints)

    print('Running mint watcher...')
    asyncio.get_event_loop().run_until_complete(fn(pool, cfg['NodeURLs']['arbitrum_wss']))