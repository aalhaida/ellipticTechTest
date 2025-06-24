import csv
import sys
import os
import requests
from dotenv import load_dotenv
from web3 import Web3

load_dotenv()

INFURA_URL = os.getenv("INFURA_URL")
BLOCKCYPHER_URL = "https://api.blockcypher.com/v1/btc/main"
SOLANA_RPC = "https://api.mainnet-beta.solana.com"

w3 = Web3(Web3.HTTPProvider(INFURA_URL))


def get_eth_data(address):
    if not w3.isAddress(address):
        raise ValueError("Invalid Ethereum address")
    address = w3.toChecksumAddress(address)
    balance_wei = w3.eth.get_balance(address)
    balance_eth = w3.fromWei(balance_wei, 'ether')
    nonce = w3.eth.get_transaction_count(address)
    return {
        "currency": "ETH",
        "address": address,
        "balance": float(balance_eth),
        "tx_count": nonce
    }


def get_btc_data(address):
    r = requests.get(f"{BLOCKCYPHER_URL}/addrs/{address}/balance")
    if r.status_code != 200:
        raise ValueError("Invalid BTC address or error from API")
    data = r.json()
    return {
        "currency": "BTC",
        "address": address,
        "balance": data["balance"] / 1e8,
        "tx_count": data["n_tx"]
    }


def get_solana_data(address):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getBalance",
        "params": [address]
    }
    r = requests.post(SOLANA_RPC, json=payload)
    if r.status_code != 200:
        raise ValueError("Invalid Solana address or error from RPC")
    result = r.json().get("result")
    if not result:
        raise ValueError("No result from Solana RPC")
    balance_sol = result["value"] / 1e9
    return {
        "currency": "SOL",
        "address": address,
        "balance": balance_sol,
        "tx_count": "N/A"
    }


def write_csv(data, filename="address_data.csv"):
    with open(filename, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=data.keys())
        writer.writeheader()
        writer.writerow(data)


def main():
    if len(sys.argv) != 3:
        print("Usage: python multi_chain_balance_exporter.py <currency> <address>")
        print("Supported currencies: ETH, BTC, SOL")
        sys.exit(1)

    currency = sys.argv[1].upper()
    address = sys.argv[2].strip()

    try:
        if currency == "ETH":
            data = get_eth_data(address)
        elif currency == "BTC":
            data = get_btc_data(address)
        elif currency == "SOL":
            data = get_solana_data(address)
        else:
            raise ValueError("Unsupported currency")

        write_csv(data)
        print(f"✅ Data written to address_data.csv:\n{data}")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
