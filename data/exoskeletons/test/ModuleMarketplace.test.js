import { expect } from "chai";
import { network } from "hardhat";

const { ethers } = await network.connect();

describe("ModuleMarketplace", function () {
  let marketplace, core;
  let owner, alice, bob, builder1, builder2, treasury;

  const LISTING_FEE = ethers.parseEther("0.001");
  const MAX_PRICE = ethers.parseEther("10");
  const PLATFORM_FEE_BPS = 420n;
  const BPS_DENOMINATOR = 10000n;
  const GENESIS_PRICE = ethers.parseEther("0.005");

  // Module name hashes
  const MOD_A = ethers.keccak256(ethers.toUtf8Bytes("module-alpha"));
  const MOD_B = ethers.keccak256(ethers.toUtf8Bytes("module-beta"));
  const MOD_C = ethers.keccak256(ethers.toUtf8Bytes("module-gamma"));
  const MOD_FREE = ethers.keccak256(ethers.toUtf8Bytes("module-free"));

  async function deployFixture() {
    [owner, alice, bob, builder1, builder2, treasury] = await ethers.getSigners();

    // Deploy ExoskeletonCore (needed for ownerOf checks)
    core = await ethers.deployContract("ExoskeletonCore", [treasury.address]);

    // Whitelist alice and bob so they can mint
    await core.setWhitelist(alice.address, true);
    await core.setWhitelist(bob.address, true);

    // Deploy ModuleMarketplace
    marketplace = await ethers.deployContract("ModuleMarketplace", [
      await core.getAddress(),
      treasury.address,
    ]);

    return { marketplace, core, owner, alice, bob, builder1, builder2, treasury };
  }

  // Helper: mint an exoskeleton for a signer
  async function mintExo(signer) {
    const config = ethers.toUtf8Bytes("default-cfg");
    const isWL = await core.whitelist(signer.address);
    const usedFree = await core.usedFreeMint(signer.address);
    const value = (isWL && !usedFree) ? 0n : await core.getMintPrice();
    await core.connect(signer).mint(config, { value });
    return await core.nextTokenId() - 1n;
  }

  // Helper: register a builder
  async function regBuilder(signer, name = "Builder", bio = "I build modules") {
    await marketplace.connect(signer).registerBuilder(name, bio);
  }

  // Helper: submit and approve a module
  async function submitAndApprove(signer, moduleName, name, price = 0n) {
    await marketplace.connect(signer).submitModule(
      moduleName, name, "A module", "1.0.0", price,
      { value: LISTING_FEE }
    );
    await marketplace.approveModule(moduleName);
  }

  // ═══════════════════════════════════════════════════════════════
  //  DEPLOYMENT
  // ═══════════════════════════════════════════════════════════════

  describe("Deployment", function () {
    it("Should deploy with correct state", async function () {
      await deployFixture();
      expect(await marketplace.platformTreasury()).to.equal(treasury.address);
      expect(await marketplace.totalModules()).to.equal(0n);
      expect(await marketplace.totalApproved()).to.equal(0n);
      expect(await marketplace.totalActivations()).to.equal(0n);
      expect(await marketplace.totalPlatformRevenue()).to.equal(0n);
    });

    it("Should store core contract address", async function () {
      await deployFixture();
      expect(await marketplace.core()).to.equal(await core.getAddress());
    });

    it("Should store constants correctly", async function () {
      await deployFixture();
      expect(await marketplace.PLATFORM_FEE_BPS()).to.equal(420n);
      expect(await marketplace.LISTING_FEE()).to.equal(LISTING_FEE);
      expect(await marketplace.MAX_PRICE()).to.equal(MAX_PRICE);
    });

    it("Should revert on zero core address", async function () {
      await deployFixture();
      await expect(
        ethers.deployContract("ModuleMarketplace", [ethers.ZeroAddress, treasury.address])
      ).to.be.revertedWithCustomError(marketplace, "ZeroAddress");
    });

    it("Should revert on zero treasury address", async function () {
      await deployFixture();
      await expect(
        ethers.deployContract("ModuleMarketplace", [await core.getAddress(), ethers.ZeroAddress])
      ).to.be.revertedWithCustomError(marketplace, "ZeroAddress");
    });
  });

  // ═══════════════════════════════════════════════════════════════
  //  BUILDER REGISTRATION
  // ═══════════════════════════════════════════════════════════════

  describe("Builder Registration", function () {
    beforeEach(async function () {
      await deployFixture();
    });

    it("Should register a builder", async function () {
      await expect(marketplace.connect(builder1).registerBuilder("Alice Builds", "I make cool modules"))
        .to.emit(marketplace, "BuilderRegistered")
        .withArgs(builder1.address, "Alice Builds");

      const b = await marketplace.getBuilder(builder1.address);
      expect(b.name).to.equal("Alice Builds");
      expect(b.bio).to.equal("I make cool modules");
      expect(b.modulesSubmitted).to.equal(0n);
      expect(b.totalEarnings).to.equal(0n);
      expect(b.registered).to.equal(true);
    });

    it("Should revert duplicate registration", async function () {
      await regBuilder(builder1);
      await expect(
        marketplace.connect(builder1).registerBuilder("Duplicate", "nope")
      ).to.be.revertedWithCustomError(marketplace, "BuilderAlreadyRegistered");
    });

    it("Should revert empty name", async function () {
      await expect(
        marketplace.connect(builder1).registerBuilder("", "bio")
      ).to.be.revertedWithCustomError(marketplace, "EmptyName");
    });

    it("Should revert name too long", async function () {
      const longName = "A".repeat(65);
      await expect(
        marketplace.connect(builder1).registerBuilder(longName, "bio")
      ).to.be.revertedWithCustomError(marketplace, "NameTooLong");
    });

    it("Should update builder profile", async function () {
      await regBuilder(builder1);
      await expect(marketplace.connect(builder1).updateBuilderProfile("New Name", "New Bio"))
        .to.emit(marketplace, "BuilderUpdated")
        .withArgs(builder1.address);

      const b = await marketplace.getBuilder(builder1.address);
      expect(b.name).to.equal("New Name");
      expect(b.bio).to.equal("New Bio");
    });

    it("Should revert update from unregistered builder", async function () {
      await expect(
        marketplace.connect(builder1).updateBuilderProfile("Name", "Bio")
      ).to.be.revertedWithCustomError(marketplace, "BuilderNotRegistered");
    });
  });

  // ═══════════════════════════════════════════════════════════════
  //  MODULE SUBMISSION
  // ═══════════════════════════════════════════════════════════════

  describe("Module Submission", function () {
    beforeEach(async function () {
      await deployFixture();
      await regBuilder(builder1);
    });

    it("Should submit a module with listing fee", async function () {
      await expect(
        marketplace.connect(builder1).submitModule(
          MOD_A, "Alpha Module", "Description", "1.0.0", ethers.parseEther("0.01"),
          { value: LISTING_FEE }
        )
      ).to.emit(marketplace, "ModuleSubmitted")
        .withArgs(MOD_A, builder1.address, ethers.parseEther("0.01"));

      const mod = await marketplace.getModule(MOD_A);
      expect(mod.builder).to.equal(builder1.address);
      expect(mod.name).to.equal("Alpha Module");
      expect(mod.description).to.equal("Description");
      expect(mod.version).to.equal("1.0.0");
      expect(mod.price).to.equal(ethers.parseEther("0.01"));
      expect(mod.status).to.equal(1n); // PENDING
    });

    it("Should submit a free module", async function () {
      await marketplace.connect(builder1).submitModule(
        MOD_FREE, "Free Module", "A free module", "1.0.0", 0,
        { value: LISTING_FEE }
      );
      const mod = await marketplace.getModule(MOD_FREE);
      expect(mod.price).to.equal(0n);
      expect(mod.status).to.equal(1n); // PENDING
    });

    it("Should accumulate listing fees", async function () {
      await marketplace.connect(builder1).submitModule(
        MOD_A, "A", "Desc", "1.0", 0, { value: LISTING_FEE }
      );
      expect(await marketplace.accumulatedListingFees()).to.equal(LISTING_FEE);
    });

    it("Should add to pending queue", async function () {
      await marketplace.connect(builder1).submitModule(
        MOD_A, "A", "Desc", "1.0", 0, { value: LISTING_FEE }
      );
      const queue = await marketplace.getPendingQueue();
      expect(queue.length).to.equal(1);
      expect(queue[0]).to.equal(MOD_A);
    });

    it("Should increment builder module count", async function () {
      await marketplace.connect(builder1).submitModule(
        MOD_A, "A", "Desc", "1.0", 0, { value: LISTING_FEE }
      );
      const b = await marketplace.getBuilder(builder1.address);
      expect(b.modulesSubmitted).to.equal(1n);
    });

    it("Should track builder modules", async function () {
      await marketplace.connect(builder1).submitModule(
        MOD_A, "A", "D", "1.0", 0, { value: LISTING_FEE }
      );
      const mods = await marketplace.getBuilderModules(builder1.address);
      expect(mods.length).to.equal(1);
      expect(mods[0]).to.equal(MOD_A);
    });

    it("Should refund overpayment", async function () {
      const overpay = LISTING_FEE + ethers.parseEther("0.5");
      const balBefore = await ethers.provider.getBalance(builder1.address);

      const tx = await marketplace.connect(builder1).submitModule(
        MOD_A, "A", "D", "1.0", 0, { value: overpay }
      );
      const receipt = await tx.wait();
      const gasCost = receipt.gasUsed * receipt.gasPrice;

      const balAfter = await ethers.provider.getBalance(builder1.address);
      // Should only have spent listing fee + gas
      expect(balBefore - balAfter).to.equal(LISTING_FEE + gasCost);
    });

    it("Should revert if not registered builder", async function () {
      await expect(
        marketplace.connect(builder2).submitModule(
          MOD_A, "A", "D", "1.0", 0, { value: LISTING_FEE }
        )
      ).to.be.revertedWithCustomError(marketplace, "BuilderNotRegistered");
    });

    it("Should revert on insufficient listing fee", async function () {
      await expect(
        marketplace.connect(builder1).submitModule(
          MOD_A, "A", "D", "1.0", 0, { value: LISTING_FEE - 1n }
        )
      ).to.be.revertedWithCustomError(marketplace, "InsufficientPayment");
    });

    it("Should revert on duplicate module name", async function () {
      await marketplace.connect(builder1).submitModule(
        MOD_A, "A", "D", "1.0", 0, { value: LISTING_FEE }
      );
      await expect(
        marketplace.connect(builder1).submitModule(
          MOD_A, "A2", "D2", "1.0", 0, { value: LISTING_FEE }
        )
      ).to.be.revertedWithCustomError(marketplace, "ModuleAlreadyExists");
    });

    it("Should revert if price exceeds max", async function () {
      await expect(
        marketplace.connect(builder1).submitModule(
          MOD_A, "A", "D", "1.0", MAX_PRICE + 1n, { value: LISTING_FEE }
        )
      ).to.be.revertedWithCustomError(marketplace, "PriceExceedsMax");
    });

    it("Should revert on empty module name", async function () {
      await expect(
        marketplace.connect(builder1).submitModule(
          MOD_A, "", "D", "1.0", 0, { value: LISTING_FEE }
        )
      ).to.be.revertedWithCustomError(marketplace, "EmptyName");
    });
  });

  // ═══════════════════════════════════════════════════════════════
  //  APPROVAL / REJECTION
  // ═══════════════════════════════════════════════════════════════

  describe("Approval & Rejection", function () {
    beforeEach(async function () {
      await deployFixture();
      await regBuilder(builder1);
      await marketplace.connect(builder1).submitModule(
        MOD_A, "Alpha", "Desc", "1.0", ethers.parseEther("0.01"),
        { value: LISTING_FEE }
      );
    });

    it("Should approve a pending module", async function () {
      await expect(marketplace.approveModule(MOD_A))
        .to.emit(marketplace, "ModuleApproved")
        .withArgs(MOD_A);

      const mod = await marketplace.getModule(MOD_A);
      expect(mod.status).to.equal(2n); // APPROVED
      expect(mod.approvedAt).to.be.greaterThan(0n);
      expect(await marketplace.totalApproved()).to.equal(1n);
    });

    it("Should remove from pending queue on approve", async function () {
      await marketplace.approveModule(MOD_A);
      expect(await marketplace.getPendingCount()).to.equal(0n);
    });

    it("Should reject a pending module with reason", async function () {
      await expect(marketplace.rejectModule(MOD_A, "Low quality"))
        .to.emit(marketplace, "ModuleRejected")
        .withArgs(MOD_A, "Low quality");

      const mod = await marketplace.getModule(MOD_A);
      expect(mod.status).to.equal(3n); // REJECTED
    });

    it("Should remove from pending queue on reject", async function () {
      await marketplace.rejectModule(MOD_A, "nope");
      expect(await marketplace.getPendingCount()).to.equal(0n);
    });

    it("Should revert approving non-pending module", async function () {
      await marketplace.approveModule(MOD_A);
      await expect(marketplace.approveModule(MOD_A))
        .to.be.revertedWithCustomError(marketplace, "ModuleNotPending");
    });

    it("Should revert rejecting non-pending module", async function () {
      await marketplace.approveModule(MOD_A);
      await expect(marketplace.rejectModule(MOD_A, "late"))
        .to.be.revertedWithCustomError(marketplace, "ModuleNotPending");
    });

    it("Should revert approve from non-owner", async function () {
      await expect(
        marketplace.connect(alice).approveModule(MOD_A)
      ).to.be.revertedWithCustomError(marketplace, "OwnableUnauthorizedAccount");
    });

    it("Should revert reject from non-owner", async function () {
      await expect(
        marketplace.connect(alice).rejectModule(MOD_A, "no")
      ).to.be.revertedWithCustomError(marketplace, "OwnableUnauthorizedAccount");
    });
  });

  // ═══════════════════════════════════════════════════════════════
  //  DELISTING & RELISTING
  // ═══════════════════════════════════════════════════════════════

  describe("Delisting & Relisting", function () {
    beforeEach(async function () {
      await deployFixture();
      await regBuilder(builder1);
      await submitAndApprove(builder1, MOD_A, "Alpha", ethers.parseEther("0.01"));
    });

    it("Should owner-delist an approved module", async function () {
      await expect(marketplace.delistModule(MOD_A))
        .to.emit(marketplace, "ModuleDelisted")
        .withArgs(MOD_A, owner.address);

      const mod = await marketplace.getModule(MOD_A);
      expect(mod.status).to.equal(4n); // DELISTED
      expect(await marketplace.totalApproved()).to.equal(0n);
    });

    it("Should builder-delist own module", async function () {
      await expect(marketplace.connect(builder1).builderDelistModule(MOD_A))
        .to.emit(marketplace, "ModuleDelisted")
        .withArgs(MOD_A, builder1.address);

      const mod = await marketplace.getModule(MOD_A);
      expect(mod.status).to.equal(4n); // DELISTED
    });

    it("Should relist a delisted module", async function () {
      await marketplace.delistModule(MOD_A);
      await expect(marketplace.relistModule(MOD_A))
        .to.emit(marketplace, "ModuleRelisted")
        .withArgs(MOD_A);

      const mod = await marketplace.getModule(MOD_A);
      expect(mod.status).to.equal(2n); // APPROVED
      expect(await marketplace.totalApproved()).to.equal(1n);
    });

    it("Should revert delisting non-approved module", async function () {
      await marketplace.delistModule(MOD_A);
      await expect(marketplace.delistModule(MOD_A))
        .to.be.revertedWithCustomError(marketplace, "ModuleNotApproved");
    });

    it("Should revert relisting non-delisted module", async function () {
      await expect(marketplace.relistModule(MOD_A))
        .to.be.revertedWithCustomError(marketplace, "ModuleNotDelisted");
    });

    it("Should revert builder delist if not the builder", async function () {
      await expect(
        marketplace.connect(builder2).builderDelistModule(MOD_A)
      ).to.be.revertedWithCustomError(marketplace, "NotModuleBuilder");
    });

    it("Should revert builder delist if not approved", async function () {
      await marketplace.delistModule(MOD_A);
      await expect(
        marketplace.connect(builder1).builderDelistModule(MOD_A)
      ).to.be.revertedWithCustomError(marketplace, "ModuleNotApproved");
    });
  });

  // ═══════════════════════════════════════════════════════════════
  //  ACTIVATION — FREE MODULES
  // ═══════════════════════════════════════════════════════════════

  describe("Activation — Free Modules", function () {
    let tokenId;

    beforeEach(async function () {
      await deployFixture();
      await regBuilder(builder1);
      await submitAndApprove(builder1, MOD_FREE, "Free Module", 0n);
      tokenId = await mintExo(alice);
    });

    it("Should activate a free module", async function () {
      await expect(marketplace.connect(alice).activateModule(tokenId, MOD_FREE))
        .to.emit(marketplace, "ModuleActivated")
        .withArgs(MOD_FREE, tokenId, alice.address);

      expect(await marketplace.isModuleActive(tokenId, MOD_FREE)).to.equal(true);
    });

    it("Should track activation timestamp", async function () {
      await marketplace.connect(alice).activateModule(tokenId, MOD_FREE);
      const act = await marketplace.getActivation(tokenId, MOD_FREE);
      expect(act.active).to.equal(true);
      expect(act.activatedAt).to.be.greaterThan(0n);
    });

    it("Should add to token active modules list", async function () {
      await marketplace.connect(alice).activateModule(tokenId, MOD_FREE);
      const mods = await marketplace.getTokenActiveModules(tokenId);
      expect(mods.length).to.equal(1);
      expect(mods[0]).to.equal(MOD_FREE);
    });

    it("Should increment global activation count", async function () {
      await marketplace.connect(alice).activateModule(tokenId, MOD_FREE);
      expect(await marketplace.totalActivations()).to.equal(1n);
    });

    it("Should increment module activation count", async function () {
      await marketplace.connect(alice).activateModule(tokenId, MOD_FREE);
      const mod = await marketplace.getModule(MOD_FREE);
      expect(mod.moduleActivations).to.equal(1n);
    });

    it("Should refund ETH sent for free module activation", async function () {
      const balBefore = await ethers.provider.getBalance(alice.address);
      const tx = await marketplace.connect(alice).activateModule(tokenId, MOD_FREE, {
        value: ethers.parseEther("0.1"),
      });
      const receipt = await tx.wait();
      const gasCost = receipt.gasUsed * receipt.gasPrice;
      const balAfter = await ethers.provider.getBalance(alice.address);

      // Only gas should be spent (ETH refunded)
      expect(balBefore - balAfter).to.equal(gasCost);
    });

    it("Should revert if not token owner", async function () {
      await expect(
        marketplace.connect(bob).activateModule(tokenId, MOD_FREE)
      ).to.be.revertedWithCustomError(marketplace, "NotTokenOwner");
    });

    it("Should revert on double activation", async function () {
      await marketplace.connect(alice).activateModule(tokenId, MOD_FREE);
      await expect(
        marketplace.connect(alice).activateModule(tokenId, MOD_FREE)
      ).to.be.revertedWithCustomError(marketplace, "ModuleAlreadyActive");
    });

    it("Should revert if module not approved", async function () {
      // Submit but don't approve
      await marketplace.connect(builder1).submitModule(
        MOD_A, "Alpha", "Desc", "1.0", 0, { value: LISTING_FEE }
      );
      await expect(
        marketplace.connect(alice).activateModule(tokenId, MOD_A)
      ).to.be.revertedWithCustomError(marketplace, "ModuleNotApproved");
    });

    it("Should revert if module doesn't exist", async function () {
      const fakeMod = ethers.keccak256(ethers.toUtf8Bytes("nonexistent"));
      await expect(
        marketplace.connect(alice).activateModule(tokenId, fakeMod)
      ).to.be.revertedWithCustomError(marketplace, "ModuleNotApproved");
    });
  });

  // ═══════════════════════════════════════════════════════════════
  //  ACTIVATION — PREMIUM MODULES (PAYMENT SPLIT)
  // ═══════════════════════════════════════════════════════════════

  describe("Activation — Premium Modules", function () {
    let tokenId;
    const MODULE_PRICE = ethers.parseEther("0.1");

    beforeEach(async function () {
      await deployFixture();
      await regBuilder(builder1);
      await submitAndApprove(builder1, MOD_A, "Premium Alpha", MODULE_PRICE);
      tokenId = await mintExo(alice);
    });

    it("Should split payment 95.80% builder / 4.20% platform", async function () {
      const builderBalBefore = await ethers.provider.getBalance(builder1.address);
      const treasuryBalBefore = await ethers.provider.getBalance(treasury.address);

      await marketplace.connect(alice).activateModule(tokenId, MOD_A, {
        value: MODULE_PRICE,
      });

      const builderBalAfter = await ethers.provider.getBalance(builder1.address);
      const treasuryBalAfter = await ethers.provider.getBalance(treasury.address);

      const expectedPlatformFee = (MODULE_PRICE * PLATFORM_FEE_BPS) / BPS_DENOMINATOR;
      const expectedBuilderPayout = MODULE_PRICE - expectedPlatformFee;

      // 0.1 ETH * 420 / 10000 = 0.0042 ETH platform fee
      expect(expectedPlatformFee).to.equal(ethers.parseEther("0.0042"));
      // 0.1 ETH - 0.0042 ETH = 0.0958 ETH builder payout
      expect(expectedBuilderPayout).to.equal(ethers.parseEther("0.0958"));

      expect(builderBalAfter - builderBalBefore).to.equal(expectedBuilderPayout);
      expect(treasuryBalAfter - treasuryBalBefore).to.equal(expectedPlatformFee);
    });

    it("Should track module revenue", async function () {
      await marketplace.connect(alice).activateModule(tokenId, MOD_A, {
        value: MODULE_PRICE,
      });

      const mod = await marketplace.getModule(MOD_A);
      expect(mod.moduleRevenue).to.equal(MODULE_PRICE);
    });

    it("Should track builder earnings (builder portion only)", async function () {
      await marketplace.connect(alice).activateModule(tokenId, MOD_A, {
        value: MODULE_PRICE,
      });

      const expectedBuilderPayout = MODULE_PRICE - (MODULE_PRICE * PLATFORM_FEE_BPS) / BPS_DENOMINATOR;
      const b = await marketplace.getBuilder(builder1.address);
      expect(b.totalEarnings).to.equal(expectedBuilderPayout);
    });

    it("Should track platform revenue", async function () {
      await marketplace.connect(alice).activateModule(tokenId, MOD_A, {
        value: MODULE_PRICE,
      });

      const expectedPlatformFee = (MODULE_PRICE * PLATFORM_FEE_BPS) / BPS_DENOMINATOR;
      expect(await marketplace.totalPlatformRevenue()).to.equal(expectedPlatformFee);
    });

    it("Should refund overpayment on premium activation", async function () {
      const overpay = MODULE_PRICE + ethers.parseEther("1");
      const balBefore = await ethers.provider.getBalance(alice.address);

      const tx = await marketplace.connect(alice).activateModule(tokenId, MOD_A, {
        value: overpay,
      });
      const receipt = await tx.wait();
      const gasCost = receipt.gasUsed * receipt.gasPrice;

      const balAfter = await ethers.provider.getBalance(alice.address);
      // Should only have spent module price + gas (excess refunded)
      expect(balBefore - balAfter).to.equal(MODULE_PRICE + gasCost);
    });

    it("Should revert on insufficient payment", async function () {
      await expect(
        marketplace.connect(alice).activateModule(tokenId, MOD_A, {
          value: MODULE_PRICE - 1n,
        })
      ).to.be.revertedWithCustomError(marketplace, "InsufficientPayment");
    });

    it("Should handle multiple activations across tokens", async function () {
      const tokenId2 = await mintExo(bob);

      await marketplace.connect(alice).activateModule(tokenId, MOD_A, { value: MODULE_PRICE });
      await marketplace.connect(bob).activateModule(tokenId2, MOD_A, { value: MODULE_PRICE });

      const mod = await marketplace.getModule(MOD_A);
      expect(mod.moduleActivations).to.equal(2n);
      expect(mod.moduleRevenue).to.equal(MODULE_PRICE * 2n);
      expect(await marketplace.totalActivations()).to.equal(2n);
    });

    it("Should handle exact 4.20% on different price points", async function () {
      // Submit module at 1 ETH
      await regBuilder(builder2, "Builder2");
      await submitAndApprove(builder2, MOD_B, "Expensive Module", ethers.parseEther("1"));

      const builderBal = await ethers.provider.getBalance(builder2.address);
      const treasuryBal = await ethers.provider.getBalance(treasury.address);

      await marketplace.connect(alice).activateModule(tokenId, MOD_B, {
        value: ethers.parseEther("1"),
      });

      const builderGain = (await ethers.provider.getBalance(builder2.address)) - builderBal;
      const treasuryGain = (await ethers.provider.getBalance(treasury.address)) - treasuryBal;

      // 1 ETH: platform = 0.042, builder = 0.958
      expect(treasuryGain).to.equal(ethers.parseEther("0.042"));
      expect(builderGain).to.equal(ethers.parseEther("0.958"));
    });
  });

  // ═══════════════════════════════════════════════════════════════
  //  DEACTIVATION
  // ═══════════════════════════════════════════════════════════════

  describe("Deactivation", function () {
    let tokenId;

    beforeEach(async function () {
      await deployFixture();
      await regBuilder(builder1);
      await submitAndApprove(builder1, MOD_FREE, "Free Module", 0n);
      tokenId = await mintExo(alice);
      await marketplace.connect(alice).activateModule(tokenId, MOD_FREE);
    });

    it("Should deactivate a module", async function () {
      await expect(marketplace.connect(alice).deactivateModule(tokenId, MOD_FREE))
        .to.emit(marketplace, "ModuleDeactivated")
        .withArgs(MOD_FREE, tokenId);

      expect(await marketplace.isModuleActive(tokenId, MOD_FREE)).to.equal(false);
    });

    it("Should remove from token active modules list", async function () {
      await marketplace.connect(alice).deactivateModule(tokenId, MOD_FREE);
      const mods = await marketplace.getTokenActiveModules(tokenId);
      expect(mods.length).to.equal(0);
    });

    it("Should revert if module not active", async function () {
      await marketplace.connect(alice).deactivateModule(tokenId, MOD_FREE);
      await expect(
        marketplace.connect(alice).deactivateModule(tokenId, MOD_FREE)
      ).to.be.revertedWithCustomError(marketplace, "ModuleNotActive");
    });

    it("Should revert if not token owner", async function () {
      await expect(
        marketplace.connect(bob).deactivateModule(tokenId, MOD_FREE)
      ).to.be.revertedWithCustomError(marketplace, "NotTokenOwner");
    });

    it("Should allow reactivation after deactivation (no refund)", async function () {
      await marketplace.connect(alice).deactivateModule(tokenId, MOD_FREE);
      await marketplace.connect(alice).activateModule(tokenId, MOD_FREE);
      expect(await marketplace.isModuleActive(tokenId, MOD_FREE)).to.equal(true);
    });
  });

  // ═══════════════════════════════════════════════════════════════
  //  BUILDER UPDATES
  // ═══════════════════════════════════════════════════════════════

  describe("Builder Updates", function () {
    beforeEach(async function () {
      await deployFixture();
      await regBuilder(builder1);
      await submitAndApprove(builder1, MOD_A, "Alpha", ethers.parseEther("0.05"));
    });

    it("Should update module price", async function () {
      const newPrice = ethers.parseEther("0.1");
      await expect(marketplace.connect(builder1).updateModulePrice(MOD_A, newPrice))
        .to.emit(marketplace, "ModulePriceUpdated")
        .withArgs(MOD_A, ethers.parseEther("0.05"), newPrice);

      const mod = await marketplace.getModule(MOD_A);
      expect(mod.price).to.equal(newPrice);
    });

    it("Should update module description", async function () {
      await expect(marketplace.connect(builder1).updateModuleDescription(MOD_A, "New description"))
        .to.emit(marketplace, "ModuleDescriptionUpdated")
        .withArgs(MOD_A);

      const mod = await marketplace.getModule(MOD_A);
      expect(mod.description).to.equal("New description");
    });

    it("Should update module version", async function () {
      await expect(marketplace.connect(builder1).updateModuleVersion(MOD_A, "2.0.0"))
        .to.emit(marketplace, "ModuleVersionUpdated")
        .withArgs(MOD_A, "2.0.0");

      const mod = await marketplace.getModule(MOD_A);
      expect(mod.version).to.equal("2.0.0");
    });

    it("Should revert price update from non-builder", async function () {
      await expect(
        marketplace.connect(builder2).updateModulePrice(MOD_A, 0n)
      ).to.be.revertedWithCustomError(marketplace, "NotModuleBuilder");
    });

    it("Should revert description update from non-builder", async function () {
      await expect(
        marketplace.connect(builder2).updateModuleDescription(MOD_A, "hack")
      ).to.be.revertedWithCustomError(marketplace, "NotModuleBuilder");
    });

    it("Should revert version update from non-builder", async function () {
      await expect(
        marketplace.connect(builder2).updateModuleVersion(MOD_A, "9.9.9")
      ).to.be.revertedWithCustomError(marketplace, "NotModuleBuilder");
    });

    it("Should revert if price exceeds max", async function () {
      await expect(
        marketplace.connect(builder1).updateModulePrice(MOD_A, MAX_PRICE + 1n)
      ).to.be.revertedWithCustomError(marketplace, "PriceExceedsMax");
    });

    it("Should allow changing from premium to free", async function () {
      await marketplace.connect(builder1).updateModulePrice(MOD_A, 0n);
      const mod = await marketplace.getModule(MOD_A);
      expect(mod.price).to.equal(0n);
    });
  });

  // ═══════════════════════════════════════════════════════════════
  //  ADMIN
  // ═══════════════════════════════════════════════════════════════

  describe("Admin", function () {
    beforeEach(async function () {
      await deployFixture();
      await regBuilder(builder1);
    });

    it("Should withdraw accumulated listing fees", async function () {
      // Submit 3 modules to accumulate fees
      await marketplace.connect(builder1).submitModule(MOD_A, "A", "D", "1.0", 0, { value: LISTING_FEE });
      await marketplace.connect(builder1).submitModule(MOD_B, "B", "D", "1.0", 0, { value: LISTING_FEE });
      await marketplace.connect(builder1).submitModule(MOD_C, "C", "D", "1.0", 0, { value: LISTING_FEE });

      const totalFees = LISTING_FEE * 3n;
      expect(await marketplace.accumulatedListingFees()).to.equal(totalFees);

      const treasuryBal = await ethers.provider.getBalance(treasury.address);
      await expect(marketplace.withdrawListingFees())
        .to.emit(marketplace, "ListingFeesWithdrawn")
        .withArgs(treasury.address, totalFees);

      const treasuryBalAfter = await ethers.provider.getBalance(treasury.address);
      expect(treasuryBalAfter - treasuryBal).to.equal(totalFees);
      expect(await marketplace.accumulatedListingFees()).to.equal(0n);
    });

    it("Should handle withdraw with zero fees (no-op)", async function () {
      // No fees accumulated — should not revert
      await marketplace.withdrawListingFees();
      expect(await marketplace.accumulatedListingFees()).to.equal(0n);
    });

    it("Should set platform treasury", async function () {
      await expect(marketplace.setPlatformTreasury(alice.address))
        .to.emit(marketplace, "TreasuryUpdated")
        .withArgs(treasury.address, alice.address);

      expect(await marketplace.platformTreasury()).to.equal(alice.address);
    });

    it("Should revert setting treasury to zero address", async function () {
      await expect(
        marketplace.setPlatformTreasury(ethers.ZeroAddress)
      ).to.be.revertedWithCustomError(marketplace, "ZeroAddress");
    });

    it("Should revert admin calls from non-owner", async function () {
      await expect(
        marketplace.connect(alice).withdrawListingFees()
      ).to.be.revertedWithCustomError(marketplace, "OwnableUnauthorizedAccount");

      await expect(
        marketplace.connect(alice).setPlatformTreasury(alice.address)
      ).to.be.revertedWithCustomError(marketplace, "OwnableUnauthorizedAccount");

      // Submit a module so we can test approve/reject auth
      await marketplace.connect(builder1).submitModule(
        MOD_A, "A", "D", "1.0", 0, { value: LISTING_FEE }
      );
      await expect(
        marketplace.connect(alice).approveModule(MOD_A)
      ).to.be.revertedWithCustomError(marketplace, "OwnableUnauthorizedAccount");

      await expect(
        marketplace.connect(alice).rejectModule(MOD_A, "no")
      ).to.be.revertedWithCustomError(marketplace, "OwnableUnauthorizedAccount");
    });
  });

  // ═══════════════════════════════════════════════════════════════
  //  VIEW FUNCTIONS
  // ═══════════════════════════════════════════════════════════════

  describe("View Functions", function () {
    beforeEach(async function () {
      await deployFixture();
      await regBuilder(builder1);
      await regBuilder(builder2, "Builder2");
      await submitAndApprove(builder1, MOD_A, "Alpha", ethers.parseEther("0.01"));
      await marketplace.connect(builder2).submitModule(
        MOD_B, "Beta", "Desc", "1.0", 0, { value: LISTING_FEE }
      );
    });

    it("Should return all module names", async function () {
      const names = await marketplace.getAllModuleNames();
      expect(names.length).to.equal(2);
    });

    it("Should return pending queue", async function () {
      const queue = await marketplace.getPendingQueue();
      expect(queue.length).to.equal(1);
      expect(queue[0]).to.equal(MOD_B);
    });

    it("Should return module count", async function () {
      expect(await marketplace.getModuleCount()).to.equal(2n);
    });

    it("Should return stats", async function () {
      const stats = await marketplace.getStats();
      expect(stats._totalModules).to.equal(2n);
      expect(stats._totalApproved).to.equal(1n);
      expect(stats._pendingCount).to.equal(1n);
      expect(stats._listingFees).to.equal(LISTING_FEE * 2n);
    });

    it("Should return builder modules", async function () {
      const mods = await marketplace.getBuilderModules(builder1.address);
      expect(mods.length).to.equal(1);
      expect(mods[0]).to.equal(MOD_A);
    });

    it("Should return unregistered builder as not registered", async function () {
      const b = await marketplace.getBuilder(alice.address);
      expect(b.registered).to.equal(false);
    });

    it("Should return false for inactive module", async function () {
      const tokenId = await mintExo(alice);
      expect(await marketplace.isModuleActive(tokenId, MOD_A)).to.equal(false);
    });
  });

  // ═══════════════════════════════════════════════════════════════
  //  EDGE CASES
  // ═══════════════════════════════════════════════════════════════

  describe("Edge Cases", function () {
    beforeEach(async function () {
      await deployFixture();
    });

    it("Should not allow activating a delisted module", async function () {
      await regBuilder(builder1);
      await submitAndApprove(builder1, MOD_A, "Alpha", 0n);
      const tokenId = await mintExo(alice);

      await marketplace.delistModule(MOD_A);
      await expect(
        marketplace.connect(alice).activateModule(tokenId, MOD_A)
      ).to.be.revertedWithCustomError(marketplace, "ModuleNotApproved");
    });

    it("Should allow activating a relisted module", async function () {
      await regBuilder(builder1);
      await submitAndApprove(builder1, MOD_A, "Alpha", 0n);
      const tokenId = await mintExo(alice);

      await marketplace.delistModule(MOD_A);
      await marketplace.relistModule(MOD_A);
      await marketplace.connect(alice).activateModule(tokenId, MOD_A);
      expect(await marketplace.isModuleActive(tokenId, MOD_A)).to.equal(true);
    });

    it("Should handle multiple modules on same token", async function () {
      await regBuilder(builder1);
      await submitAndApprove(builder1, MOD_A, "Alpha", 0n);
      await submitAndApprove(builder1, MOD_B, "Beta", 0n);
      const tokenId = await mintExo(alice);

      await marketplace.connect(alice).activateModule(tokenId, MOD_A);
      await marketplace.connect(alice).activateModule(tokenId, MOD_B);

      const mods = await marketplace.getTokenActiveModules(tokenId);
      expect(mods.length).to.equal(2);
      expect(await marketplace.isModuleActive(tokenId, MOD_A)).to.equal(true);
      expect(await marketplace.isModuleActive(tokenId, MOD_B)).to.equal(true);
    });

    it("Should correctly update active list on deactivate with multiple modules", async function () {
      await regBuilder(builder1);
      await submitAndApprove(builder1, MOD_A, "Alpha", 0n);
      await submitAndApprove(builder1, MOD_B, "Beta", 0n);
      await submitAndApprove(builder1, MOD_C, "Gamma", 0n);
      const tokenId = await mintExo(alice);

      await marketplace.connect(alice).activateModule(tokenId, MOD_A);
      await marketplace.connect(alice).activateModule(tokenId, MOD_B);
      await marketplace.connect(alice).activateModule(tokenId, MOD_C);

      // Deactivate the middle one
      await marketplace.connect(alice).deactivateModule(tokenId, MOD_B);

      const mods = await marketplace.getTokenActiveModules(tokenId);
      expect(mods.length).to.equal(2);
      expect(await marketplace.isModuleActive(tokenId, MOD_A)).to.equal(true);
      expect(await marketplace.isModuleActive(tokenId, MOD_B)).to.equal(false);
      expect(await marketplace.isModuleActive(tokenId, MOD_C)).to.equal(true);
    });

    it("Should handle pending queue with multiple approve/reject operations", async function () {
      await regBuilder(builder1);
      await marketplace.connect(builder1).submitModule(MOD_A, "A", "D", "1.0", 0, { value: LISTING_FEE });
      await marketplace.connect(builder1).submitModule(MOD_B, "B", "D", "1.0", 0, { value: LISTING_FEE });
      await marketplace.connect(builder1).submitModule(MOD_C, "C", "D", "1.0", 0, { value: LISTING_FEE });

      expect(await marketplace.getPendingCount()).to.equal(3n);

      await marketplace.approveModule(MOD_B);
      expect(await marketplace.getPendingCount()).to.equal(2n);

      await marketplace.rejectModule(MOD_A, "rejected");
      expect(await marketplace.getPendingCount()).to.equal(1n);

      await marketplace.approveModule(MOD_C);
      expect(await marketplace.getPendingCount()).to.equal(0n);
    });

    it("Should handle module price update not affecting existing activations", async function () {
      await regBuilder(builder1);
      const originalPrice = ethers.parseEther("0.05");
      await submitAndApprove(builder1, MOD_A, "Alpha", originalPrice);
      const tokenId = await mintExo(alice);

      // Activate at original price
      await marketplace.connect(alice).activateModule(tokenId, MOD_A, { value: originalPrice });

      // Change price
      await marketplace.connect(builder1).updateModulePrice(MOD_A, ethers.parseEther("0.1"));

      // Original activation still active
      expect(await marketplace.isModuleActive(tokenId, MOD_A)).to.equal(true);
    });
  });

  // ═══════════════════════════════════════════════════════════════
  //  FULL LIFECYCLE
  // ═══════════════════════════════════════════════════════════════

  describe("Full Lifecycle", function () {
    it("Should complete full marketplace lifecycle", async function () {
      await deployFixture();

      // 1. Register builder
      await regBuilder(builder1, "Ollie's Workshop");
      const b1 = await marketplace.getBuilder(builder1.address);
      expect(b1.name).to.equal("Ollie's Workshop");

      // 2. Submit module
      const MODULE_PRICE = ethers.parseEther("0.05");
      await marketplace.connect(builder1).submitModule(
        MOD_A, "Trading Tools", "Advanced trading module", "1.0.0", MODULE_PRICE,
        { value: LISTING_FEE }
      );
      expect(await marketplace.getPendingCount()).to.equal(1n);

      // 3. Approve module
      await marketplace.approveModule(MOD_A);
      expect(await marketplace.totalApproved()).to.equal(1n);
      expect(await marketplace.getPendingCount()).to.equal(0n);

      // 4. Mint an exoskeleton
      const tokenId = await mintExo(alice);

      // 5. Activate module
      const builderBalBefore = await ethers.provider.getBalance(builder1.address);
      const treasuryBalBefore = await ethers.provider.getBalance(treasury.address);

      await marketplace.connect(alice).activateModule(tokenId, MOD_A, { value: MODULE_PRICE });

      const builderGain = (await ethers.provider.getBalance(builder1.address)) - builderBalBefore;
      const treasuryGain = (await ethers.provider.getBalance(treasury.address)) - treasuryBalBefore;

      // Verify 95.80% / 4.20% split
      const expectedPlatformFee = (MODULE_PRICE * PLATFORM_FEE_BPS) / BPS_DENOMINATOR;
      const expectedBuilderPayout = MODULE_PRICE - expectedPlatformFee;
      expect(builderGain).to.equal(expectedBuilderPayout);
      expect(treasuryGain).to.equal(expectedPlatformFee);

      // 6. Verify module is active
      expect(await marketplace.isModuleActive(tokenId, MOD_A)).to.equal(true);

      // 7. Check stats
      const stats = await marketplace.getStats();
      expect(stats._totalModules).to.equal(1n);
      expect(stats._totalApproved).to.equal(1n);
      expect(stats._totalActivations).to.equal(1n);
      expect(stats._totalPlatformRevenue).to.equal(expectedPlatformFee);

      // 8. Builder updates price for future activations
      await marketplace.connect(builder1).updateModulePrice(MOD_A, ethers.parseEther("0.1"));

      // 9. Deactivate
      await marketplace.connect(alice).deactivateModule(tokenId, MOD_A);
      expect(await marketplace.isModuleActive(tokenId, MOD_A)).to.equal(false);

      // 10. Withdraw listing fees
      const feesBefore = await marketplace.accumulatedListingFees();
      expect(feesBefore).to.equal(LISTING_FEE);
      await marketplace.withdrawListingFees();
      expect(await marketplace.accumulatedListingFees()).to.equal(0n);
    });
  });
});
