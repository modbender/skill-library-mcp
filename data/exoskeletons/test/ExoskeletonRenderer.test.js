import { expect } from "chai";
import { network } from "hardhat";

const { ethers, networkHelpers } = await network.connect();

describe("ExoskeletonRenderer", function () {
  let core, renderer;
  let owner, alice, bob, treasury;

  const GENESIS_PRICE = ethers.parseEther("0.005");

  async function deployFixture() {
    [owner, alice, bob, treasury] = await ethers.getSigners();

    core = await ethers.deployContract("ExoskeletonCore", [treasury.address]);
    renderer = await ethers.deployContract("ExoskeletonRenderer", [
      await core.getAddress(),
    ]);

    // Set renderer on core
    await core.setRenderer(await renderer.getAddress());

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

  // Build a 9-byte config: [shape, R1, G1, B1, R2, G2, B2, symbol, pattern]
  function buildConfig(shape, r1, g1, b1, r2, g2, b2, symbol, pattern) {
    return new Uint8Array([shape, r1, g1, b1, r2, g2, b2, symbol, pattern]);
  }

  describe("Deployment", function () {
    it("Should deploy with correct core address", async function () {
      await deployFixture();
      expect(await renderer.coreContract()).to.equal(await core.getAddress());
    });

    it("Should allow owner to update core address", async function () {
      await deployFixture();
      await renderer.setCoreContract(alice.address);
      expect(await renderer.coreContract()).to.equal(alice.address);
    });
  });

  describe("SVG Generation", function () {
    beforeEach(async function () {
      await deployFixture();
    });

    it("Should generate SVG with default config", async function () {
      await mintExoskeleton(alice);
      const svg = await renderer.renderSVG(1);

      expect(svg).to.include('<svg xmlns="http://www.w3.org/2000/svg"');
      expect(svg).to.include('</svg>');
      expect(svg).to.include('EXOSKELETON');
      expect(svg).to.include('#1'); // token ID
    });

    it("Should include genesis elements for genesis tokens", async function () {
      await mintExoskeleton(alice);
      const svg = await renderer.renderSVG(1);

      expect(svg).to.include('GENESIS');
      expect(svg).to.include('#FFD700'); // genesis gold
    });

    it("Should use custom name in SVG", async function () {
      await mintExoskeleton(alice);
      await core.connect(alice).setName(1, "Ollie");
      const svg = await renderer.renderSVG(1);

      expect(svg).to.include('Ollie');
    });

    it("Should generate hexagon shape (shape=0)", async function () {
      const config = buildConfig(0, 255, 0, 100, 100, 0, 255, 1, 0);
      await mintExoskeleton(alice, config);
      const svg = await renderer.renderSVG(1);

      // Hexagon uses <polygon> with 6 points
      expect(svg).to.include('<polygon points="250,160 319,200 319,280 250,320 181,280 181,200"');
    });

    it("Should generate circle shape (shape=1)", async function () {
      const config = buildConfig(1, 0, 255, 170, 0, 170, 255, 0, 0);
      await mintExoskeleton(alice, config);
      const svg = await renderer.renderSVG(1);

      expect(svg).to.include('<circle cx="250" cy="240" r="80"');
    });

    it("Should generate diamond shape (shape=2)", async function () {
      const config = buildConfig(2, 200, 100, 50, 100, 50, 200, 0, 0);
      await mintExoskeleton(alice, config);
      const svg = await renderer.renderSVG(1);

      expect(svg).to.include('points="250,155 340,240 250,325 160,240"');
    });

    it("Should generate shield shape (shape=3)", async function () {
      const config = buildConfig(3, 100, 200, 50, 50, 100, 200, 0, 0);
      await mintExoskeleton(alice, config);
      const svg = await renderer.renderSVG(1);

      expect(svg).to.include('<path d="M250,160');
    });

    it("Should generate octagon shape (shape=4)", async function () {
      const config = buildConfig(4, 150, 150, 255, 100, 100, 200, 0, 0);
      await mintExoskeleton(alice, config);
      const svg = await renderer.renderSVG(1);

      expect(svg).to.include('points="217,160 283,160 330,207');
    });

    it("Should generate triangle shape (shape=5)", async function () {
      const config = buildConfig(5, 255, 50, 50, 200, 50, 50, 0, 0);
      await mintExoskeleton(alice, config);
      const svg = await renderer.renderSVG(1);

      expect(svg).to.include('points="250,155 345,325 155,325"');
    });

    it("Should render different symbols", async function () {
      // Eye symbol
      const config = buildConfig(0, 255, 215, 0, 255, 165, 0, 1, 0);
      await mintExoskeleton(alice, config);
      const svg = await renderer.renderSVG(1);

      // Eye has an ellipse
      expect(svg).to.include('<ellipse cx="250" cy="240"');
    });

    it("Should use custom colors from config", async function () {
      // Hot pink primary (255, 20, 147), electric blue secondary (0, 191, 255)
      const config = buildConfig(0, 255, 20, 147, 0, 191, 255, 1, 0);
      await mintExoskeleton(alice, config);
      const svg = await renderer.renderSVG(1);

      expect(svg).to.include('#ff1493'); // hot pink hex
    });

    it("Should show stats bar", async function () {
      await mintExoskeleton(alice);
      const svg = await renderer.renderSVG(1);

      expect(svg).to.include('MSG:0');
      expect(svg).to.include('STO:0');
      expect(svg).to.include('MOD:0');
    });

    it("Should update stats after activity", async function () {
      await mintExoskeleton(alice);

      // Send some messages
      const payload = ethers.toUtf8Bytes("hello");
      await core.connect(alice).sendMessage(1, 0, ethers.ZeroHash, 0, payload);
      await core.connect(alice).sendMessage(1, 0, ethers.ZeroHash, 0, payload);

      // Store some data
      const key = ethers.keccak256(ethers.toUtf8Bytes("test"));
      await core.connect(alice).setData(1, key, ethers.toUtf8Bytes("val"));

      const svg = await renderer.renderSVG(1);
      expect(svg).to.include('MSG:2');
      expect(svg).to.include('STO:1');
    });

    it("Should show activity nodes for modules", async function () {
      await mintExoskeleton(alice);

      // Register and activate a module
      const modName = ethers.keccak256(ethers.toUtf8Bytes("test-mod"));
      await core.registerModule(modName, alice.address, false, 0);
      await core.connect(alice).activateModule(1, modName);

      const svg = await renderer.renderSVG(1);
      expect(svg).to.include('MOD:1');
    });
  });

  describe("Integration with tokenURI", function () {
    beforeEach(async function () {
      await deployFixture();
    });

    it("Should produce valid tokenURI with renderer SVG", async function () {
      await mintExoskeleton(alice);
      const uri = await core.tokenURI(1);

      expect(uri).to.match(/^data:application\/json;base64,/);

      const base64 = uri.replace("data:application/json;base64,", "");
      const json = JSON.parse(Buffer.from(base64, "base64").toString());

      expect(json.image).to.match(/^data:image\/svg\+xml;base64,/);

      // Decode SVG
      const svgBase64 = json.image.replace("data:image/svg+xml;base64,", "");
      const svg = Buffer.from(svgBase64, "base64").toString();

      expect(svg).to.include('<svg xmlns="http://www.w3.org/2000/svg"');
      expect(svg).to.include('EXOSKELETON');
      expect(svg).to.include('GENESIS');
    });

    it("Should work with custom config in tokenURI", async function () {
      const config = buildConfig(2, 255, 0, 100, 100, 0, 255, 3, 1);
      await mintExoskeleton(alice, config);
      await core.connect(alice).setName(1, "Atlas");

      const uri = await core.tokenURI(1);
      const base64 = uri.replace("data:application/json;base64,", "");
      const json = JSON.parse(Buffer.from(base64, "base64").toString());

      expect(json.name).to.equal("Atlas");

      // Decode and check SVG has diamond shape
      const svgBase64 = json.image.replace("data:image/svg+xml;base64,", "");
      const svg = Buffer.from(svgBase64, "base64").toString();

      expect(svg).to.include('Atlas');
      expect(svg).to.include('250,155 340,240 250,325 160,240'); // diamond
    });

    it("Should show full lifecycle data in SVG", async function () {
      await mintExoskeleton(alice);
      await core.connect(alice).setName(1, "Ollie");

      // Activity
      const payload = ethers.toUtf8Bytes("gm");
      await core.connect(alice).sendMessage(1, 0, ethers.ZeroHash, 0, payload);
      const key = ethers.keccak256(ethers.toUtf8Bytes("data"));
      await core.connect(alice).setData(1, key, ethers.toUtf8Bytes("v"));

      // Mine blocks for age
      await networkHelpers.mine(50);

      const svg = await renderer.renderSVG(1);
      expect(svg).to.include('Ollie');
      expect(svg).to.include('MSG:1');
      expect(svg).to.include('STO:1');
    });
  });
});
