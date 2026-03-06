# Đoginals 

ℹ️ This is a fork/based on [apezord/ord-dogecoin](https://github.com/apezord/ord-dogecoin)

A minter and protocol for inscriptions on Dogecoin. 

## ⚠️⚠️⚠️ Important ⚠️⚠️⚠️

Use this wallet for inscribing only! Always inscribe from this wallet to a different address, e.g. one you created with Ordinals Wallet. This wallet is not meant for storing funds or inscriptions.

## Prerequisites

To use this, you'll need to use your console/terminal use Power Shell with Windows, install Node.js on your computer.

### Install NodeJS

Please head over to [https://nodejs.org/en/download](https://nodejs.org/en/download) and follow the installation instructions.

## Install Dogecoin Core 

Dogecoin Core version v1.14.6
## ⚠️⚠️⚠️ Important ⚠️⚠️⚠️
Update your dogcoin.conf file example.

```
rpcuser=<username>
rpcpassword=<password>
rpcport=22555
txindex=1
rpcallowip=127.0.0.1
server=1
```
## Install Doginals

- Download the repo by clicking <>code in the uper right of the GitHub and clicking Download ZIP                
- Extract the root folder to your rooot dir.

Using the terimnal install. 
```
cd <path to your doginals folder>
npm install
npm audit fix
``` 

After all dependencies are solved, you can configure the environment:

### Configure environment

`.env` and add your node information:

```
NODE_RPC_URL=http://127.0.0.1:22555
NODE_RPC_USER=<username>
NODE_RPC_PASS=<password>
TESTNET=false
FEE_PER_KB=30000000
```

You can get the current fee per kb from [here](https://mempool.jhoenicke.de/#DOGE,8h,weight).

### Using CLI

Import the private key to core ~/dogecoin-1.14.7/bin/ directory and you want to run the dogecoin-cli
run
./dogecoin-cli 
```
importprivkey <your_private_key> <optional_label> false
```
### Using QT
Settings>Options Wallets Enable coin controll.

Create a new wallet from shell.
```
node . wallet new
```
After creating your doginals wallet copy your private key from your doginals-main/.wallet.

Open DogecoinQT

File>Import Private Key

Paste private key and name wallet.

Fund wallet.

## Funding

Then send DOGE to the address displayed. Once sent, sync your wallet:

```
node . wallet sync
```

If you are minting a lot, you can split up your UTXOs:

```
node . wallet split <count>
```

When you are done minting, send the funds back:

```
node . wallet send <address> <optional amount>
```

## Minting

From file:

```
node . mint <address> <path>
```

From data:

```
node . mint <address> <content type> <hex data>
```

Examples:

```
node . mint D9UcJkdirVLY11UtF77WnC8peg6xRYsogu C:\doginals-main\ApeStractArtCollecton\DPAYSTONE.html
```

```
node . mint D9UcJkdirVLY11UtF77WnC8peg6xRYsogu "text/plain;charset=utf-8" 576f6f6621 
```

delegates

```
node . mint <address> "" ""  <delegate inscription ID>
```

**Note**: Please use a fresh wallet to mint to with nothing else in it until proper wallet for doginals support comes. You can get a paper wallet [here](https://www.fujicoin.org/wallet_generator?currency=Dogecoin).

## DRC-20
```
node . drc-20 deploy <address> <ticker> <total> <max mint>
```

```
node . drc-20 deploy D9pqzxiiUke5eodEzMmxZAxpFcbvwuM4Hg 'DFAT' 100000000 100000000
```


```
node . drc-20 mint <address> <ticker> <amount>
```

Examples: 

```
node . drc-20 mint D9pqzxiiUke5eodEzMmxZAxpFcbvwuM4Hg DCAC 100000000
```

## Viewing

Start the server:

```
node . server
```

And open your browser to:

```
http://localhost:3000/tx/15f3b73df7e5c072becb1d84191843ba080734805addfccb650929719080f62e
```

## Protocol

The doginals protocol allows any size data to be inscribed onto subwoofers.

An inscription is defined as a series of push datas:

```
"ord"
OP_1
"text/plain;charset=utf-8"
OP_0
"Woof!"
```

For doginals, we introduce a couple extensions. First, content may spread across multiple parts:

```
"ord"
OP_2
"text/plain;charset=utf-8"
OP_1
"Woof and "
OP_0
"woof woof!"
```

This content here would be concatenated as "Woof and woof woof!". This allows up to ~1500 bytes of data per transaction.

Second, P2SH is used to encode inscriptions.

There are no restrictions on what P2SH scripts may do as long as the redeem scripts start with inscription push datas.

And third, inscriptions are allowed to chain across transactions:

Transaction 1:

```
"ord"
OP_2
"text/plain;charset=utf-8"
OP_1
"Woof and "
```

Transaction 2

```
OP_0
"woof woof!"
```

With the restriction that each inscription part after the first must start with a number separator, and number separators must count down to 0.

This allows indexers to know how much data remains.

## FAQ

### I'm getting ECONNREFUSED errors when minting

There's a problem with the node connection. Your `dogecoin.conf` file should look something like:

```
rpcuser=ape
rpcpassword=zord
rpcport=22555
server=1
```

Make sure `port` is not set to the same number as `rpcport`. Also make sure `rpcauth` is not set.

Your `.env file` should look like:

```
NODE_RPC_URL=http://127.0.0.1:22555
NODE_RPC_USER=ape
NODE_RPC_PASS=zord
TESTNET=false
```

### I'm getting "insufficient priority" errors when minting

The miner fee is too low. You can increase it up by putting FEE_PER_KB=300000000 in your .env file or just wait it out. The default is 100000000 but spikes up when demand is high.

# Contributing

If you'd like to contribute or donate to our projects, please donate in Dogecoin. For active contributors its as easy as opening issues, and creating pull requests

If You would like to support with Donations, Send all Dogecoin to the following Contributors:

***You can donate to Apezord here:***

"handle": ***"Apezord"*** "at": [***"@apezord"***](https://x.com/apezord)

**"Đogecoin_address": "DNmrp12LfsVwy2Q2B5bvpQ1HU7zCAczYob"**

