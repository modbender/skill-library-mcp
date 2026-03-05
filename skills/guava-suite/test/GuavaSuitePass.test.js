import { expect } from "chai";
import { network } from "hardhat";

describe("GuavaSuitePass", function () {
  async function deployFixture() {
    const { ethers } = await network.connect();
    const [owner, alice, bob, treasury] = await ethers.getSigners();

    const Token = await ethers.getContractFactory("MockGuavaToken");
    const token = await Token.deploy();

    const price = ethers.parseEther("100");
    const Pass = await ethers.getContractFactory("GuavaSuitePass");
    const pass = await Pass.deploy(await token.getAddress(), treasury.address, price);

    await token.mint(alice.address, ethers.parseEther("1000"));
    await token.mint(bob.address, ethers.parseEther("1000"));

    return { owner, alice, bob, treasury, token, pass, price, ethers };
  }

  it("mints pass after ERC20 payment", async function () {
    const { alice, treasury, token, pass, price } = await deployFixture();

    await token.connect(alice).approve(await pass.getAddress(), price);
    await expect(pass.connect(alice).buyWithGuava()).to.emit(pass, "PassPurchased");

    expect(await pass.activePassId(alice.address)).to.equal(1n);
    expect(await token.balanceOf(treasury.address)).to.equal(price);
  });

  it("rejects purchase without allowance", async function () {
    const { alice, token, pass } = await deployFixture();
    await expect(pass.connect(alice).buyWithGuava()).to.be.revertedWithCustomError(token, "ERC20InsufficientAllowance");
  });

  it("rejects second purchase by same wallet", async function () {
    const { alice, token, pass, price } = await deployFixture();

    await token.connect(alice).approve(await pass.getAddress(), price * 2n);
    await pass.connect(alice).buyWithGuava();
    await expect(pass.connect(alice).buyWithGuava()).to.be.revertedWithCustomError(pass, "AlreadyHasPass");
  });

  it("supports revoke / validity check", async function () {
    const { owner, alice, token, pass, price } = await deployFixture();

    await token.connect(alice).approve(await pass.getAddress(), price);
    await pass.connect(alice).buyWithGuava();

    expect(await pass.isValidPassHolder(alice.address)).to.equal(true);
    await pass.connect(owner).setRevoked(1, true);
    expect(await pass.isValidPassHolder(alice.address)).to.equal(false);
  });

  it("blocks transfer when transferable=false", async function () {
    const { alice, bob, token, pass, price } = await deployFixture();

    await token.connect(alice).approve(await pass.getAddress(), price);
    await pass.connect(alice).buyWithGuava();

    await expect(pass.connect(alice).transferFrom(alice.address, bob.address, 1)).to.be.revertedWithCustomError(pass, "TransferDisabled");
  });
});
