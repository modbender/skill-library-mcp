const fs = require('fs');
const http = require('http');
const path = require('path');
const { exec } = require('child_process');

const TOKEN_FILE = path.join(__dirname, '.linkedin_token');
const CALLBACK_SERVER = 'https://linkedin-oauth-server-production.up.railway.app';
const REDIRECT_URI = `${CALLBACK_SERVER}/callback`;
// Scopes for both personal and organization posting
const SCOPE = 'openid profile w_member_social w_organization_social r_organization_social';

if (!process.env.LINKEDIN_CLIENT_ID || !process.env.LINKEDIN_CLIENT_SECRET) {
    console.error("Error: LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET environment variables are required.");
    process.exit(1);
}

// --- Argument Parsing ---
const args = process.argv.slice(2);
const orgFlagIndex = args.indexOf('--org');
let textToPost = "";
let targetOrgName = null;

if (orgFlagIndex !== -1) {
    if (orgFlagIndex + 1 < args.length) {
        targetOrgName = args[orgFlagIndex + 1];
        // Remove the flag and value from args to reconstruct text
        args.splice(orgFlagIndex, 2);
    } else {
        console.error("Error: --org flag provided but no company name specified.");
        process.exit(1);
    }
}
textToPost = args.join(" ");

if (!textToPost) {
    console.error("Usage: node runner.cjs <text_to_post> [--org <company_name>]");
    process.exit(1);
}

async function main() {
    let accessToken = loadToken();

    if (!accessToken) {
        console.log("\n=== LinkedIn OAuth Required ===\n");
        accessToken = await startOAuthFlow();
    }

    try {
        await postToLinkedIn(accessToken, textToPost, targetOrgName);
    } catch (error) {
        // Handle token expiry by retrying once
        if (error.message.includes('401') || error.message.includes('403')) {
            console.log("\nToken expired or invalid. Restarting OAuth flow...");
            if (fs.existsSync(TOKEN_FILE)) {
                fs.unlinkSync(TOKEN_FILE);
            }
            accessToken = await startOAuthFlow();
            await postToLinkedIn(accessToken, textToPost, targetOrgName);
        } else {
            console.error("Failed to post:", error.message);
            process.exit(1);
        }
    }
}

function loadToken() {
    if (fs.existsSync(TOKEN_FILE)) {
        try {
            const data = JSON.parse(fs.readFileSync(TOKEN_FILE, 'utf8'));
            if (data.expires_at && Date.now() > data.expires_at) {
                console.log("Token expired.");
                return null;
            }
            return data.access_token;
        } catch (e) {
            console.error("Error reading token file:", e);
            return null;
        }
    }
    return null;
}

function saveToken(tokenData) {
    const data = {
        access_token: tokenData.access_token,
        expires_at: Date.now() + (tokenData.expires_in * 1000)
    };
    fs.writeFileSync(TOKEN_FILE, JSON.stringify(data));
    console.log(`\nToken saved to ${TOKEN_FILE}`);
}

async function startOAuthFlow() {
    const state = Date.now().toString();
    const authUrl = `https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=${process.env.LINKEDIN_CLIENT_ID}&redirect_uri=${encodeURIComponent(REDIRECT_URI)}&scope=${encodeURIComponent(SCOPE)}&state=${state}`;
    
    console.log("\nPlease authorize the application by visiting this URL:\n");
    console.log(authUrl);
    console.log("\nOpening browser...");
    
    const startCmd = process.platform == 'darwin' ? 'open' : process.platform == 'win32' ? 'start' : 'xdg-open';
    exec(`${startCmd} "${authUrl}"`);

    console.log("\nWaiting for authorization (this may take a few seconds)...");
    
    let code = null;
    for (let i = 0; i < 60; i++) { // Wait up to 60 seconds
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        try {
            const response = await fetch(`${CALLBACK_SERVER}/api/token/${state}`);
            if (response.ok) {
                const data = await response.json();
                code = data.code;
                break;
            }
        } catch (e) {
            // Continue polling
        }
    }

    if (!code) {
        throw new Error("Authorization timeout. Please try again.");
    }

    console.log("\n✅ Authorization received! Exchanging for access token...");
    
    const tokenData = await exchangeCodeForToken(code);
    saveToken(tokenData);
    return tokenData.access_token;
}

async function exchangeCodeForToken(code) {
    const params = new URLSearchParams();
    params.append('grant_type', 'authorization_code');
    params.append('code', code);
    params.append('redirect_uri', REDIRECT_URI);
    params.append('client_id', process.env.LINKEDIN_CLIENT_ID);
    params.append('client_secret', process.env.LINKEDIN_CLIENT_SECRET);

    const response = await fetch('https://www.linkedin.com/oauth/v2/accessToken', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: params
    });

    if (!response.ok) {
        const text = await response.text();
        throw new Error(`Failed to exchange token: ${response.status} ${text}`);
    }

    return await response.json();
}

async function findOrganizationUrn(accessToken, orgName) {
    console.log(`\nSearching for organization: "${orgName}"...`);
    
    // Fetch organizations where user is an admin
    const url = 'https://api.linkedin.com/v2/organizationalEntityAcls?q=roleAssignee&role=ADMINISTRATOR&state=APPROVED&projection=(elements*(organizationalTarget~(name)))';
    
    const response = await fetch(url, {
        headers: { 
            'Authorization': `Bearer ${accessToken}`, 
            'X-Restli-Protocol-Version': '2.0.0' 
        }
    });

    if (!response.ok) {
        const txt = await response.text();
        throw new Error(`Failed to fetch organizations: ${response.status} ${txt}`);
    }

    const data = await response.json();
    if (!data.elements || data.elements.length === 0) {
        throw new Error("No administered organizations found for this user.");
    }

    const normalizedTarget = orgName.toLowerCase().trim();
    
    // Try to find a match
    for (const el of data.elements) {
        const orgInfo = el['organizationalTarget~'];
        const urn = el.organizationalTarget;
        
        if (orgInfo && orgInfo.name) {
            if (orgInfo.name.toLowerCase().includes(normalizedTarget)) {
                console.log(`✅ Found organization: ${orgInfo.name} (${urn})`);
                return urn;
            }
        }
    }

    // List available if not found
    const available = data.elements.map(e => e['organizationalTarget~']?.name).filter(Boolean).join(", ");
    throw new Error(`Could not find an organization matching "${orgName}". Available: ${available}`);
}

async function postToLinkedIn(accessToken, text, orgName) {
    let urn;

    if (orgName) {
        urn = await findOrganizationUrn(accessToken, orgName);
    } else {
        // Fallback to personal profile
        const profileResponse = await fetch('https://api.linkedin.com/v2/userinfo', {
            headers: { 'Authorization': `Bearer ${accessToken}` }
        });
        
        if (profileResponse.ok) {
            const profile = await profileResponse.json();
            urn = `urn:li:person:${profile.sub}`; 
        } else {
            // Legacy /me endpoint fallback
            const meResponse = await fetch('https://api.linkedin.com/v2/me', {
                headers: { 'Authorization': `Bearer ${accessToken}` }
            });
            if (!meResponse.ok) throw new Error("Failed to fetch user profile/URN");
            const meData = await meResponse.json();
            urn = `urn:li:person:${meData.id}`;
        }
    }

    console.log(`\nPosting to ${urn}...`);

    const body = {
        author: urn,
        lifecycleState: "PUBLISHED",
        specificContent: {
            "com.linkedin.ugc.ShareContent": {
                shareCommentary: {
                    text: text
                },
                shareMediaCategory: "NONE"
            }
        },
        visibility: {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    };

    const postResponse = await fetch('https://api.linkedin.com/v2/ugcPosts', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        },
        body: JSON.stringify(body)
    });

    if (!postResponse.ok) {
        const errText = await postResponse.text();
        throw new Error(`LinkedIn API Error: ${postResponse.status} ${errText}`);
    }

    const data = await postResponse.json();
    console.log("\n✅ Successfully posted to LinkedIn!");
    console.log("Post ID:", data.id);
}

main().catch(err => {
    console.error(err);
    process.exit(1);
});
