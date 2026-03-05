# Reentrancy

## Hunt Targets

- external calls before critical state updates
- callback-enabled token interactions
- multi-contract call cycles

## Exploit Checks

- define reentry point and recursive call path
- prove state is inconsistent during reentry window
- prove value extraction or state corruption

## Reject Conditions

- guard is effective in actual path
- no meaningful state change can be abused
- only theoretical recursion with no impact

## Evidence Required

- call order and affected state variables
- minimal tx sequence demonstrating impact

