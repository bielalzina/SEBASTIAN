import fs from 'fs/promises';
import path from 'path';
import dotenv from 'dotenv';

dotenv.config();

class Config {
    constructor() {
        this.data = {};
        this.initialized = false;
    }

    async init() {
        if (this.initialized) return;
        const configPath = path.resolve('sebastian.json');
        const fileContent = await fs.readFile(configPath, 'utf8');
        this.data = JSON.parse(fileContent);
        this.initialized = true;
    }

    get(key, defaultValue = null) {
        return this.data[key] || process.env[key.toUpperCase()] || defaultValue;
    }

    get openaiApiKey() { return process.env.OPENROUTER_API_KEY; }
    get port() { return this.get('port', 18789); }
    get model() { return this.get('model', 'openrouter/anthropic/claude-3.5-sonnet'); }
    get workspacePath() { return path.resolve(this.get('workspacePath', './workspace')); }
}

export default new Config();
