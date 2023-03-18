from datetime import datetime, time, timedelta
from web3 import Web3
import telegram
import requests, json
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()


TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
channel_id = '@ethgaswatch'


alchemy = os.getenv('ALCHEMY_API_KEY')
w3 = Web3(Web3.HTTPProvider(alchemy))

async def send_message_async(channel_id, tweet_text):
    bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
    await bot.send_message(chat_id=channel_id, text=tweet_text)

#Send status update every 4h
async def send_four_hourly_messages():
    while True:
        utc_time = datetime.utcnow()
        formatted_time = utc_time.strftime('%m-%d-%Y %I:%M %p')

        market_cap = json.loads(requests.get('https://api.coingecko.com/api/v3/coins/ethereum').text)['market_data']['market_cap']['usd']

        btc_dominance = json.loads(requests.get('https://api.coingecko.com/api/v3/global').text)['data']['market_cap_percentage']['btc']
        eth_dominance = json.loads(requests.get('https://api.coingecko.com/api/v3/global').text)['data']['market_cap_percentage']['eth']
        diff = btc_dominance - eth_dominance

        response = requests.get('https://api.coingecko.com/api/v3/coins/ethereum?market_data=true')
        data=response.json()
        eth_usd_price = data['market_data']['current_price']['usd']
        eth_usd_1h_change = data['market_data']['price_change_percentage_1h_in_currency']['usd']


        current_gas_price_gwei = w3.eth.gas_price / 10**9
        current_gas_price_usd = current_gas_price_gwei * 10**-9 * 21000 * eth_usd_price

        tweet_text = f"{formatted_time} UTC Live from #Ethereum Mainnet\n\n• $ETH price is ${eth_usd_price} ({eth_usd_1h_change:+.2f}% 1h)\n• Market Cap: ${market_cap:,}\n• Dominance: {eth_dominance:.2f}% | {diff:.2f} behind $BTC\n• Gas price: {current_gas_price_gwei:.2f} GWEI = ${current_gas_price_usd:.2f}\n\n#DeFi #NFT #Crypto"

        print(tweet_text)

        await send_message_async(channel_id, tweet_text)
        await asyncio.sleep(14400)


def ordinal(n):
    return str(n) + ('th' if 4 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th'))

async def send_daily_message():
    while True:
        now = datetime.utcnow()
        scheduled_time = time(hour=9, minute=0, second=0, microsecond=0)
        
        now_datetime = datetime.combine(now.date(), now.time())
        next_schedule_datetime = datetime.combine(now.date(), scheduled_time)

        if now.time() > scheduled_time:
            next_schedule_datetime += timedelta(days=1)

        time_diff = next_schedule_datetime - now_datetime
        
        await asyncio.sleep(time_diff.total_seconds())
        
        url = "https://api.alternative.me/fng/?limit=1&format=json"
        response = requests.get(url)
        data = response.json()
        fear_greed_value = data["data"][0]["value"]
        sentiment = data["data"][0]["value_classification"]
        date = datetime.utcfromtimestamp(int(data["data"][0]["timestamp"])).strftime('%B ') + ordinal(int(data["data"][0]["timestamp"][8:10]))
        
        message = f"GM #CryptoTwitter\n\n{date} Crypto Fear and Greed Index stands at {fear_greed_value}/100\n\nSentiment: {sentiment}"
        
        print(message)

        await send_message_async(channel_id, message)



async def main():
    tasks = [
        asyncio.create_task(send_four_hourly_messages()),
        asyncio.create_task(send_daily_message()),
    ]
    await asyncio.gather(*tasks)

asyncio.run(main())
