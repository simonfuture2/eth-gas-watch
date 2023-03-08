#!/usr/bin/env python
# coding: utf-8

import tweepy
import time
from decimal import Decimal
from datetime import datetime, timezone, timedelta
from web3 import Web3
import requests
import matplotlib.pyplot as plt
from etherscan import Etherscan
from dotenv import load_dotenv
import os


#API KEYS and env variables

load_dotenv()

alchemy = os.getenv('ALCHEMY_API_KEY')

# Get your Etherscan API key from the environment variables
etherscan_api_key = os.getenv('ETHERSCAN_API_KEY')

# Create an instance of the Etherscan client for the mainnet API
etherscan = Etherscan(etherscan_api_key)

# Twitter API keys and access tokens
#consumer_key = os.getenv('consumer-key')
#consumer_secret = os.getenv('consumer-secret')
#access_token = os.getenv('access-token')
#access_token_secret = os.getenv('access-token-secret')

# Authenticate with the Twitter API
#auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
#auth.set_access_token(access_token, access_token_secret)
#api = tweepy.API(auth)


# Connect to the Ethereum network using Alchemy
w3 = Web3(Web3.HTTPProvider(alchemy))

while True:
    # Get the start and end times of the current day in UTC
    today = datetime.now(timezone.utc).date()
    start_time = int(datetime(today.year, today.month, today.day, tzinfo=timezone.utc).timestamp())
    end_time = int((datetime(today.year, today.month, today.day, tzinfo=timezone.utc) + timedelta(days=1)).timestamp())    
    try:
    # Convert the current gas price to USD using the current ETH/USD price
        response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd&include_24hr_change=true')
        data=response.json()
        eth_usd_price = data['ethereum']['usd']
        eth_usd_24h_change = data['ethereum']['usd_24h_change']

        print(f"ETH price: ${eth_usd_price} ({eth_usd_24h_change:+.2f}% last 24h)")
    
        # Get the current gas price
        current_gas_price_gwei = w3.eth.gas_price / 10**9
        current_gas_price_usd = current_gas_price_gwei * 10**-9 * 21000 * eth_usd_price
    
        print(f"Gas price: ${current_gas_price_usd:.2f}")
    except KeyError:
    # Handle the KeyError here
        print("KeyError: Ethereum data not found in response.")


    # Get historical gas prices for the last 24 hours grouped by hour
    average_gas_price_usd = []
    for i in range(24):
        hour_ago = datetime.now(timezone.utc) - timedelta(hours=i+1)
        start_time = int(hour_ago.timestamp())
        end_time = int((hour_ago + timedelta(hours=1)).timestamp())
        gas_prices = w3.eth.get_block('latest', full_transactions=False)['gasUsed']
        total_gas_cost = gas_prices * w3.eth.gas_price
        average_gas_price_usd.append(total_gas_cost / 1e18)

    average_gas_price_usd = sum(average_gas_price_usd) / len(average_gas_price_usd)
    print('Average gas price last 24h: ${:.2f}'.format(average_gas_price_usd))

    average_transaction_cost_usd = []
    for i in range(24):
        hour_ago = datetime.now(timezone.utc) - timedelta(hours=i+1)
        start_time = int(hour_ago.timestamp())
        end_time = int((hour_ago + timedelta(hours=1)).timestamp())
        block = w3.eth.get_block('latest', full_transactions=True)
        gas_prices = block['transactions']
        gas_used = sum([tx['gas'] for tx in gas_prices])
        gas_price = w3.fromWei(block['gasUsed'], 'ether') / w3.fromWei(block['gasLimit'], 'ether')
        transaction_cost = gas_used * gas_price
        average_transaction_cost_usd.append(transaction_cost * Decimal(str(eth_usd_price)))

    average_transaction_cost_usd = sum(average_transaction_cost_usd) / len(average_transaction_cost_usd)
    print('Avg trans. cost last 24h: ${:.2f}'.format(average_transaction_cost_usd))




# Get current block number and timestamp
    current_block = w3.eth.blockNumber
    current_time = datetime.now()

# Initialize list to store gas prices
    gas_prices_usd = []

# Loop over previous 6 hours
    for i in range(1, 7):
    # Calculate block number and timestamp for i hours ago
        block_number = current_block - i * 240  # Assuming 4 blocks are mined every minute
        block_time = current_time - timedelta(hours=i)

    # Get gas price of block
        block = w3.eth.get_block(block_number)
        gas_used = sum([w3.eth.getTransaction(tx_hash)['gas'] for tx_hash in block.transactions])
        gas_limit = block.gasLimit
        gas_price = gas_used / gas_limit

    # Convert to USD 
        gas_price_usd = gas_price * eth_usd_price
        gas_prices_usd.append(gas_price_usd)

    print(f"Gas used: {gas_used}")
    print(f"Gas limit: {gas_limit}")
    print(f"Gas price: {gas_price}")
    print(f"Gas price usd: {gas_price_usd}")

    print(f"Average gas prices in USD for last 6 hours: {gas_prices_usd}")

# Create a bar chart of the average gas price in the last 6 hours grouped by hour
    fig, ax = plt.subplots()
    ax.bar(range(1, 7), gas_prices_usd[-6:], color='#1DA1F2')
    ax.set_ylabel('Average gas price ($)')
    ax.set_xlabel('Last 6 hours in UTC time')
    ax.set_title('Average gas price in the last 6 hours')
    hours = [datetime.now() - timedelta(hours=x) for x in range(5,-1,-1)]
    ax.set_xticks(range(1, 7))

#fig.savefig('chart.png')

# Attach the chart image to the tweet
#media = api.media_upload('chart.png')


# Get historical gas prices for the last 30 days
    historical_gas_prices_30 = []
    today = datetime.now(timezone.utc).date()
    for i in range(1, 31):
        day = today - timedelta(days=i)
        start_time = int(datetime(day.year, day.month, day.day, tzinfo=timezone.utc).timestamp())
        end_time = int((datetime(day.year, day.month, day.day, tzinfo=timezone.utc) + timedelta(days=1)).timestamp())
        gas_prices = w3.eth.get_block('latest', full_transactions=False)['transactions']
        daily_gas_prices = []
        for tx in gas_prices:
            if start_time <= tx['block_timestamp'] < end_time:
                daily_gas_prices.append(tx['gas_price'])
        if len(daily_gas_prices) > 0:
            historical_gas_prices_30.append(sum(daily_gas_prices) / len(daily_gas_prices))

# Calculate the historical average 30d gas price in Gwei
    if len(historical_gas_prices_30) > 0:
        historical_average_gas_price_gwei_30 = sum(historical_gas_prices_30) / len(historical_gas_prices_30)
    else:
        historical_average_gas_price_gwei_30 = 0

# Convert the historical 30d average gas price to USD using the current ETH/USD price
    historical_average_gas_price_usd_30 = historical_average_gas_price_gwei_30 * 10**-9 * 21000 * eth_usd_price
    print(historical_average_gas_price_usd_30)


# Construct the tweet text
    tweet_text = f"🔷 ETH price is ${eth_usd_price} ({eth_usd_24h_change:+.2f}% last 24h)\n🔥 Average Ethereum gas price (24h): ${average_gas_price_usd:.2f}\n💰 Current gas price: ${current_gas_price_usd:.2f}\n📈 Historical average gas price (30d): ${historical_average_gas_price_usd_30:.2f}\n\n"
    
# Determine whether to wait or execute based on historical data
    if average_gas_price_usd > historical_average_gas_price_usd_30:
     tweet_text += "⚠️ Gas prices are higher than historical average. Consider waiting to execute transactions."
    else:
        tweet_text += "🚀 Gas prices are lower than historical average. Take advantage of lower fees and execute transactions now!"
    
    print(tweet_text)
# Send the tweet with the chart image attached
    api.update_status(status=tweet_text, media_ids=[media.media_id])
    
# Wait an hour before sending the next tweet
    time.sleep(3600)





