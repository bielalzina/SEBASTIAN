import config from './config.js';
import fs from 'fs/promises';
import path from 'path';

class ContextAssembler {
    constructor() {
        this.systemFiles = ['SOUL.md', 'AGENTS.md', 'IDENTITY.md', 'USER.md', 'TOOLS.md', 'MEMORY.md'];
    }

    async assemble(messages = []) {
        await config.init();
        const workspacePath = config.workspacePath;
        let systemPrompt = "Ets en SEBASTIAN, un agent d'IA autònom.\n\n";

        for (const file of this.systemFiles) {
            try {
                const filePath = path.join(workspacePath, file);
                const content = await fs.readFile(filePath, 'utf8');
                systemPrompt += `--- ${file} ---\n${content}\n\n`;
            } catch (err) {
                console.warn(`No s'ha pogut llegir ${file}: ${err.message}`);
            }
        }

        return [
            { role: 'system', content: systemPrompt },
            ...messages
        ];
    }
}

export default new ContextAssembler();
