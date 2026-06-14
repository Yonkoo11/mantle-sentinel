// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

import "forge-std/Test.sol";
import "../src/AuditAttestationRegistry.sol";

contract AuditAttestationRegistryTest is Test {
    AuditAttestationRegistry reg;
    address auditor = address(0xA11CE);
    address target = address(0xBEEF);

    function setUp() public {
        reg = new AuditAttestationRegistry(); // this == owner + first auditor
    }

    function test_OwnerIsDeployerAndAuditor() public view {
        assertEq(reg.owner(), address(this));
        assertTrue(reg.isAuditor(address(this)));
    }

    function test_AttestAndReadBack() public {
        uint256 idx = reg.attest(target, true, 0, 0, 42, keccak256("report"), "QmCID");
        assertEq(idx, 0);
        assertTrue(reg.isAttestedSafe(target));
        AuditAttestationRegistry.Attestation memory a = reg.latest(target);
        assertEq(a.auditor, address(this));
        assertTrue(a.pass);
        assertEq(a.erc8004AgentId, 42);
        assertEq(a.ipfsCID, "QmCID");
        assertEq(reg.count(target), 1);
    }

    function test_FailVerdictNotSafe() public {
        reg.attest(target, false, 3, 5, 0, keccak256("bad"), "QmBad");
        assertFalse(reg.isAttestedSafe(target));
    }

    function test_LatestWins_AppendOnly() public {
        reg.attest(target, false, 2, 4, 0, keccak256("v1"), "Qm1");
        reg.attest(target, true, 0, 0, 0, keccak256("v2"), "Qm2");
        assertEq(reg.count(target), 2);
        assertTrue(reg.isAttestedSafe(target));
    }

    function test_NeverAudited_IsNotSafe() public view {
        assertFalse(reg.isAttestedSafe(address(0xDEAD)));
    }

    function test_RevertWhen_NotAuditor() public {
        vm.prank(auditor);
        vm.expectRevert(AuditAttestationRegistry.NotAuditor.selector);
        reg.attest(target, true, 0, 0, 0, keccak256("x"), "Qm");
    }

    function test_RevertWhen_EmptyReportHash() public {
        vm.expectRevert(AuditAttestationRegistry.EmptyReport.selector);
        reg.attest(target, true, 0, 0, 0, bytes32(0), "Qm");
    }

    function test_RevertWhen_ZeroTarget() public {
        vm.expectRevert(AuditAttestationRegistry.ZeroAddress.selector);
        reg.attest(address(0), true, 0, 0, 0, keccak256("x"), "Qm");
    }

    function test_SetAuditor_AllowsWrite() public {
        reg.setAuditor(auditor, true);
        vm.prank(auditor);
        reg.attest(target, true, 0, 0, 0, keccak256("ok"), "Qm");
        assertTrue(reg.isAttestedSafe(target));
    }

    function test_RevertWhen_NonOwnerSetsAuditor() public {
        vm.prank(auditor);
        vm.expectRevert(AuditAttestationRegistry.NotOwner.selector);
        reg.setAuditor(auditor, true);
    }
}
