# Sowing Airdrop Auto-Claim Bot
# Author: ChatGPT x You
# Description: Claim Diamonds every 3 hours automatically via wallet confirmation

import time
import random
from web3 import Web3
from eth_account import Account

# === CONFIGURATIONS ===
RPC_URL = 'https://bsc-dataseed.binance.org/'  # Ganti sesuai chain Sowing
MIN_BALANCE_ETH = 0.001
CLAIM_INTERVAL_HOURS = 3

# Load private keys from file
with open('privateKeys.txt', 'r') as f:
    PRIVATE_KEYS = [line.strip() for line in f if line.strip()]

# Connect to RPC
w3 = Web3(Web3.HTTPProvider(RPC_URL))
if not w3.is_connected():
    print("❌ Gagal terhubung ke RPC")
    exit()

# === FUNCTIONS ===
def claim_diamonds(private_key):
    account = Account.from_key(private_key)
    address = account.address
    balance = w3.eth.get_balance(address)

    if balance < w3.to_wei(MIN_BALANCE_ETH, 'ether'):
        print(f"⚠️  Wallet {address} saldo kurang dari {MIN_BALANCE_ETH} ETH. Diskip.")
        return

    print(f"🚀 Claiming dari wallet {address}...")

    # Kontrak dan ABI Sowing
    contract_address = w3.to_checksum_address("0x522439A28EbFb99Ee1d3FccfE0C87FbdD68dD95C")
    inviter_address = w3.to_checksum_address("0x0000000000000000000000000000000000000000")  # ubah kalau kamu mau pakai referral

    sowing_abi = [
        {
            "inputs": [
                {"internalType": "address", "name": "inviter", "type": "address"}
            ],
            "name": "claim",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        }
    ]

    contract = w3.eth.contract(address=contract_address, abi=sowing_abi)
    nonce = w3.eth.get_transaction_count(address, 'pending')
    tx = contract.functions.claim(inviter_address).build_transaction({
        'from': address,
        'nonce': nonce,
        'gas': 200000,
        'gasPrice': w3.eth.gas_price,
        'chainId': w3.eth.chain_id
    })

    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    print(f"✅ Claim sukses untuk {address}: https://explorer.taker.xyz/tx/{tx_hash.hex()}")

# === LOOP ===
while True:
    print("============================")
    print("⏳ Mulai ronde klaim baru")
    for idx, pk in enumerate(PRIVATE_KEYS):
        print(f"\n🔢 Wallet #{idx+1}")
        try:
            claim_diamonds(pk)
            delay = random.randint(10, 60)
            print(f"⏱️ Delay {delay} detik ke wallet berikutnya...")
            time.sleep(delay)
        except Exception as e:
            print(f"❌ Error di wallet #{idx+1}: {e}")
    print(f"🕒 Tunggu {CLAIM_INTERVAL_HOURS} jam sebelum klaim selanjutnya...\n")
    time.sleep(CLAIM_INTERVAL_HOURS * 3600)
