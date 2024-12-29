import csv
import os
from web3 import Web3

# Alchemy URL (Replace YOUR_ALCHEMY_API_KEY with your actual Alchemy API key)
alchemy_url = 'https://eth-mainnet.g.alchemy.com/v2/oY_DEIcIgmoHz6sN1dFBCXGDUdgIltnb'

# Connect to the Alchemy Ethereum node using Web3
web3 = Web3(Web3.HTTPProvider(alchemy_url))

# Check if the connection is successful using is_connected()
if web3.is_connected():
    print("Successfully connected to Ethereum network via Alchemy.")
else:
    print("Failed to connect to the Ethereum network.")

# Get the latest block number
def get_latest_block_number():
    try:
        latest_block = web3.eth.block_number
        return latest_block
    except Exception as e:
        print(f"Error fetching latest block number: {str(e)}")
        return None

# Get the transactions in a block and their details
def get_transactions_in_block(block_number):
    try:
        block = web3.eth.get_block(block_number, full_transactions=True)  # full_transactions=True retrieves transaction details
        return block['transactions']
    except Exception as e:
        print(f"Error fetching transactions for block {block_number}: {str(e)}")
        return []

# Get transaction details
def get_transaction_details(tx_hash):
    try:
        transaction = web3.eth.get_transaction(tx_hash)
        receipt = web3.eth.get_transaction_receipt(tx_hash)  # Get transaction receipt for logs and status
        return transaction, receipt
    except Exception as e:
        print(f"Error fetching transaction details for {tx_hash}: {str(e)}")
        return None, None

# Fetch the last 100 transactions
def fetch_last_100_transactions():
    latest_block = get_latest_block_number()
    if latest_block is None:
        print("Could not fetch latest block number.")
        return

    transactions_fetched = 0
    block_number = latest_block
    all_transactions = []

    while transactions_fetched < 100 and block_number >= 0:
        print(f"Fetching block {block_number}...")
        transactions = get_transactions_in_block(block_number)
        
        # Process each transaction in the block
        for tx in transactions:
            if transactions_fetched >= 100:
                break
            tx_details, receipt = get_transaction_details(tx['hash'])
            if tx_details:
                all_transactions.append({
                    'transaction_hash': tx_details['hash'].hex(),
                    'from': tx_details['from'],
                    'to': tx_details['to'],
                    'value_in_eth': web3.from_wei(tx_details['value'], 'ether'),
                    'gas_used': receipt['gasUsed'],
                    'block_number': tx_details['blockNumber'],
                    'block_hash': tx_details['blockHash'].hex(),
                    'status': 'Success' if receipt['status'] == 1 else 'Failed'
                })
                transactions_fetched += 1

        block_number -= 1  # Move to the previous block

    return all_transactions

# Save transactions to CSV in the same folder as the script
def save_transactions_to_csv(transactions, file_name):
    # Define column names
    fieldnames = ['transaction_hash', 'from', 'to', 'value_in_eth', 'gas_used', 'block_number', 'block_hash', 'status']
    
    # Get the directory where the script is located
    script_directory = os.path.dirname(os.path.realpath(__file__))
    save_file_path = os.path.join(script_directory, file_name)
    
    # Create the CSV file and write the transactions
    try:
        with open(save_file_path, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()  # Write the header
            writer.writerows(transactions)  # Write transaction data
        print(f"Transactions saved to {save_file_path}")
    except Exception as e:
        print(f"Error saving to CSV: {str(e)}")

# Fetch and save last 100 transactions to CSV
transactions = fetch_last_100_transactions()
if transactions:
    # Save transactions to CSV file in the same folder as the script
    save_transactions_to_csv(transactions, 'last_100_transactions.csv')
