import json
from pathlib import Path

from web3 import Web3

ROOT = Path(__file__).parent
DEPLOYMENT = ROOT / "deployment.json"


def load_deployment():
    if not DEPLOYMENT.exists():
        raise FileNotFoundError(
            "deployment.json not found. Run `npx hardhat node` and "
            "`npm run deploy:local` first."
        )
    return json.loads(DEPLOYMENT.read_text())


class Blockchain:
    def __init__(self, rpc_url="http://127.0.0.1:8545"):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        if not self.w3.is_connected():
            raise ConnectionError("Could not connect to " + rpc_url)
        dep = load_deployment()
        self.contract = self.w3.eth.contract(address=dep["address"], abi=dep["abi"])

    def register(self, product_id, name, manufacturer, manufactured_at, private_key):
        acct = self.w3.eth.account.from_key(private_key)
        tx = self.contract.functions.registerProduct(
            product_id, name, manufacturer, manufactured_at
        ).build_transaction({
            "from": acct.address,
            "nonce": self.w3.eth.get_transaction_count(acct.address),
            "gas": 500000,
            "gasPrice": self.w3.eth.gas_price,
        })
        signed = self.w3.eth.account.sign_transaction(tx, private_key=private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        return receipt

    def verify(self, product_id):
        exists, name, manufacturer, manufactured_at, registered_by = (
            self.contract.functions.verifyProduct(product_id).call()
        )
        return {
            "exists": exists,
            "name": name,
            "manufacturer": manufacturer,
            "manufactured_at": manufactured_at,
            "registered_by": registered_by,
        }
