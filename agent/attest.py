"""Write the audit verdict on-chain.

Two writes (deep ERC-8004 integration):
  1. AuditAttestationRegistry.attest(...)         -> our composable, queryable registry.
  2. ReputationRegistry.giveFeedback(...)         -> binds the verdict to the target's ERC-8004
     identity NFT, so the security reputation travels with the agent. Only attempted when an
     erc8004_agent_id is supplied (the target is a registered agent).

The operator key is read from DEPLOYER_PRIVATE_KEY in the environment at runtime. Never hardcoded,
never logged."""
import os
from typing import Dict

from web3 import Web3
from eth_account import Account

from config import RPC_URL, AUDIT_REGISTRY, ERC8004_REPUTATION, EXPLORER_TX

_REGISTRY_ABI = [{
    "type": "function", "name": "attest", "stateMutability": "nonpayable",
    "inputs": [
        {"name": "auditedContract", "type": "address"},
        {"name": "pass", "type": "bool"},
        {"name": "vulnCount", "type": "uint16"},
        {"name": "highestSeverity", "type": "uint8"},
        {"name": "erc8004AgentId", "type": "uint256"},
        {"name": "reportHash", "type": "bytes32"},
        {"name": "ipfsCID", "type": "string"},
    ],
    "outputs": [{"name": "index", "type": "uint256"}],
}]

_REPUTATION_ABI = [{
    "type": "function", "name": "giveFeedback", "stateMutability": "nonpayable",
    "inputs": [
        {"name": "agentId", "type": "uint256"},
        {"name": "value", "type": "int128"},
        {"name": "valueDecimals", "type": "uint8"},
        {"name": "tag1", "type": "string"},
        {"name": "tag2", "type": "string"},
        {"name": "endpoint", "type": "string"},
        {"name": "feedbackURI", "type": "string"},
        {"name": "feedbackHash", "type": "bytes32"},
    ],
    "outputs": [],
}]


def _w3_and_account():
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    pk = os.getenv("DEPLOYER_PRIVATE_KEY")
    if not pk:
        raise RuntimeError("DEPLOYER_PRIVATE_KEY not set in environment")
    acct = Account.from_key(pk)
    return w3, acct


def _txhash_hex(rcpt) -> str:
    h = rcpt["transactionHash"]
    s = h.hex() if hasattr(h, "hex") else str(h)
    return s if s.startswith("0x") else "0x" + s


def _send(w3, acct, fn, nonce):
    """Send with an explicit nonce. Mantle's sequencer can lag on get_transaction_count right after a
    tx is mined, so the caller manages the nonce and increments it per tx."""
    tx = fn.build_transaction({
        "from": acct.address,
        "nonce": nonce,
        "chainId": w3.eth.chain_id,
        "gas": 500000,
        "gasPrice": w3.eth.gas_price,
    })
    signed = acct.sign_transaction(tx)
    h = w3.eth.send_raw_transaction(signed.raw_transaction)
    rcpt = w3.eth.wait_for_transaction_receipt(h, timeout=180)
    if rcpt.get("status") != 1:
        raise RuntimeError(f"transaction reverted on-chain: {_txhash_hex(rcpt)}")
    return rcpt


def write_attestation(target: str, passed: bool, vuln_count: int, highest_severity: int,
                      erc8004_agent_id: int, report_hash_hex: str, ipfs_cid: str) -> Dict:
    """Write to our registry, and (if agent_id>0) bind to ERC-8004 reputation. Returns tx info."""
    w3, acct = _w3_and_account()
    target = Web3.to_checksum_address(target)
    rh = bytes.fromhex(report_hash_hex[2:]) if report_hash_hex.startswith("0x") else bytes.fromhex(report_hash_hex)

    nonce = w3.eth.get_transaction_count(acct.address, "pending")
    reg = w3.eth.contract(address=Web3.to_checksum_address(AUDIT_REGISTRY), abi=_REGISTRY_ABI)
    rcpt = _send(w3, acct, reg.functions.attest(
        target, passed, vuln_count, highest_severity, erc8004_agent_id, rh, ipfs_cid), nonce)
    nonce += 1
    reg_hash = _txhash_hex(rcpt)
    result = {
        "registryTx": reg_hash,
        "registryTxUrl": EXPLORER_TX + reg_hash,
        "reputationTx": None,
    }

    if erc8004_agent_id and erc8004_agent_id > 0:
        # score: 100 = clean pass, else scaled down by severity (5=critical -> 0)
        score = 100 if passed else max(0, 100 - highest_severity * 20)
        rep = w3.eth.contract(address=Web3.to_checksum_address(ERC8004_REPUTATION), abi=_REPUTATION_ABI)
        try:
            r2 = _send(w3, acct, rep.functions.giveFeedback(
                erc8004_agent_id, score, 0, "security-audit",
                "critical" if highest_severity >= 5 else "high" if highest_severity == 4 else "ok",
                "mantle-sentinel", ipfs_cid or "", rh), nonce)
            rep_hash = _txhash_hex(r2)
            result["reputationTx"] = rep_hash
            result["reputationTxUrl"] = EXPLORER_TX + rep_hash
        except Exception as e:
            result["reputationError"] = str(e)[:200]
    return result
