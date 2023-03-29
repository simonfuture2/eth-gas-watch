from datetime import datetime
import time
from pytz import timezone
from web3 import Web3
import requests
from dotenv import load_dotenv
import os
import asyncio
import aiohttp

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
channel_id = '@ethgaswatch'

alchemy = os.getenv('ALCHEMY_API_KEY')
etherscan = os.getenv("ETHERSCAN_API_KEY")

w3 = Web3(Web3.HTTPProvider(alchemy))
pt = timezone('US/Pacific')


async def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text
    }
    async with aiohttp.ClientSession() as session:
        await session.post(url, data=data)


async def fetch_eth_data():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd&include_market_cap=true&include_24hr_change=true"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
    return data

async def send_four_hourly_messages():
    while True:
        now = datetime.now()
        utc_time = now.strftime('%m-%d-%Y %I:%M %p')

        eth_data = await fetch_eth_data()

        market_cap = eth_data['ethereum']['usd_market_cap']
        eth_usd_price = eth_data['ethereum']['usd']

        current_gas_price_gwei = w3.eth.gas_price / 10**9
        current_gas_price_usd = current_gas_price_gwei * 10**-9 * 21000 * eth_usd_price

        tweet_text = f"{utc_time} UTC Live from #Ethereum Mainnet\n\n$ETH price is ${eth_usd_price}\nMarket Cap: ${market_cap:,}\nGas price: {current_gas_price_gwei:.2f} GWEI = ${current_gas_price_usd:.2f}\n\n#DeFi #NFT #Crypto"

        print(tweet_text)

        await send_telegram_message(channel_id, tweet_text)

        await asyncio.sleep(14400)



async def fear_greed():
    async def job():
        url = "https://api.alternative.me/fng/?limit=1&format=json"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.json()

        fear_greed_value = data["data"][0]["value"]
        sentiment = data["data"][0]["value_classification"]
        date = datetime.utcfromtimestamp(int(data["data"][0]["timestamp"])).strftime('%B %d')

        message = f"GM #CryptoTwitter\n\n{date} Crypto Fear and Greed Index stands at {fear_greed_value}/100\n\nSentiment: {sentiment}"
        
        print(message)

        await send_telegram_message(channel_id, message)

    while True:
        now = datetime.now().strftime('%H:%M')
        if now == '08:00':
            await job()
            # wait until tomorrow
            await asyncio.sleep(86400 - time.time() % 86400)
        else:
            # wait 1 minute before checking again
            await asyncio.sleep(60)


async def eth_supply():
    async def job():
        now = datetime.utcnow().replace(tzinfo=timezone('UTC')).astimezone(pt)

        url = f"https://api.etherscan.io/api?module=stats&action=ethsupply2&apikey={etherscan}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                result = await resp.json()["result"]

        eth_supply = int(result["EthSupply"]) / 10**18
        staking_rewards = int(result["Eth2Staking"]) / 10**18
        burnt_fees = int(result["BurntFees"]) / 10**18
        us_time = now.strftime('%I:%M %p %Z')

        supply = f"{us_time} $ETH status update\n\nCurrent Ethereum supply: {eth_supply:,.2f} ETH\nETH2 staking rewards: {staking_rewards:,.2f} ETH\nTotal ETH burnt since PoS transition: {burnt_fees:,.2f} ETH"
        
        print(supply)

        await send_telegram_message(channel_id, supply)

    while True:
        now = datetime.now().strftime('%H:%M')
        if now == '09:00':
            await job()
            # wait until tomorrow
            await asyncio.sleep(86400 - time.time() % 86400)
        else:
            # wait 1 minute before checking again
            await asyncio.sleep(60)


async def main():
    await asyncio.gather(send_four_hourly_messages(), fear_greed(), eth_supply())


asyncio.run(main())

