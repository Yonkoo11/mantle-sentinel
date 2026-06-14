"""ERC-8004 helpers on Mantle Sepolia.

register_agent(): mint an ERC-8004 identity (one-time) for an agent, returning its agentId. Used both
to give our auditor its own on-chain identity and, in the demo, to stand up a "competing agent" whose
contract we then audit and whose reputation carries the verdict."""
import os
import sys
import json

from web3 import Web3
from eth_account import Account

from config import RPC_URL, ERC8004_IDENTITY, EXPLORER_TX

_IDENTITY_ABI = [
    {"type": "function", "name": "register", "stateMutability": "nonpayable",
     "inputs": [{"name": "agentURI", "type": "string"}], "outputs": [{"name": "agentId", "type": "uint256"}]},
    {"type": "function", "name": "ownerOf", "stateMutability": "view",
     "inputs": [{"name": "tokenId", "type": "uint256"}], "outputs": [{"name": "", "type": "address"}]},
    {"type": "event", "name": "Registered", "anonymous": False, "inputs": [
        {"name": "agentId", "type": "uint256", "indexed": True},
        {"name": "agentURI", "type": "string", "indexed": False},
        {"name": "owner", "type": "address", "indexed": True}]},
]


def register_agent(agent_uri: str) -> dict:
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    pk = os.getenv("DEPLOYER_PRIVATE_KEY")
    if not pk:
        raise RuntimeError("DEPLOYER_PRIVATE_KEY not set")
    acct = Account.from_key(pk)
    idr = w3.eth.contract(address=Web3.to_checksum_address(ERC8004_IDENTITY), abi=_IDENTITY_ABI)
    fn = idr.functions.register(agent_uri)
    tx = fn.build_transaction({
        "from": acct.address, "nonce": w3.eth.get_transaction_count(acct.address),
        "chainId": w3.eth.chain_id, "gas": 600000, "gasPrice": w3.eth.gas_price,
    })
    signed = acct.sign_transaction(tx)
    h = w3.eth.send_raw_transaction(signed.raw_transaction)
    rcpt = w3.eth.wait_for_transaction_receipt(h, timeout=180)
    agent_id = None
    for log in idr.events.Registered().process_receipt(rcpt, errors=__import__("web3").logs.DISCARD):
        agent_id = log["args"]["agentId"]
        break
    th = rcpt["transactionHash"]
    ths = th.hex() if hasattr(th, "hex") else str(th)
    if not ths.startswith("0x"):
        ths = "0x" + ths
    return {"agentId": agent_id, "tx": ths, "txUrl": EXPLORER_TX + ths, "owner": acct.address}


if __name__ == "__main__":
    uri = sys.argv[1] if len(sys.argv) > 1 else "https://mantle-sentinel.example/agent.json"
    print(json.dumps(register_agent(uri), indent=2))
