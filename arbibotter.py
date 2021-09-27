from configparser import ConfigParser
from web3 import Web3
from web3.auto import w3

from ratelimit import limits, sleep_and_retry

import json
import numpy as np

import sys

import time
import redis

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

@sleep_and_retry
@limits(150, period=1)
def check_tx(instance, hash):
    instance.eth.get_transaction_receipt(hash)

def wait_for_tx(instance, hash):
    last_tx_confirmed = False
    while(last_tx_confirmed == False):
        try:
            if check_tx(instance, hash) != None:
                last_tx_confirmed = True
        except:
            continue
    return

@sleep_and_retry
@limits(150, period=1)
def send_tx(instance, signed_tx):
    instance.eth.send_raw_transaction(signed_tx.rawTransaction)

def get_num_mints(redis_instance):
    return int(redis_instance.get(0))

def mint_at(personal_address, privatekey, node, buy_price, qty, gwei, panic_point=0, max_price=None):
    if panic_point == 0:        
        max_price = buy_price
    else:
        r0 = redis.StrictRedis(host='localhost', port=6379, password=cfg['PASSWORDS']['redis'], db=0)
        max_price = max_price

    abi = json.loads('[{"inputs":[],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"approved","type":"address"},{"indexed":true,"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"operator","type":"address"},{"indexed":false,"internalType":"bool","name":"approved","type":"bool"}],"name":"ApprovalForAll","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"uint256","name":"tokenId","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"price","type":"uint256"}],"name":"Mint","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Redeem","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":true,"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"Transfer","type":"event"},{"inputs":[],"name":"MAX_BOTS","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"TOTAL_REWARD_POOLS","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"approve","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"bodies","outputs":[{"internalType":"bytes","name":"","type":"bytes"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"burn","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"eyes","outputs":[{"internalType":"bytes","name":"","type":"bytes"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"getApproved","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"headgears","outputs":[{"internalType":"bytes","name":"","type":"bytes"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"heads","outputs":[{"internalType":"bytes","name":"","type":"bytes"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"operator","type":"address"}],"name":"isApprovedForAll","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"mint","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[],"name":"mintPrice","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"mouths","outputs":[{"internalType":"bytes","name":"","type":"bytes"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"ownerOf","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"uint256","name":"","type":"uint256"}],"name":"palettes","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"redeem","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"redeemable","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"uint256","name":"","type":"uint256"}],"name":"redeemed","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"rewardPools","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"safeTransferFrom","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"},{"internalType":"bytes","name":"_data","type":"bytes"}],"name":"safeTransferFrom","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"seeds","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"operator","type":"address"},{"internalType":"bool","name":"approved","type":"bool"}],"name":"setApprovalForAll","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes4","name":"interfaceId","type":"bytes4"}],"name":"supportsInterface","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"index","type":"uint256"}],"name":"tokenByIndex","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"uint256","name":"index","type":"uint256"}],"name":"tokenOfOwnerByIndex","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"tokenURI","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalRewards","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"transferFrom","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"}]')

    contract_address = Web3.toChecksumAddress("0xc1fcf330b4b4c773fa7e6835f681e8f798e9ebff")
    contract =  node.eth.contract(address=contract_address, abi=abi)

    gas_price = Web3.toWei(gwei, 'gwei')

    start = time.monotonic()
    mint_price = np.float64(Web3.fromWei(contract.functions.mintPrice().call(), 'ether'))
    current_seconds = offchain_secondsSinceAuctionStart(mint_price)

    if panic_point == 0:
        target_seconds = offchain_secondsSinceAuctionStart(buy_price)
    else:
        target_seconds = offchain_secondsSinceAuctionStart(max_price)

    end = time.monotonic()

    time_to_sleep = target_seconds - current_seconds - (end - start) - 60
    if time_to_sleep > 0:
        time.sleep(time_to_sleep)

    if panic_point > 0:
        panicked = False
        while (np.float64(Web3.fromWei(contract.functions.mintPrice().call(), 'ether')) > np.float64(buy_price)) & (panicked == False):            
            n = get_num_mints(r0)            
            if n > panic_point:
                panicked = True
            time.sleep(1)

    current_nonce = node.eth.get_transaction_count(personal_address)
    for nonce in range(current_nonce+1, current_nonce+qty+2):
        tx = {
                'chainId': 42161,
                'from': personal_address, 
                'value': str(Web3.toHex(contract.functions.mintPrice().call())),
                'gasPrice': str(Web3.toHex(Web3.toWei(gas_price, 'gwei'))),
                'nonce': nonce
            }
        signed_tx = w3.eth.account.sign_transaction(contract.functions.mint().buildTransaction(tx), private_key=privatekey)        
        hash = node.toHex(node.keccak(signed_tx.rawTransaction))
        
        send_tx(node, signed_tx)
        wait_for_tx(node, hash)

cfg = ConfigParser()
cfg.read('config.cfg')

privatekey = cfg["IDENTITY"]['private_key']
personal_address = cfg["IDENTITY"]['personal_address']

node = Web3(Web3.WebsocketProvider(cfg['NodeURLs']['arbitrum_wss']))

if len(sys.argv) == 3:
    print(3)
    mint_at(personal_address, privatekey, node, np.float64(sys.argv[1]), int(sys.argv[2]), 3)
elif len(sys.argv) == 5:
    print(5)
    mint_at(personal_address, privatekey, node, np.float64(sys.argv[1]), int(sys.argv[2]), 3, np.float64(sys.argv[3]), np.float64(sys.argv[4]))
else:
    print('arguments must be MINT_PRICE QUANTITY and optionally be followed by PANIC_POINT MAX_PRICE')