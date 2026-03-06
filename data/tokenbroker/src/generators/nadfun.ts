/**
 * Nad.fun Launch Manager
 * 
 * Handles token deployment preparation for nad.fun:
 * 1. Generate token image (SVG)
 * 2. Upload image to nad.fun API
 * 3. Upload metadata to nad.fun API
 * 4. Mine salt for vanity address
 * 
 * For on-chain deployment, use deploy.ts which requires ethers.
 */

import { IdentityOutput } from './identity.js';

/**
 * Nad.fun API base URLs
 */
const NAD_API = {
    mainnet: 'https://api.nadapp.net',
    testnet: 'https://dev-api.nad.fun'
};

/**
 * Token image generation options
 */
export interface ImageGenerationParams {
    /** Token name */
    name: string;
    /** Token ticker */
    ticker: string;
    /** Primary color (hex) */
    color?: string;
    /** Background color (hex) */
    backgroundColor?: string;
    /** Style: 'meme', 'minimal', 'gradient' */
    style?: 'meme' | 'minimal' | 'gradient';
}

/**
 * Uploaded image result
 */
export interface UploadImageResult {
    imageUri: string;
}

/**
 * Uploaded metadata result
 */
export interface UploadMetadataResult {
    metadataUri: string;
}

/**
 * Salt mining result
 */
export interface MineSaltResult {
    salt: string;
    address: string;
    vanity: string;
}

/**
 * Prepared launch data (ready for on-chain deployment)
 */
export interface PreparedLaunch {
    imageUri: string;
    metadataUri: string;
    salt: string;
    saltAddress: string;
}

/**
 * Generates an SVG token image for nad.fun
 */
export function generateTokenImage(params: ImageGenerationParams): string {
    const {
        name,
        ticker,
        color = '#6366f1',
        backgroundColor = '#1e1e2e',
        style = 'meme'
    } = params;

    // Clean name for display
    const displayName = name.toUpperCase();
    const displayTicker = ticker.toUpperCase();

    let svgContent: string;

    if (style === 'meme') {
        svgContent = `
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400">
                <defs>
                    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" style="stop-color:${backgroundColor}"/>
                        <stop offset="100%" style="stop-color:#2d2d44"/>
                    </linearGradient>
                    <radialGradient id="glow" cx="50%" cy="50%" r="50%">
                        <stop offset="0%" style="stop-color:${color};stop-opacity:0.3"/>
                        <stop offset="100%" style="stop-color:${color};stop-opacity:0"/>
                    </radialGradient>
                </defs>
                
                <!-- Background -->
                <rect width="400" height="400" fill="url(#bg)"/>
                <circle cx="200" cy="200" r="180" fill="url(#glow)"/>
                
                <!-- Border -->
                <rect x="20" y="20" width="360" height="360" rx="20" 
                      fill="none" stroke="${color}" stroke-width="4"/>
                
                <!-- Ticker in center -->
                <text x="200" y="180" text-anchor="middle" 
                      fill="${color}" font-family="monospace" font-size="64" font-weight="bold">
                    ${displayTicker}
                </text>
                
                <!-- Name below -->
                <text x="200" y="260" text-anchor="middle" 
                      fill="#ffffff" font-family="sans-serif" font-size="24">
                    ${displayName}
                </text>
                
                <!-- Decorative elements -->
                <circle cx="50" cy="50" r="8" fill="${color}"/>
                <circle cx="350" cy="350" r="8" fill="${color}"/>
                <circle cx="350" cy="50" r="6" fill="${color}" opacity="0.6"/>
                <circle cx="50" cy="350" r="6" fill="${color}" opacity="0.6"/>
            </svg>
        `;
    } else if (style === 'gradient') {
        svgContent = `
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400">
                <defs>
                    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" style="stop-color:#667eea"/>
                        <stop offset="50%" style="stop-color:#764ba2"/>
                        <stop offset="100%" style="stop-color:#f093fb"/>
                    </linearGradient>
                </defs>
                
                <rect width="400" height="400" fill="url(#bg)"/>
                
                <!-- Ticker -->
                <text x="200" y="200" text-anchor="middle" 
                      fill="white" font-family="monospace" font-size="80" font-weight="bold">
                    ${displayTicker}
                </text>
            </svg>
        `;
    } else {
        // Minimal style
        svgContent = `
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400">
                <rect width="400" height="400" fill="${backgroundColor}"/>
                
                <text x="200" y="200" text-anchor="middle" 
                      fill="${color}" font-family="monospace" font-size="72" font-weight="bold">
                    ${displayTicker}
                </text>
                
                <text x="200" y="280" text-anchor="middle" 
                      fill="white" font-family="sans-serif" font-size="20" opacity="0.8">
                    ${displayName}
                </text>
            </svg>
        `;
    }

    return svgContent.trim();
}

/**
 * Uploads token image to nad.fun
 */
export async function uploadImage(
    imageData: string,
    network: 'mainnet' | 'testnet' = 'mainnet'
): Promise<UploadImageResult> {
    const baseUrl = NAD_API[network];

    const response = await fetch(`${baseUrl}/agent/token/image`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            image: imageData
        })
    });

    if (!response.ok) {
        throw new Error(`Failed to upload image: ${response.statusText}`);
    }

    const data = await response.json();
    return {
        imageUri: data.image_uri || data.imageUrl || data.uri
    };
}

/**
 * Uploads token metadata to nad.fun
 */
export async function uploadMetadata(
    identity: IdentityOutput,
    imageUri: string,
    network: 'mainnet' | 'testnet' = 'mainnet'
): Promise<UploadMetadataResult> {
    const baseUrl = NAD_API[network];

    const metadata = {
        name: identity.name,
        description: identity.description,
        image: imageUri,
        symbol: identity.ticker,
        // Nad.fun specific extensions
        attributes: [
            {
                trait_type: 'Generator',
                value: 'TokenBroker v1.02'
            },
            {
                trait_type: 'Type',
                value: 'Memecoin'
            }
        ]
    };

    const response = await fetch(`${baseUrl}/agent/token/metadata`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(metadata)
    });

    if (!response.ok) {
        throw new Error(`Failed to upload metadata: ${response.statusText}`);
    }

    const data = await response.json();
    return {
        metadataUri: data.metadata_uri || data.metadataUrl || data.uri
    };
}

/**
 * Mines salt for vanity address generation
 */
export async function mineSalt(
    name: string,
    network: 'mainnet' | 'testnet' = 'mainnet'
): Promise<MineSaltResult> {
    const baseUrl = NAD_API[network];

    const response = await fetch(`${baseUrl}/agent/salt`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name })
    });

    if (!response.ok) {
        throw new Error(`Failed to mine salt: ${response.statusText}`);
    }

    const data = await response.json();
    return {
        salt: data.salt,
        address: data.address,
        vanity: data.vanity || '7777'
    };
}

/**
 * Prepares all launch data (image, metadata, salt) - no on-chain interaction
 */
export async function prepareLaunch(
    identity: IdentityOutput,
    network: 'mainnet' | 'testnet' = 'mainnet'
): Promise<PreparedLaunch> {
    // Step 1: Generate and upload image
    const svgImage = generateTokenImage({
        name: identity.name,
        ticker: identity.ticker,
        style: 'meme'
    });

    const imageResult = await uploadImage(svgImage, network);
    console.log('Image uploaded:', imageResult.imageUri);

    // Step 2: Upload metadata
    const metadataResult = await uploadMetadata(identity, imageResult.imageUri, network);
    console.log('Metadata uploaded:', metadataResult.metadataUri);

    // Step 3: Mine salt
    const saltResult = await mineSalt(identity.name, network);
    console.log('Salt mined:', saltResult.salt);
    console.log('Token address:', saltResult.address);

    return {
        imageUri: imageResult.imageUri,
        metadataUri: metadataResult.metadataUri,
        salt: saltResult.salt,
        saltAddress: saltResult.address
    };
}

/**
 * Quick prepare - minimal setup for launch
 */
export async function quickPrepare(
    identity: IdentityOutput,
    network: 'mainnet' | 'testnet' = 'mainnet'
): Promise<PreparedLaunch> {
    return prepareLaunch(identity, network);
}
