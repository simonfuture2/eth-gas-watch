[![Build](https://github.com/Gridddd/eth-gas-watch/actions/workflows/python-app.yml/badge.svg?branch=main)](https://github.com/Gridddd/eth-gas-watch/actions/workflows/python-app.yml) ![Open issues](https://img.shields.io/github/issues-raw/Gridddd/eth-gas-watch?color=red&label=Open%20Issues) [![Donate](https://img.shields.io/static/v1?label=Donate&message=Ethereum&color=3C3C3D&logo=ethereum)](https://etherscan.io/address/0x5F4a5E69248f6580c438B31AEdC648e518bD9828)




# Eth Gas Watch

Eth Gas Watch is an automated tool that sends a tweet or message every hour with relevant real-time data about the Ethereum Blockchain. This information can be useful for anyone who interacts with the Ethereum Blockchain and wants to stay informed about gas prices and other metrics.\
\
You can check the current account on Twitter [![Twitter](https://img.shields.io/twitter/follow/ethgaswatch?style=social)](https://twitter.com/ethgaswatch) and Telegram [![Telegram](https://img.shields.io/badge/Join-Telegram-blue.svg?logo=telegram)](https://t.me/ethgaswatch)



## Contents
- Getting Started
- Installation
- License

## Getting Started
Before using Eth Gas Watch, you will need to make sure you have the following API keys:

- [Alchemy](https://docs.alchemy.com/reference/api-overview)
- [Etherscan](https://docs.etherscan.io/)


Alchemy and Etherscan are the providers of choice, although others are encouraged to be used if you find more suitable endpoints.\
\
The Telegram bot API is not needed and you can avoid having to set one up, just comment or delete those lines.\
\
The main file is `main.py` and the Python version is `3.10.6`.

## Installation

To install Eth Gas Watch, follow these steps:

1. Clone the project repository to your local machine.
2. Create a virtual environment in your project directory:

```
python3 -m venv venv
```
3. Activate the virtual environment:
```
source venv/bin/activate
```
4. Install the required packages:
```
pip install -r requirements.txt
```
5. Set up your API keys as environment variables in a `.env` file.

## License
Eth Gas Watch is licensed under the MIT License.





