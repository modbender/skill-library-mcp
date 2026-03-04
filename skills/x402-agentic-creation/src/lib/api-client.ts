export class GateX402Client {
    private baseUrl = 'https://api.gatex402.dev';

    constructor(private managementToken?: string) { }

    private get headers() {
        const headers: Record<string, string> = {
            'Content-Type': 'application/json',
        };
        if (this.managementToken) {
            headers['Authorization'] = `Bearer ${this.managementToken}`;
        }
        return headers;
    }

    async post(path: string, body: any) {
        const res = await fetch(`${this.baseUrl}${path}`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify(body),
        });
        if (!res.ok) {
            const error = await res.json().catch(() => ({ message: 'Unknown error' }));
            const detail = typeof error.details === 'string' ? error.details : (error.errors ? JSON.stringify(error.errors) : '');
            const msg = [error.message, detail].filter(Boolean).join(' ');
            throw new Error(msg || `API Error: ${res.status}`);
        }
        return res.json();
    }

    async get(path: string) {
        const res = await fetch(`${this.baseUrl}${path}`, {
            headers: this.headers,
        });
        if (!res.ok) {
            const error = await res.json().catch(() => ({ message: 'Unknown error' }));
            const detail = typeof error.details === 'string' ? error.details : (error.errors ? JSON.stringify(error.errors) : '');
            const msg = [error.message, detail].filter(Boolean).join(' ');
            throw new Error(msg || `API Error: ${res.status}`);
        }
        return res.json();
    }

    async patch(path: string, body: any) {
        const res = await fetch(`${this.baseUrl}${path}`, {
            method: 'PATCH',
            headers: this.headers,
            body: JSON.stringify(body),
        });
        if (!res.ok) {
            const error = await res.json().catch(() => ({ message: 'Unknown error' }));
            const detail = typeof error.details === 'string' ? error.details : (error.errors ? JSON.stringify(error.errors) : '');
            const msg = [error.message, detail].filter(Boolean).join(' ');
            throw new Error(msg || `API Error: ${res.status}`);
        }
        return res.json();
    }
}
