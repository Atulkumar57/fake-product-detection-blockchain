# Fake Product Detection Using Blockchain

A tamper-proof product registry on Ethereum. Authorized manufacturers register product IDs on-chain; anyone can verify authenticity.

## Stack
- Smart contract: Solidity 0.8.20 (Hardhat)
- Python client: web3.py
- UI: Streamlit

## Setup
1. Install JS deps and start local chain:
   npm install
   npx hardhat node

2. In a second terminal: deploy
   npm run deploy:local

3. Install Python deps:
   pip install -r requirements.txt

4. Run UI:
   streamlit run app.py

Use a private key printed by `npx hardhat node` (e.g. Account #0) as the manufacturer key in the sidebar.

## Features
- Owner-only manufacturer authorization
- Duplicate product-ID protection
- Public verification view (no gas needed)
- Events for off-chain indexing
