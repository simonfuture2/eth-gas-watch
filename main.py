from datetime import datetime
from web3 import Web3
import telegram
import requests, json
from dotenv import load_dotenv
import os
import asyncio
import time

load_dotenv()


TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
channel_id = '@ethgaswatch'


alchemy = os.getenv('ALCHEMY_API_KEY')
w3 = Web3(Web3.HTTPProvider(alchemy))


while True:

    utc_time = datetime.utcnow()
    formatted_time = utc_time.strftime('%m-%d-%Y %I:%M %p')


    market_cap = json.loads(requests.get('https://api.coingecko.com/api/v3/coins/ethereum').text)['market_data']['market_cap']['usd']


    btc_dominance = json.loads(requests.get('https://api.coingecko.com/api/v3/global').text)['data']['market_cap_percentage']['btc']
    eth_dominance = json.loads(requests.get('https://api.coingecko.com/api/v3/global').text)['data']['market_cap_percentage']['eth']
    diff = btc_dominance - eth_dominance


    # Convert the current gas price to USD using the current ETH/USD price
    response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd&include_24hr_change=true')
    data=response.json()
    eth_usd_price = data['ethereum']['usd']
    eth_usd_24h_change = data['ethereum']['usd_24h_change']


    # Get the current gas price and gwei
    current_gas_price_gwei = w3.eth.gas_price / 10**9
    current_gas_price_usd = current_gas_price_gwei * 10**-9 * 21000 * eth_usd_price


    latest_block = w3.eth.block_number
    one_hour_ago_block = w3.eth.get_block(latest_block - (60 * 60 // 13))

    # get the transaction count of each block in the last hour
    tx_count = 0
    for i in range(one_hour_ago_block.number, latest_block + 1):
        tx_count += w3.eth.get_block_transaction_count(i)
    
    tweet_text = f"{formatted_time} UTC Live from #Ethereum Mainnet\n\n• $ETH price is ${eth_usd_price} ({eth_usd_24h_change:+.2f}% last 24h)\n• Market Cap: ${market_cap:,}\n• Dominance: {eth_dominance:.2f}% | {diff:.2f} behind $BTC\n• Gas price: {current_gas_price_gwei:.2f} GWEI = ${current_gas_price_usd:.2f}\n• Last 1h transactions: {tx_count}\n\n#DeFi #NFT #Crypto"     

    print(tweet_text)


    async def send_message_async(channel_id, tweet_text):
        bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
        await bot.send_message(chat_id=channel_id, text=tweet_text)
    

    asyncio.run(send_message_async(channel_id, tweet_text))
    time.sleep(3600)