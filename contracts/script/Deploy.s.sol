// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

import "forge-std/Script.sol";
import "../src/AuditAttestationRegistry.sol";

/// @notice Deploys AuditAttestationRegistry to Mantle Sepolia.
/// @dev Reads the deployer key from the environment at runtime — never hardcoded, never on the CLI.
contract Deploy is Script {
    function run() external returns (AuditAttestationRegistry reg) {
        uint256 pk = vm.envUint("DEPLOYER_PRIVATE_KEY");
        vm.startBroadcast(pk);
        reg = new AuditAttestationRegistry();
        vm.stopBroadcast();
        console2.log("AuditAttestationRegistry deployed at:", address(reg));
    }
}
