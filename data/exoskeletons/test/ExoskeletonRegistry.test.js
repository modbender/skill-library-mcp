import { expect } from "chai";
import { network } from "hardhat";

const { ethers, networkHelpers } = await network.connect();

describe("ExoskeletonRegistry", function () {
  let core, registry;
  let owner, alice, bob, treasury;

  const GENESIS_PRICE = ethers.parseEther("0.005");

  async function deployFixture() {
    [owner, alice, bob, treasury] = await ethers.getSigners();

    core = await ethers.deployContract("ExoskeletonCore", [treasury.address]);
    registry = await ethers.deployContract("ExoskeletonRegistry", [
      await core.getAddress(),
    ]);

    // Whitelist alice & bob for minting
    await core.setWhitelist(alice.address, true);
    await core.setWhitelist(bob.address, true);
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
    it("Should deploy with correct core address", async function () {
      await deployFixture();
      expect(await registry.core()).to.equal(await core.getAddress());
    });

    it("Should allow owner to update core address", async function () {
      await deployFixture();
      await registry.setCoreContract(alice.address);
      expect(await registry.core()).to.equal(alice.address);
    });

    it("Should reject zero address for core", async function () {
      await deployFixture();
      await expect(registry.setCoreContract(ethers.ZeroAddress))
        .to.be.revert(ethers);
    });
  });

  describe("Name Lookup", function () {
    beforeEach(async function () {
      await deployFixture();
    });

    it("Should resolve name to token ID", async function () {
      await mintExoskeleton(alice);
      await core.connect(alice).setName(1, "Atlas");

      expect(await registry.resolveByName("Atlas")).to.equal(1);
    });

    it("Should return 0 for unknown name", async function () {
      expect(await registry.resolveByName("nonexistent")).to.equal(0);
    });

    it("Should get name by token ID", async function () {
      await mintExoskeleton(alice);
      await core.connect(alice).setName(1, "Spartan");

      expect(await registry.getName(1)).to.equal("Spartan");
    });

    it("Should return empty string for unnamed token", async function () {
      await mintExoskeleton(alice);
      expect(await registry.getName(1)).to.equal("");
    });
  });

  describe("Profile", function () {
    beforeEach(async function () {
      await deployFixture();
    });

    it("Should return full profile for a token", async function () {
      await mintExoskeleton(alice);
      await core.connect(alice).setName(1, "Vanguard");
      await core.connect(alice).setBio(1, "First line agent");

      const profile = await registry.getProfile(1);
      expect(profile.name).to.equal("Vanguard");
      expect(profile.bio).to.equal("First line agent");
      expect(profile.genesis).to.be.true;
      expect(profile.owner).to.equal(alice.address);
      expect(profile.reputationScore).to.be.greaterThanOrEqual(0n);
    });

    it("Should include reputation data in profile", async function () {
      await mintExoskeleton(alice);

      // Send a message
      const payload = ethers.toUtf8Bytes("hello");
      await core.connect(alice).sendMessage(1, 0, ethers.ZeroHash, 0, payload);

      // Store some data
      const key = ethers.keccak256(ethers.toUtf8Bytes("test"));
      await core.connect(alice).setData(1, key, ethers.toUtf8Bytes("val"));

      const profile = await registry.getProfile(1);
      expect(profile.messagesSent).to.equal(1);
      expect(profile.storageWrites).to.equal(1);
    });
  });

  describe("Module Discovery", function () {
    beforeEach(async function () {
      await deployFixture();
    });

    it("Should track a module", async function () {
      const modName = ethers.keccak256(ethers.toUtf8Bytes("comms-v2"));
      await registry.trackModule(modName, "Advanced Comms");

      expect(await registry.isTracked(modName)).to.be.true;
      expect(await registry.moduleLabels(modName)).to.equal("Advanced Comms");
      expect(await registry.getTrackedModuleCount()).to.equal(1);
    });

    it("Should reject duplicate module tracking", async function () {
      const modName = ethers.keccak256(ethers.toUtf8Bytes("test-mod"));
      await registry.trackModule(modName, "Test Module");

      await expect(registry.trackModule(modName, "Test Module"))
        .to.be.revert(ethers);
    });

    it("Should untrack a module", async function () {
      const mod1 = ethers.keccak256(ethers.toUtf8Bytes("mod-1"));
      const mod2 = ethers.keccak256(ethers.toUtf8Bytes("mod-2"));
      await registry.trackModule(mod1, "Module 1");
      await registry.trackModule(mod2, "Module 2");

      await registry.untrackModule(mod1);

      expect(await registry.isTracked(mod1)).to.be.false;
      expect(await registry.getTrackedModuleCount()).to.equal(1);
    });

    it("Should get all tracked modules", async function () {
      const mod1 = ethers.keccak256(ethers.toUtf8Bytes("mod-a"));
      const mod2 = ethers.keccak256(ethers.toUtf8Bytes("mod-b"));
      const mod3 = ethers.keccak256(ethers.toUtf8Bytes("mod-c"));

      await registry.trackModule(mod1, "Module A");
      await registry.trackModule(mod2, "Module B");
      await registry.trackModule(mod3, "Module C");

      const modules = await registry.getTrackedModules();
      expect(modules.length).to.equal(3);
    });

    it("Should find active modules for a token", async function () {
      await mintExoskeleton(alice);

      // Register and activate a module on Core
      const modName = ethers.keccak256(ethers.toUtf8Bytes("tracker"));
      await core.registerModule(modName, alice.address, false, 0);
      await core.connect(alice).activateModule(1, modName);

      // Track it in Registry
      await registry.trackModule(modName, "Tracker Module");

      const active = await registry.getActiveModulesForToken(1);
      expect(active.length).to.equal(1);
      expect(active[0]).to.equal(modName);
    });

    it("Should return empty for token with no active tracked modules", async function () {
      await mintExoskeleton(alice);

      const modName = ethers.keccak256(ethers.toUtf8Bytes("unused"));
      await registry.trackModule(modName, "Unused Module");

      const active = await registry.getActiveModulesForToken(1);
      expect(active.length).to.equal(0);
    });

    it("Should only allow owner to track/untrack", async function () {
      const modName = ethers.keccak256(ethers.toUtf8Bytes("test"));

      await expect(registry.connect(alice).trackModule(modName, "Test"))
        .to.be.revert(ethers);
    });
  });

  describe("Network Statistics", function () {
    beforeEach(async function () {
      await deployFixture();
    });

    it("Should report zero stats before any activity", async function () {
      const stats = await registry.getNetworkStats();
      expect(stats.totalMinted).to.equal(0);
      expect(stats.totalMessages).to.equal(0);
    });

    it("Should track minted count", async function () {
      await mintExoskeleton(alice);
      await mintExoskeleton(bob);

      const stats = await registry.getNetworkStats();
      expect(stats.totalMinted).to.equal(2);
    });

    it("Should track message count", async function () {
      await mintExoskeleton(alice);
      const payload = ethers.toUtf8Bytes("gm");
      await core.connect(alice).sendMessage(1, 0, ethers.ZeroHash, 0, payload);
      await core.connect(alice).sendMessage(1, 0, ethers.ZeroHash, 0, payload);

      const stats = await registry.getNetworkStats();
      expect(stats.totalMessages).to.equal(2);
    });
  });

  describe("Batch Queries", function () {
    beforeEach(async function () {
      await deployFixture();
    });

    it("Should get reputation scores in batch", async function () {
      await mintExoskeleton(alice);
      await mintExoskeleton(bob);

      await networkHelpers.mine(10);

      const result = await registry.getReputationBatch(1, 2);
      expect(result.tokenIds.length).to.equal(2);
      expect(result.scores.length).to.equal(2);
      expect(result.tokenIds[0]).to.equal(1);
      expect(result.tokenIds[1]).to.equal(2);
      expect(result.scores[0]).to.be.greaterThan(0n);
    });

    it("Should handle batch query past max token ID", async function () {
      await mintExoskeleton(alice);

      const result = await registry.getReputationBatch(1, 100);
      expect(result.tokenIds.length).to.equal(1);
    });

    it("Should return empty for invalid start ID", async function () {
      const result = await registry.getReputationBatch(999, 10);
      expect(result.tokenIds.length).to.equal(0);
    });

    it("Should get profiles in batch", async function () {
      await mintExoskeleton(alice);
      await mintExoskeleton(bob);
      await core.connect(alice).setName(1, "Agent-A");
      await core.connect(bob).setName(2, "Agent-B");

      const result = await registry.getProfileBatch([1, 2]);
      expect(result.names[0]).to.equal("Agent-A");
      expect(result.names[1]).to.equal("Agent-B");
      expect(result.genesisFlags[0]).to.be.true;
      expect(result.genesisFlags[1]).to.be.true;
    });
  });
});
