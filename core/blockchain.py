from web3 import Web3
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# -------------------- 1. Environment Setup --------------------
from web3 import Web3
import json, os
from dotenv import load_dotenv

load_dotenv()

INFURA_URL = os.getenv("INFURA_URL")
CONTRACT_ADDRESS = Web3.to_checksum_address(os.getenv("CONTRACT_ADDRESS"))
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
SENDER_WALLET = os.getenv("WALLET_ADDRESS")

w3 = Web3(Web3.HTTPProvider(INFURA_URL))

# Load contract ABI
with open(os.path.join(os.path.dirname(__file__), "abi","contract_abi.json")) as f:
    abi = json.load(f)

contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)
# -------------------- 4. Register Doctor Function --------------------

# blockchain.py

def register_doctor_on_chain(wallet, name, credit_level):
    wallet = Web3.to_checksum_address(wallet)
    sender = Web3.to_checksum_address("0xFd7057C729b8D2E4EBEa48d16D46BB3502244604")
    nonce = w3.eth.get_transaction_count(sender)

    txn = contract.functions.registerDoctor(wallet, name, credit_level).build_transaction({
        'chainId': 11155111,
        'from': sender,
        'nonce': nonce,
        'gas': 3000000,
        'gasPrice': w3.to_wei('10', 'gwei'),
    })

    signed_txn = w3.eth.account.sign_transaction(txn, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
    return w3.to_hex(tx_hash)
 
def request_access_on_chain(wallet_address,patient_id):
    try:
        wallet = Web3.to_checksum_address(wallet_address)
        sender = Web3.to_checksum_address(SENDER_WALLET)
        nonce = w3.eth.get_transaction_count(sender)

        txn = contract.functions.requestAccess("Emergency Access").build_transaction({
            'chainId': 11155111,  # Sepolia Testnet
            'from': sender,
            'nonce': nonce,
            'gas': 300000,
            'gasPrice': w3.to_wei('10', 'gwei'),
        })

        signed_txn = w3.eth.account.sign_transaction(txn, PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)


        return w3.to_hex(tx_hash)

    except Exception as e:
        print(f"❌ Error requesting access: {e}")
        return None
