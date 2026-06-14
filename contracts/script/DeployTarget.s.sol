// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Script.sol";
import "../test-targets/VulnerableVault.sol";

/// @notice Deploys the deliberately-vulnerable sample as a real on-chain audit target.
contract DeployTarget is Script {
    function run() external returns (VulnerableVault v) {
        uint256 pk = vm.envUint("DEPLOYER_PRIVATE_KEY");
        vm.startBroadcast(pk);
        v = new VulnerableVault();
        vm.stopBroadcast();
        console2.log("VulnerableVault deployed at:", address(v));
    }
}
