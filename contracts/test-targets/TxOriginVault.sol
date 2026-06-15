// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @dev Uses tx.origin for authorization — a real (medium) phishing-prone access-control flaw.
contract TxOriginVault {
    address public owner;

    constructor() {
        owner = msg.sender;
    }

    function withdrawAll(address payable to) external {
        require(tx.origin == owner, "not owner"); // tx.origin auth -> phishable
        to.transfer(address(this).balance);
    }

    receive() external payable {}
}
