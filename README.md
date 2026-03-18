# SEBASTIAN 🕰️
**Agent d'IA Autònom (Arquitectura OpenClaw)**

SEBASTIAN és un "digital worker" local-first, dissenyat per Gabriel, amb capacitats de raonament (ReAct loop), acció directa (eines en Python) i memòria persistent.

## 🚀 Inici Ràpid

1. **Configuració**:
   - Edita el fitxer `.env` i afegeix la teva `OPENROUTER_API_KEY`.
   - Si utilitzes Telegram, afegeix el teu `TELEGRAM_BOT_TOKEN`.

2. **Inici**:
   ```powershell
   python bin/sebastian.py doctor # Diagnòstic
   python bin/sebastian.py start  # Inicia WebSocket Server (Port 18789)
   ```

## 🛠️ Eines Inclòs (Skills)
- `shell`: Execució PowerShell.
- `file_ops`: Manipulació de fitxers al workspace.
- `web_search`: Cerca web sense API key.

## 🧠 Arquitectura "Lobster-Tank"
- **Central Gateway**: Motor ReAct en Python amb inferència via OpenRouter (Claude 3.5 Sonnet / Gemini 2.0 Flash).
- **Workspace**: Memòria basada en fitxers Markdown (`workspace/`).
- **Heartbeat**: Tasques periòdiques (cada 30 minuts) llegides de `HEARTBEAT.md`.

## 🔒 Seguretat
- Mode Sandbox: `off` (per defecte).
- `PAIRING`: Només usuaris autoritzats a `TELEGRAM_ALLOWED_USERS`.