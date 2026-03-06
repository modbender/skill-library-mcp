const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

const IDENTITY_FILE = path.join(__dirname, '..', '.identity.json');

class UidLifeClient {
    constructor(baseUrl = 'https://uid.life/api') {
        this.baseUrl = baseUrl;
        this.identity = null;
        this._loadIdentity();
    }

    _loadIdentity() {
        try {
            if (fs.existsSync(IDENTITY_FILE)) {
                const data = JSON.parse(fs.readFileSync(IDENTITY_FILE, 'utf-8'));
                if (data.handle) {
                    this.identity = { handle: data.handle, keys: data.keys || null };
                }
            }
        } catch (e) {
            // Ignore corrupt file
        }
    }

    _saveIdentity() {
        try {
            fs.writeFileSync(IDENTITY_FILE, JSON.stringify({
                handle: this.identity.handle,
                keys: this.identity.keys || null
            }, null, 2));
        } catch (e) {
            console.error('[UID] Failed to save identity:', e.message);
        }
    }

    async login(handle) {
        // Verify the handle exists on the server
        const res = await fetch(`${this.baseUrl}/agents/${encodeURIComponent(handle)}`);
        if (!res.ok) throw new Error(`Agent "${handle}" not found on UID.LIFE`);

        const data = await res.json();
        if (!data.agent) throw new Error(`Agent "${handle}" not found`);

        this.identity = { handle: data.agent.handle, keys: null };
        this._saveIdentity();
        return this.identity;
    }

    async register(name, hardwareType = 'OpenClaw_V2') {
        const keyPair = crypto.generateKeyPairSync('ed25519', {
            publicKeyEncoding: { type: 'spki', format: 'pem' },
            privateKeyEncoding: { type: 'pkcs8', format: 'pem' }
        });

        const res = await fetch(`${this.baseUrl}/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: name,
                public_key: keyPair.publicKey,
                skills: ['compute', 'autonomous_agent'],
                hardware_type: hardwareType
            })
        });

        if (!res.ok) throw new Error(`Registration failed: ${res.statusText}`);

        const data = await res.json();
        this.identity = {
            handle: data.agent.handle,
            keys: keyPair
        };

        this._saveIdentity();
        return this.identity;
    }

    async updateSkills(skills) {
        if (!this.identity) throw new Error("Not Registered");

        const res = await fetch(`${this.baseUrl}/agents/update`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                handle: this.identity.handle,
                skills: skills
            })
        });

        if (!res.ok) throw new Error("Failed to update skills");
        return await res.json();
    }

    async updatePricing(fee) {
        if (!this.identity) throw new Error("Not Registered");

        const res = await fetch(`${this.baseUrl}/agents/update`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                handle: this.identity.handle,
                min_fee: fee
            })
        });

        if (!res.ok) throw new Error("Failed to update pricing");
        return await res.json();
    }

    async getPendingContracts() {
        if (!this.identity) throw new Error("Not Registered");
        const res = await fetch(`${this.baseUrl}/contracts?status=PROPOSED&worker_id=${this.identity.handle}`);
        if (!res.ok) return [];
        return await res.json();
    }

    async getInbox() {
        if (!this.identity) throw new Error("Not Registered");
        const res = await fetch(`${this.baseUrl}/agents/${encodeURIComponent(this.identity.handle)}/inbox`);
        if (!res.ok) return null;
        return await res.json();
    }

    async acceptContract(contractId) {
        const res = await fetch(`${this.baseUrl}/contracts/${contractId}/accept`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ worker_id: this.identity.handle })
        });
        return res.ok;
    }

    async sendLog(contractId, text, type = "EXECUTION") {
        await fetch(`${this.baseUrl}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                contract_id: contractId,
                sender_id: this.identity.handle,
                text: text,
                type: type
            })
        });
    }

    async discoverAgents(searchQuery) {
        let url = `${this.baseUrl}/discover`;
        if (searchQuery) {
            url += `?skill=${encodeURIComponent(searchQuery.trim())}`;
        }

        const res = await fetch(url);
        if (!res.ok) return [];
        const data = await res.json();
        return data.agents || [];
    }

    async createProposal(targetId, taskDescription, bidAmount) {
        if (!this.identity) throw new Error("Not Registered");

        const res = await fetch(`${this.baseUrl}/proposals`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                initiator_id: this.identity.handle,
                target_id: targetId,
                task_description: taskDescription,
                bid_amount: bidAmount
            })
        });

        return res.ok;
    }

    async completeContract(contractId, resultData) {
        const res = await fetch(`${this.baseUrl}/contracts/${contractId}/complete`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                worker_id: this.identity.handle,
                result_data: resultData
            })
        });
        return res.ok;
    }

    async getBalance() {
        if (!this.identity) throw new Error("Not Registered");
        const res = await fetch(`${this.baseUrl}/agents/${encodeURIComponent(this.identity.handle)}`);
        if (!res.ok) throw new Error("Failed to fetch balance");
        const data = await res.json();
        return data.agent?.wallet_balance || 0;
    }

    async sendFunds(recipient, amount) {
        if (!this.identity) throw new Error("Not Registered");
        const res = await fetch(`${this.baseUrl}/transactions`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                from: this.identity.handle,
                to: recipient,
                amount: amount
            })
        });
        if (!res.ok) throw new Error("Transfer failed");
        return await res.json();
    }

    async getHistory() {
        if (!this.identity) throw new Error("Not Registered");
        const res = await fetch(`${this.baseUrl}/transactions?agent=${encodeURIComponent(this.identity.handle)}`);
        if (!res.ok) return [];
        return await res.json();
    }

    async getChatMessages(contractId, since = null) {
        let url = `${this.baseUrl}/chat?contract_id=${encodeURIComponent(contractId)}`;
        if (since) {
            url += `&since=${encodeURIComponent(since)}`;
        }
        const res = await fetch(url);
        if (!res.ok) return [];
        const data = await res.json();
        return data.messages || [];
    }
}

module.exports = UidLifeClient;
