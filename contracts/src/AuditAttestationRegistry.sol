// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

/// @title AuditAttestationRegistry
/// @notice On-chain, composable security attestations for contracts and on-chain agents on Mantle.
///         An AI auditor writes a pass/fail verdict keyed to an audited contract address. The full
///         report lives off-chain (IPFS); only a keccak256 hash + CID are stored, so any verdict is
///         tamper-evident and falsifiable. Reads are permissionless so other contracts and frontends
///         can call `isAttestedSafe(addr)`; writes are restricted to allowlisted auditor keys so a
///         "pass" cannot be forged. Trust is solved on the write path; verification on the read path.
contract AuditAttestationRegistry {
    struct Attestation {
        address auditor; // msg.sender that wrote it
        bool pass; // verdict: true = no high/critical findings
        uint16 vulnCount; // number of findings in the report
        uint8 highestSeverity; // 0 none, 1 info, 2 low, 3 medium, 4 high, 5 critical
        uint256 erc8004AgentId; // bound ERC-8004 identity (0 if target is not a registered agent)
        bytes32 reportHash; // keccak256 of the canonical report JSON
        string ipfsCID; // full report on IPFS
        uint64 timestamp;
    }

    address public owner;
    mapping(address => bool) public isAuditor; // allowlisted writer keys
    mapping(address => Attestation[]) private _history; // audited contract => append-only attestations

    event AuditorSet(address indexed auditor, bool allowed);
    event Attested(
        address indexed auditedContract,
        address indexed auditor,
        bool pass,
        uint16 vulnCount,
        uint8 highestSeverity,
        uint256 erc8004AgentId,
        bytes32 reportHash,
        uint256 index
    );

    error NotOwner();
    error NotAuditor();
    error ZeroAddress();
    error EmptyReport();
    error NoAttestation();

    modifier onlyOwner() {
        if (msg.sender != owner) revert NotOwner();
        _;
    }

    constructor() {
        owner = msg.sender;
        isAuditor[msg.sender] = true; // deployer is the first auditor
        emit AuditorSet(msg.sender, true);
    }

    /// @notice Allow or revoke an auditor key.
    function setAuditor(address auditor, bool allowed) external onlyOwner {
        if (auditor == address(0)) revert ZeroAddress();
        isAuditor[auditor] = allowed;
        emit AuditorSet(auditor, allowed);
    }

    function transferOwnership(address newOwner) external onlyOwner {
        if (newOwner == address(0)) revert ZeroAddress();
        owner = newOwner;
    }

    /// @notice Write a security verdict for `auditedContract`. Restricted to allowlisted auditors.
    /// @dev No external calls — storage write + event only, so the function is reentrancy-safe.
    function attest(
        address auditedContract,
        bool pass,
        uint16 vulnCount,
        uint8 highestSeverity,
        uint256 erc8004AgentId,
        bytes32 reportHash,
        string calldata ipfsCID
    ) external returns (uint256 index) {
        if (!isAuditor[msg.sender]) revert NotAuditor();
        if (auditedContract == address(0)) revert ZeroAddress();
        if (reportHash == bytes32(0)) revert EmptyReport();

        _history[auditedContract].push(
            Attestation({
                auditor: msg.sender,
                pass: pass,
                vulnCount: vulnCount,
                highestSeverity: highestSeverity,
                erc8004AgentId: erc8004AgentId,
                reportHash: reportHash,
                ipfsCID: ipfsCID,
                timestamp: uint64(block.timestamp)
            })
        );
        index = _history[auditedContract].length - 1;
        emit Attested(
            auditedContract, msg.sender, pass, vulnCount, highestSeverity, erc8004AgentId, reportHash, index
        );
    }

    /// @notice Latest verdict pass/fail. Reverts if never audited — callers should check `count` first
    ///         or use `isAttestedSafe` which treats "never audited" as not safe.
    function latest(address auditedContract) external view returns (Attestation memory) {
        Attestation[] storage arr = _history[auditedContract];
        if (arr.length == 0) revert NoAttestation();
        return arr[arr.length - 1];
    }

    /// @notice Composable safety check: true only if the most recent attestation passed.
    ///         Never audited => false (safe default for integrators).
    function isAttestedSafe(address auditedContract) external view returns (bool) {
        Attestation[] storage arr = _history[auditedContract];
        if (arr.length == 0) return false;
        return arr[arr.length - 1].pass;
    }

    function count(address auditedContract) external view returns (uint256) {
        return _history[auditedContract].length;
    }

    function attestationAt(address auditedContract, uint256 index)
        external
        view
        returns (Attestation memory)
    {
        return _history[auditedContract][index];
    }
}
