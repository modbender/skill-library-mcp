import { expect } from "chai";
import { network } from "hardhat";

const { ethers, networkHelpers } = await network.connect();

describe("ExoskeletonWallet", function () {
  let core, wallet;
  let owner, alice, bob, treasury;

  const GENESIS_PRICE = ethers.parseEther("0.005");

  // We deploy a mock TBA implementation (just a dummy contract)
  // and mock the ERC-6551 registry behavior
  let mockImpl;

  async function deployFixture() {
    [owner, alice, bob, treasury] = await ethers.getSigners();

    core = await ethers.deployContract("ExoskeletonCore", [treasury.address]);

    // Use alice.address as a placeholder TBA implementation (just needs to be non-zero)
    mockImpl = alice.address;

    wallet = await ethers.deployContract("ExoskeletonWallet", [
      await core.getAddress(),
      mockImpl,
      31337n, // hardhat chain ID
    ]);

    // Whitelist alice for minting
    await core.setWhitelist(alice.address, true);
  }

  async function mintExoskeleton(signer, config) {
    config = config || ethers.toUtf8Bytes("default-config");
    const isWL = await core.whitelist(signer.address);
    const usedFree = await core.usedFreeMint(signer.address);
    const value = (isWL && !usedFree) ? 0n : await core.getMintPrice();
    await core.connect(signer).mint(config, { value });
    return await core.nextTokenId() - 1n;
  }

  describe("Deployment", function () {
    it("Should deploy with correct core and chain ID", async function () {
      await deployFixture();
      expect(await wallet.core()).to.equal(await core.getAddress());
      expect(await wallet.chainId()).to.equal(31337n);
      expect(await wallet.tbaImplementation()).to.equal(mockImpl);
    });

    it("Should reject zero core address", async function () {
      await deployFixture();
      await expect(wallet.setCoreContract(ethers.ZeroAddress))
        .to.be.revert(ethers);
    });

    it("Should allow owner to update implementation", async function () {
      await deployFixture();
      await wallet.setImplementation(bob.address);
      expect(await wallet.tbaImplementation()).to.equal(bob.address);
    });

    it("Should allow owner to update core", async function () {
      await deployFixture();
      await wallet.setCoreContract(bob.address);
      expect(await wallet.core()).to.equal(bob.address);
    });
  });

  describe("Wallet Activation", function () {
    beforeEach(async function () {
      await deployFixture();
    });

    it("Should reject activation from non-owner", async function () {
      await mintExoskeleton(alice);

      // Bob doesn't own token 1
      await expect(wallet.connect(bob).activateWallet(1))
        .to.be.revert(ethers);
    });

    it("Should reject activation when implementation not set", async function () {
      await wallet.setImplementation(ethers.ZeroAddress);
      await mintExoskeleton(alice);

      await expect(wallet.connect(alice).activateWallet(1))
        .to.be.revert(ethers);
    });

    it("Should revert getWalletAddress when registry not deployed (test network)", async function () {
      await mintExoskeleton(alice);

      // The canonical ERC-6551 registry doesn't exist on Hardhat's test network,
      // so this call reverts. On Base mainnet/testnet it would return a deterministic address.
      await expect(wallet.getWalletAddress(1)).to.be.revert(ethers);
    });

    it("Should report no wallet before activation", async function () {
      await mintExoskeleton(alice);
      expect(await wallet.hasWallet(1)).to.be.false;
    });

    it("Should reject getWalletAddress when no implementation", async function () {
      await wallet.setImplementation(ethers.ZeroAddress);
      await mintExoskeleton(alice);

      await expect(wallet.getWalletAddress(1))
        .to.be.revert(ethers);
    });

    it("Should only allow owner to update settings", async function () {
      await expect(wallet.connect(alice).setImplementation(bob.address))
        .to.be.revert(ethers);

      await expect(wallet.connect(alice).setCoreContract(bob.address))
        .to.be.revert(ethers);
    });
  });

  // Note: Full wallet activation (createAccount) requires the canonical ERC-6551
  // registry to be deployed, which isn't available on Hardhat's test network.
  // These tests will be validated on Base Sepolia where the registry exists.
  // The above tests verify all the access control and validation logic.
});
