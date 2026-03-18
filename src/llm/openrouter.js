import config from '../gateway/config.js';
import fetch from 'node-fetch'; // Només si node < 18, si no usa global fetch

class LLMClient {
    constructor() {
        this.baseUrl = 'https://openrouter.ai/api/v1/chat/completions';
    }

    async getCompletion(messages, options = {}) {
        await config.init();
        const apiKey = config.openaiApiKey;
        const model = options.model || config.model;

        const response = await fetch(this.baseUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${apiKey}`,
                'HTTP-Referer': 'https://github.com/bielalzina/SEBASTIAN',
                'X-Title': 'SEBASTIAN Agent'
            },
            body: JSON.stringify({
                model: model,
                messages: messages,
                max_tokens: options.maxTokens || 4000
            })
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(`OpenRouter Error: ${err.error?.message || response.statusText}`);
        }

        const data = await response.json();
        return data.choices[0].message;
    }
}

export default new LLMClient();
