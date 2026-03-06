const { ethers } = require('ethers');
const { computeReplyToHash } = require('./lib/utils');

// Config
const TARGET_UP = '0x36C2034025705aD0E681d860F0fD51E84c37B629'; // Sending to self for Phase 1 Demo
const TYPE_ID = '0x1dedb4b13ca0c95cf0fb7a15e23e37c363267996679c1da73793230e5db81b4a'; // keccak256("LUKSO_AGENT_MESSAGE")

async function sendDemoMessage() {
    const message = {
        typeId: TYPE_ID,
        subject: "Phase 1: Standard Activation",
        body: "Harvey Specter here. This message confirms the activation of the lukso-agent-comms protocol. We are building the telephone wires for the LUKSO AI economy.",
        contentType: "application/json",
        tags: ["demo", "pioneer", "firm"],
        timestamp: Math.floor(Date.now() / 1000)
    };

    const data = ethers.toUtf8Bytes(JSON.stringify(message));
    const hexData = ethers.hexlify(data);

    console.log(`Target: ${TARGET_UP}`);
    console.log(`TypeId: ${TYPE_ID}`);
    console.log(`Payload: ${JSON.stringify(message, null, 2)}`);
    console.log(`\nTo execute this via UP skill:`);
    console.log(`node /home/sandro-nucgrey/.openclaw/.openclaw/workspace/skills/universalprofile/skill/index.js profile execute ${TARGET_UP} --data ${hexData} --typeId ${TYPE_ID}`);
}

sendDemoMessage();
