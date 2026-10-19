# Fake Product Detection Using Blockchain

A tamper-proof product registry on Ethereum. Only recognized manufacturers may register products, and anyone can verify authenticity.

## Stack
- Smart contract: Solidity 0.8.20 (Hardhat)
- Python client: web3.py
- UI: Streamlit

## Setup
1. Install JS deps and start the local chain:
   npm install
   npx hardhat node

2. In a second terminal, deploy the contract:
   npm run deploy:local

3. Install Python deps:
   pip install -r requirements.txt

4. Run the UI:
   streamlit run app.py

5. Authorize a manufacturer account from the contract owner, then use that account's private key in the UI.

## Important security model
- Manufacturer authorization is owner-controlled.
- A registered manufacturer must submit the exact manufacturer name previously assigned to that account.
- Empty values, invalid timestamps, and duplicate product IDs are rejected.
- Product verification is public and read-only.

## Features
- Owner-only manufacturer authorization
- Exact manufacturer-name enforcement
- Duplicate product-ID protection
- Public verification view (no gas needed)
- Events for off-chain indexing
