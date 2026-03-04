# Clubs & Power Reference

## Available Clubs

Driver, 3-Wood, 5-Wood, 3-Iron through 9-Iron, PW, SW, Putter.

The `look` command shows your stock yardages at full power (carry and total for each club). These reflect your current skill level.

## Power Math

Distance scales linearly with power:

- `carry = stockCarry * (power / 100)`
- `total = stockTotal * (power / 100)`

To hit a specific distance: `power = (desiredDistance / stockTotal) * 100`

Example: You need 150y total. With a 7-iron (180y stock total): `power = 150 / 180 * 100 = 83%`.

## Shot Command

```
node "{baseDir}/dist/cli.js" hit --club <club-name> --aim <degrees> --power <percent>
```

- `--club`: One of `driver`, `3-wood`, `5-wood`, `3-iron` through `9-iron`, `pw`, `sw`, `putter`
- `--aim`: Degrees 0-360
- `--power`: 1-100 (percentage of full power)
