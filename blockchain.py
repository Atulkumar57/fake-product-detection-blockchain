import json
from pathlib import Path

from web3 import Web3

ROOT = Path(__file__).parent
DEPLOYMENT = ROOT / "deployment.json"


def _sanitize_text(value):
    if value is None:
        return ""
    return str(value).strip()


def load_deployment():
    if not DEPLOYMENT.exists():
        raise FileNotFoundError(
            "deployment.json not found. Run `npx hardhat node` and "
            "`npm run deploy:local` first."
        )
    try:
        data = json.loads(DEPLOYMENT.read_text())
    except json.JSONDecodeError as exc:
        raise ValueError(f"deployment.json is malformed: {exc}") from exc

    address = data.get("address") or data.get("contractAddress")
    abi = data.get("abi") or data.get("contractAbi")
    if not address or not abi:
        raise ValueError(
            "deployment.json must contain 'address' and 'abi' "
            f"(or 'contractAddress'/'contractAbi'). Found keys: {list(data)}"
        )
    return {"address": Web3.to_checksum_address(address), "abi": abi}


class Blockchain:
    def __init__(self, rpc_url="http://127.0.0.1:8545"):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={"timeout": 10}))
        if not self.w3.is_connected():
            raise ConnectionError("Could not connect to " + rpc_url)
        dep = load_deployment()
        self.contract = self.w3.eth.contract(address=dep["address"], abi=dep["abi"])

    def _build_tx(self, account, func, tx_overrides=None):
        tx_overrides = tx_overrides or {}
        base_tx = {
            "from": account.address,
            "nonce": self.w3.eth.get_transaction_count(account.address),
            "chainId": self.w3.eth.chain_id,
        }
        estimated = func.estimate_gas({"from": account.address})
        base_tx["gas"] = int(estimated * 1.2)
        latest = self.w3.eth.gas_price
        if latest is not None:
            base_tx["gasPrice"] = int(latest * 1.05)
        base_tx.update(tx_overrides)
        return func.build_transaction(base_tx)

    def _validate_product_fields(self, product_id, name, manufacturer, manufactured_at):
        product_id = _sanitize_text(product_id)
        name = _sanitize_text(name)
        manufacturer = _sanitize_text(manufacturer)

        if not product_id or not name or not manufacturer:
            raise ValueError("Product ID, name, and manufacturer are required.")

        manufactured_at = int(manufactured_at)
        if manufactured_at < 0:
            raise ValueError("Manufactured-at timestamp cannot be negative.")

        latest_block = self.w3.eth.get_block("latest")
        if manufactured_at > latest_block["timestamp"]:
            raise ValueError("Manufactured-at timestamp cannot be in the future.")

        return product_id, name, manufacturer, manufactured_at

    def register(self, product_id, name, manufacturer, manufactured_at, private_key):
        product_id, name, manufacturer, manufactured_at = self._validate_product_fields(
            product_id, name, manufacturer, manufactured_at
        )
        acct = self.w3.eth.account.from_key(private_key)
        fn = self.contract.functions.registerProduct(
            product_id, name, manufacturer, manufactured_at
        )
        tx = self._build_tx(acct, fn)
        signed = self.w3.eth.account.sign_transaction(tx, private_key=private_key)

        raw = getattr(signed, "rawTransaction", None)
        if raw is None:
            raw = signed.raw_transaction

        tx_hash = self.w3.eth.send_raw_transaction(raw)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

        if receipt.status != 1:
            raise RuntimeError(
                f"Transaction reverted on-chain (status=0, tx={Web3.to_hex(tx_hash)})"
            )
        return receipt

    def verify(self, product_id):
        product_id = _sanitize_text(product_id)
        if not product_id:
            raise ValueError("Product ID is required.")

        exists, name, manufacturer, manufactured_at, registered_by = (
            self.contract.functions.verifyProduct(product_id).call()
        )
        return {
            "exists": bool(exists),
            "name": name,
            "manufacturer": manufacturer,
            "manufactured_at": int(manufactured_at),
            "registered_by": registered_by,
        }

    def is_authorized_manufacturer(self, account):
        return bool(self.contract.functions.authorizedManufacturers(account).call())

    def manufacturer_name_for(self, account):
        return self.contract.functions.manufacturerNames(account).call()

    def register_manufacturer(self, account, manufacturer_name, private_key):
        acct = self.w3.eth.account.from_key(private_key)
        tx = self._build_tx(
            acct,
            self.contract.functions.authorizeManufacturer(
                Web3.to_checksum_address(account), manufacturer_name
            ),
        )
        signed = self.w3.eth.account.sign_transaction(tx, private_key=private_key)
        raw = getattr(signed, "rawTransaction", None)
        if raw is None:
            raw = signed.raw_transaction
        tx_hash = self.w3.eth.send_raw_transaction(raw)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        if receipt.status != 1:
            raise RuntimeError(
                f"Manufacturer authorization failed (status=0, tx={Web3.to_hex(tx_hash)})"
            )
        return receipt
