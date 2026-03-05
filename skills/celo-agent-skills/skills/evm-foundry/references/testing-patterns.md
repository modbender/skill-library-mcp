# Foundry Testing Patterns

## Test Structure

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

import {Test, console} from "forge-std/Test.sol";
import {MyContract} from "../src/MyContract.sol";

contract MyContractTest is Test {
    MyContract public myContract;
    address public owner;
    address public user;

    function setUp() public {
        owner = address(this);
        user = makeAddr("user");
        myContract = new MyContract("Initial");
    }

    function test_InitialState() public view {
        assertEq(myContract.name(), "Initial");
    }
}
```

## Testing Events

```solidity
function test_EmitsEvent() public {
    vm.expectEmit(true, true, true, true);
    emit MyContract.ValueChanged(0, 100);
    myContract.setValue(100);
}
```

## Testing Reverts

```solidity
function test_RevertsWithMessage() public {
    vm.prank(user);
    vm.expectRevert("Not owner");
    myContract.onlyOwnerFunction();
}

function test_RevertsWithCustomError() public {
    vm.expectRevert(
        abi.encodeWithSelector(MyContract.InsufficientBalance.selector, 0, 100)
    );
    myContract.withdraw(100);
}
```

## Fuzz Testing

```solidity
function testFuzz_SetValue(uint256 value) public {
    myContract.setValue(value);
    assertEq(myContract.value(), value);
}

function testFuzz_BoundedValue(uint256 value) public {
    value = bound(value, 1, 1000);
    myContract.setValue(value);
}
```

## Time Manipulation

```solidity
function test_AfterTimePasses() public {
    // Warp to specific timestamp
    vm.warp(block.timestamp + 1 days);

    // Roll to specific block
    vm.roll(block.number + 100);
}
```

## Account Manipulation

```solidity
function test_AsUser() public {
    // Single call as user
    vm.prank(user);
    myContract.publicFunction();

    // Multiple calls as user
    vm.startPrank(user);
    myContract.function1();
    myContract.function2();
    vm.stopPrank();
}

function test_WithBalance() public {
    vm.deal(user, 10 ether);
    assertEq(user.balance, 10 ether);
}
```

## Snapshots

```solidity
function test_WithSnapshot() public {
    uint256 snapshot = vm.snapshot();

    myContract.setValue(100);

    vm.revertTo(snapshot);
    assertEq(myContract.value(), 0);
}
```

## Fork Testing

```solidity
function test_OnFork() public {
    // Create fork
    uint256 forkId = vm.createFork("https://forno.celo.org");
    vm.selectFork(forkId);

    // Test against mainnet state
}
```

## Console Logging

```solidity
function test_WithLogs() public {
    console.log("Value:", myContract.value());
    console.log("Address:", address(myContract));
    console.logBytes32(keccak256("test"));
}
```
