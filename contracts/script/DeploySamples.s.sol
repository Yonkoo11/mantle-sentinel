// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Script.sol";
import "../test-targets/SafeVault.sol";
import "../test-targets/TxOriginVault.sol";

/// @notice Deploys extra audit targets so the registry shows a real spread of verdicts.
contract DeploySamples is Script {
    function run() external returns (SafeVault safe, TxOriginVault txo) {
        uint256 pk = vm.envUint("DEPLOYER_PRIVATE_KEY");
        vm.startBroadcast(pk);
        safe = new SafeVault();
        txo = new TxOriginVault();
        vm.stopBroadcast();
        console2.log("SafeVault:", address(safe));
        console2.log("TxOriginVault:", address(txo));
    }
}
