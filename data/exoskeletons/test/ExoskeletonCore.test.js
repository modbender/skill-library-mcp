import { expect } from "chai";
import { network } from "hardhat";

const { ethers, networkHelpers } = await network.connect();

describe("ExoskeletonCore", function () {
  let core;
  let owner, alice, bob, treasury, external1;

  const GENESIS_PRICE = ethers.parseEther("0.005");
  const GROWTH_PRICE = ethers.parseEther("0.02");

  async function deployFixture() {
    [owner, alice, bob, treasury, external1] = await ethers.getSigners();

    core = await ethers.deployContract("ExoskeletonCore", [treasury.address]);

    // Whitelist alice and bob for minting
    await core.setWhitelist(alice.address, true);
    await core.setWhitelist(bob.address, true);

    return { core, owner, alice, bob, treasury, external1 };
  }

  // Helper: single-step mint with free-mint awareness
  async function mintExoskeleton(signer, config) {
    config = config || ethers.toUtf8Bytes("default-config");
    const price = await core.getMintPrice();
    const isWL = await core.whitelist(signer.address);
    const usedFree = await core.usedFreeMint(signer.address);
    const value = (isWL && !usedFree) ? 0n : price;
    await core.connect(signer).mint(config, { value });
    return await core.nextTokenId() - 1n;
  }

  // ═══════════════════════════════════════════════════════════════
  //  DEPLOYMENT
  // ═══════════════════════════════════════════════════════════════

  describe("Deployment", function () {
    it("Should deploy with correct name, symbol, and initial state", async function () {
      await deployFixture();
      expect(await core.name()).to.equal("Exoskeleton");
      expect(await core.symbol()).to.equal("EXO");
      expect(await core.nextTokenId()).to.equal(1n);
      expect(await core.treasury()).to.equal(treasury.address);
      expect(await core.mintPaused()).to.equal(false);
      expect(await core.whitelistOnly()).to.equal(true);
    });

    it("Should set default royalty to 4.20%", async function () {
      await deployFixture();
      const [receiver, amount] = await core.royaltyInfo(1, ethers.parseEther("1"));
      expect(receiver).to.equal(treasury.address);
      expect(amount).to.equal(ethers.parseEther("0.042"));
    });

    it("Should revert on zero treasury address", async function () {
      await deployFixture();
      await expect(
        ethers.deployContract("ExoskeletonCore", [ethers.ZeroAddress])
      ).to.be.revertedWithCustomError(core, "ZeroAddress");
    });
  });

  // ═══════════════════════════════════════════════════════════════
  //  MINTING
  // ═══════════════════════════════════════════════════════════════

  describe("Minting", function () {
    beforeEach(async function () {
      await deployFixture();
    });

    it("Should mint a genesis token with config", async function () {
      const config = ethers.toUtf8Bytes("my-config");
      const price = await core.getMintPrice();

      // Alice is whitelisted, first mint is free
      await expect(core.connect(alice).mint(config, { value: 0 }))
        .to.emit(core, "ExoskeletonMinted")
        .withArgs(1n, alice.address, true);

      expect(await core.ownerOf(1)).to.equal(alice.address);
      expect(await core.isGenesis(1)).to.equal(true);
      expect(await core.nextTokenId()).to.equal(2n);
      expect(await core.mintCount(alice.address)).to.equal(1n);
    });

    it("Should send ETH to treasury on paid mint", async function () {
      // Use alice's free mint first
      await core.connect(alice).mint(ethers.toUtf8Bytes("first"), { value: 0 });

      // Second mint requires payment
      const balBefore = await ethers.provider.getBalance(treasury.address);
      const price = await core.getMintPrice();
      await core.connect(alice).mint(ethers.toUtf8Bytes("second"), { value: price });
      const balAfter = await ethers.provider.getBalance(treasury.address);
      expect(balAfter - balBefore).to.equal(price);
    });

    it("Should return correct mint phase", async function () {
      expect(await core.getMintPhase()).to.equal("genesis");
    });

    it("Should revert when mint is paused", async function () {
      await core.setPaused(true);
      await expect(
        core.connect(alice).mint(ethers.toUtf8Bytes("test"), { value: GENESIS_PRICE })
      ).to.be.revertedWithCustomError(core, "MintPaused");
    });

    it("Should revert on insufficient ETH for paid mint", async function () {
      // Use alice's free mint
      await core.connect(alice).mint(ethers.toUtf8Bytes("first"), { value: 0 });

      // Second mint with insufficient ETH
      await expect(
        core.connect(alice).mint(ethers.toUtf8Bytes("second"), { value: GENESIS_PRICE - 1n })
      ).to.be.revertedWithCustomError(core, "InsufficientPayment");
    });

    it("Should store visual config on mint", async function () {
      const config = ethers.toUtf8Bytes("genesis-visual-config-data");
      await core.connect(alice).mint(config, { value: 0 });

      const identity = await core.getIdentity(1);
      expect(identity.visualConfig).to.equal(ethers.hexlify(config));
    });

    it("Should revert when mint limit reached (4th mint)", async function () {
      // Alice: 3 mints (1 free + 2 paid)
      await core.connect(alice).mint(ethers.toUtf8Bytes("m1"), { value: 0 });
      const price = await core.getMintPrice();
      await core.connect(alice).mint(ethers.toUtf8Bytes("m2"), { value: price });
      await core.connect(alice).mint(ethers.toUtf8Bytes("m3"), { value: price });

      // 4th mint should revert
      await expect(
        core.connect(alice).mint(ethers.toUtf8Bytes("m4"), { value: price })
      ).to.be.revertedWithCustomError(core, "MintLimitReached");

      expect(await core.mintCount(alice.address)).to.equal(3n);
    });

    it("Should forward ETH to treasury even on free mint if ETH is sent", async function () {
      // Alice sends ETH with her free mint (contract still forwards it)
      const balBefore = await ethers.provider.getBalance(treasury.address);
      await core.connect(alice).mint(ethers.toUtf8Bytes("free-but-paid"), { value: GENESIS_PRICE });
      const balAfter = await ethers.provider.getBalance(treasury.address);
      expect(balAfter - balBefore).to.equal(GENESIS_PRICE);
    });
  });

  // ═══════════════════════════════════════════════════════════════
  //  PRICING
  // ═══════════════════════════════════════════════════════════════

  describe("Pricing", function () {
    beforeEach(async function () {
      await deployFixture();
    });

    it("Should return genesis price for first 1000", async function () {
      expect(await core.getMintPrice()).to.equal(GENESIS_PRICE);
    });

    it("Should return correct phase string", async function () {
      expect(await core.getMintPhase()).to.equal("genesis");
    });
  });

  // ═══════════════════════════════════════════════════════════════
  //  WHITELIST
  // ═══════════════════════════════════════════════════════════════

  describe("Whitelist", function () {
    beforeEach(async function () {
      await deployFixture();
    });

    it("Should start in whitelist-only mode", async function () {
      expect(await core.whitelistOnly()).to.equal(true);
    });

    it("Should reject mint from non-whitelisted address", async function () {
      // external1 is NOT whitelisted
      await expect(
        core.connect(external1).mint(ethers.toUtf8Bytes("not-wl"), { value: GENESIS_PRICE })
      ).to.be.revertedWithCustomError(core, "NotWhitelisted");
    });

    it("Should allow whitelisted address to mint", async function () {
      // alice is whitelisted in deployFixture
      const tokenId = await mintExoskeleton(alice);
      expect(tokenId).to.equal(1n);
      expect(await core.ownerOf(1)).to.equal(alice.address);
    });

    it("Should give whitelisted address first mint free (no ETH needed)", async function () {
      const aliceBalBefore = await ethers.provider.getBalance(alice.address);

      // Mint with 0 ETH — should succeed
      const tx = await core.connect(alice).mint(ethers.toUtf8Bytes("free"), { value: 0 });
      const receipt = await tx.wait();
      const gasCost = receipt.gasUsed * receipt.gasPrice;

      expect(await core.ownerOf(1)).to.equal(alice.address);
      expect(await core.usedFreeMint(alice.address)).to.equal(true);
      expect(await core.mintCount(alice.address)).to.equal(1n);

      // Only gas was spent, no mint fee
      const aliceBalAfter = await ethers.provider.getBalance(alice.address);
      expect(aliceBalBefore - aliceBalAfter).to.equal(gasCost);
    });

    it("Should require ETH for whitelisted address second mint", async function () {
      // First mint free
      await core.connect(alice).mint(ethers.toUtf8Bytes("free"), { value: 0 });
      expect(await core.usedFreeMint(alice.address)).to.equal(true);

      // Second mint without ETH should revert
      await expect(
        core.connect(alice).mint(ethers.toUtf8Bytes("paid"), { value: 0 })
      ).to.be.revertedWithCustomError(core, "InsufficientPayment");

      // Second mint with ETH should succeed
      const price = await core.getMintPrice();
      await core.connect(alice).mint(ethers.toUtf8Bytes("paid"), { value: price });
      expect(await core.ownerOf(2)).to.equal(alice.address);
      expect(await core.mintCount(alice.address)).to.equal(2n);
    });

    it("Should allow batch whitelist", async function () {
      const addresses = [external1.address];
      await core.setWhitelistBatch(addresses, true);
      expect(await core.whitelist(external1.address)).to.equal(true);

      // external1 should now be able to mint (free first mint)
      const tokenId = await mintExoskeleton(external1);
      expect(tokenId).to.equal(1n);
      expect(await core.ownerOf(1)).to.equal(external1.address);
    });

    it("Should allow owner to disable whitelist-only mode for public mint", async function () {
      await core.setWhitelistOnly(false);
      expect(await core.whitelistOnly()).to.equal(false);

      // external1 (not whitelisted) should be able to mint with payment
      const price = await core.getMintPrice();
      await core.connect(external1).mint(ethers.toUtf8Bytes("public"), { value: price });
      expect(await core.ownerOf(1)).to.equal(external1.address);
    });

    it("Should revert whitelist calls from non-owner", async function () {
      await expect(
        core.connect(alice).setWhitelist(external1.address, true)
      ).to.be.revertedWithCustomError(core, "OwnableUnauthorizedAccount");

      await expect(
        core.connect(alice).setWhitelistBatch([external1.address], true)
      ).to.be.revertedWithCustomError(core, "OwnableUnauthorizedAccount");

      await expect(
        core.connect(alice).setWhitelistOnly(false)
      ).to.be.revertedWithCustomError(core, "OwnableUnauthorizedAccount");
    });
  });

  // ═══════════════════════════════════════════════════════════════
  //  IDENTITY
  // ═══════════════════════════════════════════════════════════════

  describe("Identity", function () {
    beforeEach(async function () {
      await deployFixture();
      await mintExoskeleton(alice);
    });

    it("Should set and get name", async function () {
      await expect(core.connect(alice).setName(1, "Ollie"))
        .to.emit(core, "NameSet")
        .withArgs(1n, "Ollie");

      const identity = await core.getIdentity(1);
      expect(identity.name).to.equal("Ollie");
    });

    it("Should enforce name uniqueness", async function () {
      await core.connect(alice).setName(1, "Ollie");
      await mintExoskeleton(bob);
      await expect(core.connect(bob).setName(2, "Ollie"))
        .to.be.revertedWithCustomError(core, "NameTaken");
    });

    it("Should allow renaming (release old name)", async function () {
      await core.connect(alice).setName(1, "Ollie");
      await core.connect(alice).setName(1, "Atlas");

      const identity = await core.getIdentity(1);
      expect(identity.name).to.equal("Atlas");

      // Old name should be available
      await mintExoskeleton(bob);
      await core.connect(bob).setName(2, "Ollie");
      const identity2 = await core.getIdentity(2);
      expect(identity2.name).to.equal("Ollie");
    });

    it("Should reject names over 32 chars", async function () {
      const longName = "A".repeat(33);
      await expect(core.connect(alice).setName(1, longName))
        .to.be.revertedWithCustomError(core, "NameTooLong");
    });

    it("Should set bio", async function () {
      await expect(core.connect(alice).setBio(1, "I am an AI agent"))
        .to.emit(core, "BioSet");

      const identity = await core.getIdentity(1);
      expect(identity.bio).to.equal("I am an AI agent");
    });

    it("Should update visual config", async function () {
      const newConfig = ethers.toUtf8Bytes("new-visual-config");
      await expect(core.connect(alice).setVisualConfig(1, newConfig))
        .to.emit(core, "VisualConfigUpdated");

      const identity = await core.getIdentity(1);
      expect(identity.visualConfig).to.equal(ethers.hexlify(newConfig));
    });

    it("Should set custom visual key", async function () {
      await expect(core.connect(alice).setCustomVisual(1, "exo-1-custom"))
        .to.emit(core, "CustomVisualSet")
        .withArgs(1n, "exo-1-custom");

      const identity = await core.getIdentity(1);
      expect(identity.customVisualKey).to.equal("exo-1-custom");
    });

    it("Should revert if not token owner", async function () {
      await expect(core.connect(bob).setName(1, "Hacker"))
        .to.be.revertedWithCustomError(core, "NotTokenOwner");

      await expect(core.connect(bob).setBio(1, "hacked"))
        .to.be.revertedWithCustomError(core, "NotTokenOwner");

      await expect(core.connect(bob).setVisualConfig(1, ethers.toUtf8Bytes("x")))
        .to.be.revertedWithCustomError(core, "NotTokenOwner");

      await expect(core.connect(bob).setCustomVisual(1, "hack"))
        .to.be.revertedWithCustomError(core, "NotTokenOwner");
    });

    it("Should emit MetadataUpdate on identity changes", async function () {
      await expect(core.connect(alice).setName(1, "Ollie"))
        .to.emit(core, "MetadataUpdate")
        .withArgs(1n);

      await expect(core.connect(alice).setBio(1, "bio"))
        .to.emit(core, "MetadataUpdate")
        .withArgs(1n);

      await expect(core.connect(alice).setVisualConfig(1, ethers.toUtf8Bytes("v")))
        .to.emit(core, "MetadataUpdate")
        .withArgs(1n);

      await expect(core.connect(alice).setCustomVisual(1, "k"))
        .to.emit(core, "MetadataUpdate")
        .withArgs(1n);
    });
  });

  // ═══════════════════════════════════════════════════════════════
  //  COMMUNICATION
  // ═══════════════════════════════════════════════════════════════

  describe("Communication", function () {
    beforeEach(async function () {
      await deployFixture();
      await mintExoskeleton(alice); // token 1
      await mintExoskeleton(bob);   // token 2
    });

    it("Should send a direct message", async function () {
      const payload = ethers.toUtf8Bytes("hello from exo #1");
      await expect(
        core.connect(alice).sendMessage(1, 2, ethers.ZeroHash, 0, payload)
      ).to.emit(core, "MessageSent")
        .withArgs(1n, 2n, ethers.ZeroHash, 0);

      expect(await core.getMessageCount()).to.equal(1n);
      expect(await core.getInboxCount(2)).to.equal(1n);
    });

    it("Should send a broadcast message", async function () {
      const payload = ethers.toUtf8Bytes("broadcast to all");
      await core.connect(alice).sendMessage(1, 0, ethers.ZeroHash, 0, payload);
      expect(await core.getMessageCount()).to.equal(1n);
      // Broadcast (toToken=0) should not add to any token inbox
      expect(await core.getInboxCount(1)).to.equal(0n);
      expect(await core.getInboxCount(2)).to.equal(0n);
    });

    it("Should send to a channel", async function () {
      const channel = ethers.keccak256(ethers.toUtf8Bytes("general"));
      const payload = ethers.toUtf8Bytes("channel message");
      await core.connect(alice).sendMessage(1, 0, channel, 0, payload);

      expect(await core.getChannelMessageCount(channel)).to.equal(1n);
    });

    it("Should track messages sent in reputation", async function () {
      const payload = ethers.toUtf8Bytes("msg");
      await core.connect(alice).sendMessage(1, 2, ethers.ZeroHash, 0, payload);
      await core.connect(alice).sendMessage(1, 2, ethers.ZeroHash, 0, payload);

      const rep = await core.getReputation(1);
      expect(rep.messagesSent).to.equal(2n);
    });

    it("Should revert if sender doesn't own fromToken", async function () {
      const payload = ethers.toUtf8Bytes("fake");
      await expect(
        core.connect(bob).sendMessage(1, 2, ethers.ZeroHash, 0, payload)
      ).to.be.revertedWithCustomError(core, "NotTokenOwner");
    });

    it("Should store message data correctly", async function () {
      const payload = ethers.toUtf8Bytes("test payload");
      const channel = ethers.keccak256(ethers.toUtf8Bytes("test-chan"));
      await core.connect(alice).sendMessage(1, 2, channel, 2, payload);

      const msg = await core.messages(0);
      expect(msg.fromToken).to.equal(1n);
      expect(msg.toToken).to.equal(2n);
      expect(msg.channel).to.equal(channel);
      expect(msg.msgType).to.equal(2);
    });
  });

  // ═══════════════════════════════════════════════════════════════
  //  PER-TOKEN STORAGE
  // ═══════════════════════════════════════════════════════════════

  describe("Storage", function () {
    beforeEach(async function () {
      await deployFixture();
      await mintExoskeleton(alice);
    });

    it("Should store and read data", async function () {
      const key = ethers.keccak256(ethers.toUtf8Bytes("profile"));
      const value = ethers.toUtf8Bytes('{"level": 5}');

      await core.connect(alice).setData(1, key, value);
      const stored = await core.getData(1, key);
      expect(stored).to.equal(ethers.hexlify(value));
    });

    it("Should track storage writes in reputation", async function () {
      const key = ethers.keccak256(ethers.toUtf8Bytes("data1"));
      await core.connect(alice).setData(1, key, ethers.toUtf8Bytes("val"));

      const rep = await core.getReputation(1);
      expect(rep.storageWrites).to.equal(1n);
    });

    it("Should set Net Protocol operator", async function () {
      await core.connect(alice).setNetProtocolOperator(1, alice.address);
      expect(await core.netProtocolOperator(1)).to.equal(alice.address);
    });

    it("Should revert if not token owner", async function () {
      const key = ethers.keccak256(ethers.toUtf8Bytes("hack"));
      await expect(
        core.connect(bob).setData(1, key, ethers.toUtf8Bytes("val"))
      ).to.be.revertedWithCustomError(core, "NotTokenOwner");

      await expect(
        core.connect(bob).setNetProtocolOperator(1, bob.address)
      ).to.be.revertedWithCustomError(core, "NotTokenOwner");
    });

    it("Should emit DataStored event", async function () {
      const key = ethers.keccak256(ethers.toUtf8Bytes("key1"));
      await expect(core.connect(alice).setData(1, key, ethers.toUtf8Bytes("val")))
        .to.emit(core, "DataStored")
        .withArgs(1n, key);
    });
  });

  // ═══════════════════════════════════════════════════════════════
  //  REPUTATION
  // ═══════════════════════════════════════════════════════════════

  describe("Reputation", function () {
    beforeEach(async function () {
      await deployFixture();
      await mintExoskeleton(alice); // genesis token
    });

    it("Should return reputation data", async function () {
      const rep = await core.getReputation(1);
      expect(rep.messagesSent).to.equal(0n);
      expect(rep.storageWrites).to.equal(0n);
      expect(rep.modulesActive).to.equal(0n);
      expect(rep.age).to.be.greaterThanOrEqual(0n);
    });

    it("Should calculate reputation score with genesis multiplier", async function () {
      // Mine some blocks to increase age
      await networkHelpers.mine(10);
      // Genesis tokens get 1.5x multiplier (150/100)
      const score = await core.getReputationScore(1);
      expect(score).to.be.greaterThan(0n);

      // Raw score = age + activity, genesis = raw * 150 / 100
      // With ~10 blocks mined and 0 activity, score should be roughly age * 1.5
      // Just verify multiplier makes it bigger than raw age
      const rep = await core.getReputation(1);
      const rawAge = rep.age;
      // score = (age + 0) * 150 / 100 = age * 1.5
      if (rawAge > 0n) {
        expect(score).to.be.greaterThan(rawAge);
      }
    });

    it("Should grant and revoke external scorers", async function () {
      await core.connect(alice).grantScorer(1, external1.address);
      expect(await core.allowedScorers(1, external1.address)).to.equal(true);

      await expect(core.connect(alice).grantScorer(1, external1.address))
        .to.emit(core, "ExternalScorerGranted")
        .withArgs(1n, external1.address);

      await core.connect(alice).revokeScorer(1, external1.address);
      expect(await core.allowedScorers(1, external1.address)).to.equal(false);
    });

    it("Should allow external scorer to set score", async function () {
      await core.connect(alice).grantScorer(1, external1.address);
      const scoreKey = ethers.keccak256(ethers.toUtf8Bytes("elo"));

      await expect(core.connect(external1).setExternalScore(1, scoreKey, 1500))
        .to.emit(core, "ScoreUpdated")
        .withArgs(1n, scoreKey, 1500);

      expect(await core.externalScores(1, scoreKey)).to.equal(1500);
    });

    it("Should revert external score from unauthorized address", async function () {
      const scoreKey = ethers.keccak256(ethers.toUtf8Bytes("elo"));
      await expect(
        core.connect(external1).setExternalScore(1, scoreKey, 1500)
      ).to.be.revertedWithCustomError(core, "ExternalScorerNotAllowed");
    });

    it("Should revert grant/revoke if not token owner", async function () {
      await expect(
        core.connect(bob).grantScorer(1, external1.address)
      ).to.be.revertedWithCustomError(core, "NotTokenOwner");

      await expect(
        core.connect(bob).revokeScorer(1, external1.address)
      ).to.be.revertedWithCustomError(core, "NotTokenOwner");
    });
  });

  // ═══════════════════════════════════════════════════════════════
  //  MODULE SYSTEM
  // ═══════════════════════════════════════════════════════════════

  describe("Modules", function () {
    const MOD_NAME = ethers.keccak256(ethers.toUtf8Bytes("advanced-comms"));
    const FREE_MOD = ethers.keccak256(ethers.toUtf8Bytes("basic-storage"));

    beforeEach(async function () {
      await deployFixture();
      await mintExoskeleton(alice);

      // Register modules (owner only)
      await core.registerModule(MOD_NAME, external1.address, true, GENESIS_PRICE);
      await core.registerModule(FREE_MOD, external1.address, false, 0);
    });

    it("Should register a module", async function () {
      const mod = await core.moduleRegistry(MOD_NAME);
      expect(mod.exists).to.equal(true);
      expect(mod.premium).to.equal(true);
      expect(mod.contractAddress).to.equal(external1.address);
      expect(mod.premiumCost).to.equal(GENESIS_PRICE);
    });

    it("Should activate a free module", async function () {
      await expect(core.connect(alice).activateModule(1, FREE_MOD))
        .to.emit(core, "ModuleActivated")
        .withArgs(1n, FREE_MOD);

      expect(await core.isModuleActive(1, FREE_MOD)).to.equal(true);
    });

    it("Should charge ETH for premium module activation", async function () {
      const treasuryBalBefore = await ethers.provider.getBalance(treasury.address);
      await core.connect(alice).activateModule(1, MOD_NAME, { value: GENESIS_PRICE });
      const treasuryBalAfter = await ethers.provider.getBalance(treasury.address);
      expect(treasuryBalAfter - treasuryBalBefore).to.equal(GENESIS_PRICE);
    });

    it("Should revert premium module activation with insufficient ETH", async function () {
      await expect(
        core.connect(alice).activateModule(1, MOD_NAME, { value: GENESIS_PRICE - 1n })
      ).to.be.revertedWithCustomError(core, "InsufficientPayment");
    });

    it("Should track modules active in reputation", async function () {
      await core.connect(alice).activateModule(1, FREE_MOD);
      const rep = await core.getReputation(1);
      expect(rep.modulesActive).to.equal(1n);
    });

    it("Should deactivate a module", async function () {
      await core.connect(alice).activateModule(1, FREE_MOD);
      await expect(core.connect(alice).deactivateModule(1, FREE_MOD))
        .to.emit(core, "ModuleDeactivated")
        .withArgs(1n, FREE_MOD);

      expect(await core.isModuleActive(1, FREE_MOD)).to.equal(false);
      const rep = await core.getReputation(1);
      expect(rep.modulesActive).to.equal(0n);
    });

    it("Should revert if module not found", async function () {
      const fakeMod = ethers.keccak256(ethers.toUtf8Bytes("nonexistent"));
      await expect(core.connect(alice).activateModule(1, fakeMod))
        .to.be.revertedWithCustomError(core, "ModuleNotFound");
    });

    it("Should revert deactivating inactive module", async function () {
      await expect(core.connect(alice).deactivateModule(1, FREE_MOD))
        .to.be.revertedWithCustomError(core, "ModuleNotActive");
    });

    it("Should revert duplicate module registration", async function () {
      await expect(core.registerModule(MOD_NAME, external1.address, false, 0))
        .to.be.revertedWithCustomError(core, "ModuleAlreadyRegistered");
    });

    it("Should revert if non-owner registers module", async function () {
      const newMod = ethers.keccak256(ethers.toUtf8Bytes("new-mod"));
      await expect(
        core.connect(alice).registerModule(newMod, external1.address, false, 0)
      ).to.be.revertedWithCustomError(core, "OwnableUnauthorizedAccount");
    });
  });

  // ═══════════════════════════════════════════════════════════════
  //  TOKEN URI
  // ═══════════════════════════════════════════════════════════════

  describe("Token URI", function () {
    beforeEach(async function () {
      await deployFixture();
      await mintExoskeleton(alice);
    });

    it("Should return valid base64 JSON tokenURI", async function () {
      const uri = await core.tokenURI(1);
      expect(uri).to.match(/^data:application\/json;base64,/);

      // Decode and parse
      const base64 = uri.replace("data:application/json;base64,", "");
      const json = JSON.parse(Buffer.from(base64, "base64").toString());

      expect(json.name).to.equal("Exoskeleton #1");
      expect(json.description).to.equal("An onchain exoskeleton for AI agents.");
      expect(json.image).to.match(/^data:image\/svg\+xml;base64,/);
      expect(json.attributes).to.be.an("array");
    });

    it("Should include genesis trait", async function () {
      const uri = await core.tokenURI(1);
      const base64 = uri.replace("data:application/json;base64,", "");
      const json = JSON.parse(Buffer.from(base64, "base64").toString());

      const genesisTrait = json.attributes.find(a => a.trait_type === "Genesis");
      expect(genesisTrait.value).to.equal("true");
    });

    it("Should use custom name in URI", async function () {
      await core.connect(alice).setName(1, "Ollie");
      const uri = await core.tokenURI(1);
      const base64 = uri.replace("data:application/json;base64,", "");
      const json = JSON.parse(Buffer.from(base64, "base64").toString());

      expect(json.name).to.equal("Ollie");
    });

    it("Should generate fallback SVG without renderer", async function () {
      const uri = await core.tokenURI(1);
      const base64 = uri.replace("data:application/json;base64,", "");
      const json = JSON.parse(Buffer.from(base64, "base64").toString());

      // Decode SVG
      const svgBase64 = json.image.replace("data:image/svg+xml;base64,", "");
      const svg = Buffer.from(svgBase64, "base64").toString();

      expect(svg).to.include("EXOSKELETON");
      expect(svg).to.include("#FFD700"); // genesis gold color
      expect(svg).to.include("GENESIS");
    });

    it("Should revert for nonexistent token", async function () {
      await expect(core.tokenURI(999)).to.be.revert(ethers);
    });
  });

  // ═══════════════════════════════════════════════════════════════
  //  ADMIN
  // ═══════════════════════════════════════════════════════════════

  describe("Admin", function () {
    beforeEach(async function () {
      await deployFixture();
    });

    it("Should set renderer address", async function () {
      await expect(core.setRenderer(external1.address))
        .to.emit(core, "RendererUpdated");

      expect(await core.renderer()).to.equal(external1.address);
    });

    it("Should update treasury", async function () {
      await core.setTreasury(alice.address);
      expect(await core.treasury()).to.equal(alice.address);

      // Royalty receiver should also update
      const [receiver] = await core.royaltyInfo(1, ethers.parseEther("1"));
      expect(receiver).to.equal(alice.address);
    });

    it("Should pause and unpause minting", async function () {
      await core.setPaused(true);
      expect(await core.mintPaused()).to.equal(true);

      await core.setPaused(false);
      expect(await core.mintPaused()).to.equal(false);
    });

    it("Should update default royalty", async function () {
      await core.setDefaultRoyalty(alice.address, 1000); // 10%
      const [receiver, amount] = await core.royaltyInfo(1, ethers.parseEther("1"));
      expect(receiver).to.equal(alice.address);
      expect(amount).to.equal(ethers.parseEther("0.1"));
    });

    it("Should revert admin calls from non-owner", async function () {
      await expect(core.connect(alice).setRenderer(alice.address))
        .to.be.revertedWithCustomError(core, "OwnableUnauthorizedAccount");
      await expect(core.connect(alice).setTreasury(alice.address))
        .to.be.revertedWithCustomError(core, "OwnableUnauthorizedAccount");
      await expect(core.connect(alice).setPaused(true))
        .to.be.revertedWithCustomError(core, "OwnableUnauthorizedAccount");
      await expect(core.connect(alice).setDefaultRoyalty(alice.address, 500))
        .to.be.revertedWithCustomError(core, "OwnableUnauthorizedAccount");
    });

    it("Should revert setting treasury to zero address", async function () {
      await expect(core.setTreasury(ethers.ZeroAddress))
        .to.be.revertedWithCustomError(core, "ZeroAddress");
    });
  });

  // ═══════════════════════════════════════════════════════════════
  //  INTERFACE SUPPORT
  // ═══════════════════════════════════════════════════════════════

  describe("Interface Support", function () {
    beforeEach(async function () {
      await deployFixture();
    });

    it("Should support ERC-721", async function () {
      expect(await core.supportsInterface("0x80ac58cd")).to.equal(true);
    });

    it("Should support ERC-721 Enumerable", async function () {
      expect(await core.supportsInterface("0x780e9d63")).to.equal(true);
    });

    it("Should support ERC-2981 (royalties)", async function () {
      expect(await core.supportsInterface("0x2a55205a")).to.equal(true);
    });

    it("Should support ERC-4906 (metadata update)", async function () {
      expect(await core.supportsInterface("0x49064906")).to.equal(true);
    });

    it("Should support ERC-165", async function () {
      expect(await core.supportsInterface("0x01ffc9a7")).to.equal(true);
    });
  });

  // ═══════════════════════════════════════════════════════════════
  //  OWNER MINT
  // ═══════════════════════════════════════════════════════════════

  describe("Owner Mint", function () {
    beforeEach(async function () {
      await deployFixture();
    });

    it("Should allow owner to mint to any address for free", async function () {
      const config = ethers.toUtf8Bytes("owner-config");
      await core.ownerMint(config, alice.address);

      expect(await core.ownerOf(1)).to.equal(alice.address);
      expect(await core.nextTokenId()).to.equal(2n);
    });

    it("Should not count against recipient mint limit", async function () {
      const config = ethers.toUtf8Bytes("promo");

      // Owner mints 5 to alice (beyond the 3-per-wallet limit)
      for (let i = 0; i < 5; i++) {
        await core.ownerMint(config, alice.address);
      }

      expect(await core.balanceOf(alice.address)).to.equal(5n);

      // alice can still use her own 3 regular mints
      await core.connect(alice).mint(config, { value: 0 }); // free WL mint
      expect(await core.balanceOf(alice.address)).to.equal(6n);
    });

    it("Should batch mint multiple to same address", async function () {
      const config = ethers.toUtf8Bytes("batch");
      await core.ownerMintBatch(config, bob.address, 10);

      expect(await core.balanceOf(bob.address)).to.equal(10n);
      expect(await core.nextTokenId()).to.equal(11n);

      // All should be genesis (within first 1000)
      for (let i = 1; i <= 10; i++) {
        expect(await core.isGenesis(i)).to.equal(true);
        expect(await core.ownerOf(i)).to.equal(bob.address);
      }
    });

    it("Should set genesis flag correctly on owner mints", async function () {
      const config = ethers.toUtf8Bytes("gen-test");
      await core.ownerMint(config, alice.address);
      expect(await core.isGenesis(1)).to.equal(true);
    });

    it("Should revert owner mint from non-owner", async function () {
      const config = ethers.toUtf8Bytes("hack");
      await expect(core.connect(alice).ownerMint(config, alice.address))
        .to.be.revert(ethers);
    });

    it("Should revert owner mint to zero address", async function () {
      const config = ethers.toUtf8Bytes("zero");
      await expect(core.ownerMint(config, ethers.ZeroAddress))
        .to.be.revert(ethers);
    });

    it("Should revert owner batch mint from non-owner", async function () {
      const config = ethers.toUtf8Bytes("hack");
      await expect(core.connect(alice).ownerMintBatch(config, alice.address, 5))
        .to.be.revert(ethers);
    });
  });

  // ═══════════════════════════════════════════════════════════════
  //  FULL LIFECYCLE
  // ═══════════════════════════════════════════════════════════════

  describe("Full Lifecycle", function () {
    it("Should complete full agent lifecycle", async function () {
      await deployFixture();

      // 1. Mint an Exoskeleton (alice is whitelisted, first mint free)
      const tokenId = await mintExoskeleton(alice);
      expect(tokenId).to.equal(1n);
      expect(await core.ownerOf(1)).to.equal(alice.address);

      // 2. Set name
      await core.connect(alice).setName(1, "Ollie");
      const identityAfterName = await core.getIdentity(1);
      expect(identityAfterName.name).to.equal("Ollie");

      // 3. Set bio
      await core.connect(alice).setBio(1, "potdealer's first agent");
      const identityAfterBio = await core.getIdentity(1);
      expect(identityAfterBio.bio).to.equal("potdealer's first agent");

      // 4. Send a message to another exoskeleton
      await mintExoskeleton(bob); // token 2
      const payload = ethers.toUtf8Bytes("hey, let's play Agent Outlier");
      await core.connect(alice).sendMessage(1, 2, ethers.ZeroHash, 0, payload);
      expect(await core.getMessageCount()).to.equal(1n);

      // 5. Store data
      const key = ethers.keccak256(ethers.toUtf8Bytes("skills"));
      await core.connect(alice).setData(1, key, ethers.toUtf8Bytes("solidity,game-theory"));
      const stored = await core.getData(1, key);
      expect(stored).to.equal(ethers.hexlify(ethers.toUtf8Bytes("solidity,game-theory")));

      // 6. Activate a module
      const modName = ethers.keccak256(ethers.toUtf8Bytes("game-connector"));
      await core.registerModule(modName, external1.address, false, 0);
      await core.connect(alice).activateModule(1, modName);
      expect(await core.isModuleActive(1, modName)).to.equal(true);

      // 7. Check reputation
      const rep = await core.getReputation(1);
      expect(rep.messagesSent).to.equal(1n);
      expect(rep.storageWrites).to.equal(1n);
      expect(rep.modulesActive).to.equal(1n);

      // 8. Grant external scorer and set score
      await core.connect(alice).grantScorer(1, external1.address);
      const eloKey = ethers.keccak256(ethers.toUtf8Bytes("outlier-elo"));
      await core.connect(external1).setExternalScore(1, eloKey, 1650);
      expect(await core.externalScores(1, eloKey)).to.equal(1650);

      // 9. Check reputation score > 0 (genesis multiplier)
      expect(await core.getReputationScore(1)).to.be.greaterThan(0n);

      // 10. Verify tokenURI has all data
      const uri = await core.tokenURI(1);
      const base64 = uri.replace("data:application/json;base64,", "");
      const json = JSON.parse(Buffer.from(base64, "base64").toString());
      expect(json.name).to.equal("Ollie");
      expect(json.description).to.equal("potdealer's first agent");
    });
  });
});
