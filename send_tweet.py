#!/usr/bin/env python
# coding: utf-8

import json
import sys
from mastodon import Mastodon
import time
import ethers
from decimal import Decimal
from datetime import datetime, timezone, timedelta
from web3 import Web3
from web3 import HTTPProvider
import requests
import matplotlib.pyplot as plt
from etherscan import Etherscan
from dotenv import load_dotenv
import os


#API KEYS and env variables

load_dotenv()

alchemy = os.getenv('ALCHEMY_API_KEY')
alchemy_api_key=os.getenv('ALCHEMY_KEY')
etherscan_api_key = os.getenv('ETHERSCAN_API_KEY')
ifttt=os.getenv('ifttt_key')



# Connect to instances
w3 = Web3(Web3.HTTPProvider(alchemy))
etherscan = Etherscan(etherscan_api_key)
ifttt_url = f'https://maker.ifttt.com/trigger/post_tweet/with/key/{ifttt}'

mastodon = Mastodon(
    access_token=os.getenv('mastodon_accesstoken'),
    api_base_url='https://mastodon.social'
)


interval = 3600



#ETH price, 24h change and Gas price

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

    
        # Get the current gas price
        current_gas_price_gwei = w3.eth.gas_price / 10**9
        current_gas_price_usd = current_gas_price_gwei * 10**-9 * 21000 * eth_usd_price
    
    except KeyError:
    # Handle the Coingecko KeyError
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


# Construct the tweet text
    tweet_text = f"🔷 ETH price is ${eth_usd_price} ({eth_usd_24h_change:+.2f}% last 24h)\n🔥 Current Gas price: ${current_gas_price_usd:.2f} || Avg Gas Price last 24h: ${average_gas_price_usd:.2f}"

    print(tweet_text)


#Send out the tweet

    while True:
        try:
        # Post to Mastodon
            mastodon.toot(tweet_text)

        # Post to Steemit
            #c = Comment("", steem_instance=steem)
            #c.post(text)

        # Post to IFTTT
            payload = {'value1': tweet_text}
            response = requests.post(ifttt_url, json=payload)

            if response.status_code == 200:
                print('Tweet posted successfully via IFTTT!')
            else:
                print('Error posting tweet via IFTTT:', response.text)

        except Exception as e:
        
            print('Error posting text:', e)

    # Wait for the interval before posting again
        time.sleep(interval)





