import asyncio
import requests
import base58
from pprint import pprint
from cecdsa import tron_sign
from datetime import datetime
import httpx
import orjson

client = httpx.AsyncClient()

ADDRESS = "TXJdFrZbfL1fZcwkAs7HtgGHNdRjYnviwV"
PRIV_KEY = b'ab4a34b671936ef061602752afe26fd13a31ce75d47d0c02401ae3fdcbca968a'
# ADDRESS = "TJvckKsqKq5LnrLSk25HWP7tbcwwdYvAzb"
# PRIV_KEY = b"6844e9005f4e907217e29befea21330c08af0150dc413ca15ab665560aa71523"

# CONTRACT = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"  # USDT
# CONTRACT = "TF17BgPaZYbz8oxbjhriubPDsA7ArKoLX3"
CONTRACT = "TXYZopYRdj2D9XRtbG411XZZ3kM5VkAeBf"

# API_URL_BASE = 'https://api.trongrid.io/'
# API_URL_BASE = 'https://api.shasta.trongrid.io/'
# API_URL_BASE = 'https://api.nileex.io/'
API_URL_BASE = 'http://5.45.75.175:8090/'

# 70a08231: balanceOf(address)
METHOD_BALANCE_OF = 'balanceOf(address)'

# a9059cbb: transfer(address,uint256)
METHOD_TRANSFER = 'transfer(address,uint256)'


DEFAULT_FEE_LIMIT = 1000000000  # 1 TRX

async def post(url, body) -> dict:
    response = await client.post(url, json=body)
    print("response:", response)
    json: dict = orjson.loads(response.content)

    return json

def address_to_parameter(addr):
    return "0" * 24 + base58.b58decode_check(addr)[1:].hex()


def amount_to_parameter(amount):
    return '%064x' % amount


def get_balance(address=ADDRESS):
    url = API_URL_BASE + 'wallet/triggerconstantcontract'
    payload = {
        'owner_address': base58.b58decode_check(ADDRESS).hex(),
        'contract_address': base58.b58decode_check(CONTRACT).hex(),
        'function_selector': METHOD_BALANCE_OF,
        'parameter': address_to_parameter(address),
    }
    resp = requests.post(url, json=payload)
    data = resp.json()

    if data['result'].get('result', None):
        print(data['constant_result'])
        val = data['constant_result'][0]
        print('balance =', int(val, 16))
    else:
        print('error:', bytes.fromhex(data['result']['message']).decode())


async def get_trc20_transaction(to, amount, memo=''):
    url = API_URL_BASE + 'wallet/triggersmartcontract'
    payload = {
        'owner_address': base58.b58decode_check(ADDRESS).hex(),
        'contract_address': base58.b58decode_check(CONTRACT).hex(),
        'function_selector': METHOD_TRANSFER,
        'parameter': address_to_parameter(to) + amount_to_parameter(amount),
        "fee_limit": DEFAULT_FEE_LIMIT,
        # 'extra_data': base64.b64encode(memo.encode()).decode(),  # TODO: not supported yet
    }

    # resp =
    data = await post(url, payload)

    if data['result'].get('result', None):
        transaction = data['transaction']
        return transaction

    else:
        print('error:', bytes.fromhex(data['result']['message']).decode())
        raise RuntimeError


def sign_transaction(transaction, private_key=PRIV_KEY):
    sign = tron_sign(transaction["txID"], private_key)
    transaction["signature"] = [sign]
    # url = API_URL_BASE + 'wallet/addtransactionsign'
    # payload = {'transaction': transaction, 'privateKey': private_key}
    # resp = requests.post(url, json=payload)

    # data = resp.json()

    # if 'Error' in data:
    #     print('error:', data)
    #     raise RuntimeError
    return transaction


async def broadcast_transaction(transaction):
    url = API_URL_BASE + 'wallet/broadcasttransaction'
    data = await post(url, transaction)

    print("broadcast_transaction:", data)


async def transfer(to, amount, memo=''):
    transaction = await get_trc20_transaction(to, amount, memo)
    print("transaction:", transaction)
    start = datetime.now()
    # print("expiration:", datetime.utcfromtimestamp(transaction["raw_data"]["expiration"]))
    transaction = sign_transaction(transaction)
    print(datetime.now() - start)
    await broadcast_transaction(transaction)


get_balance()

usdj1 = 1 * 1000000

async def main():
    # await transfer('TLiU5eauvCECuHykvG54qjFPFcrUu1RpaR', 1000 * 1000000, 'test from python')
    await asyncio.gather(
        *[transfer('TJSQdBmanjLzvj8zhZgEvtzmsVqDMt3QKH', usdj1 + i * 10000, 'test from python') for i in range(1, 150)]
    )

asyncio.run(main())

# transfer('TJSQdBmanjLzvj8zhZgEvtzmsVqDMt3QKH', usdj1, 'test from python')

# transfer('TJvckKsqKq5LnrLSk25HWP7tbcwwdYvAzb', usdj1, 'test from python')

# transfer('TRCWtzWMyXtCQf34jLMSm6P9fXyGuMMutV', usdj1, 'test from python')
