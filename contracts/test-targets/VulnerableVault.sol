// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @dev Deliberately vulnerable sample used to prove the auditor finds real bugs.
///      Contains a classic reentrancy: the external call happens BEFORE the balance update.
contract VulnerableVault {
    mapping(address => uint256) public balances;

    function deposit() external payable {
        balances[msg.sender] += msg.value;
    }

    function withdraw(uint256 amount) external {
        require(balances[msg.sender] >= amount, "insufficient");
        (bool ok,) = msg.sender.call{value: amount}(""); // external call before state update
        require(ok, "send failed");
        balances[msg.sender] -= amount; // state updated AFTER the call -> reentrancy
    }
}
