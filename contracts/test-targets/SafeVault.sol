// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @dev A correct vault — effects before interaction (no reentrancy). Used to show a PASS verdict.
contract SafeVault {
    mapping(address => uint256) public balances;

    function deposit() external payable {
        balances[msg.sender] += msg.value;
    }

    function withdraw(uint256 amount) external {
        require(balances[msg.sender] >= amount, "insufficient");
        balances[msg.sender] -= amount; // state updated BEFORE the external call
        (bool ok,) = msg.sender.call{value: amount}("");
        require(ok, "send failed");
    }
}
