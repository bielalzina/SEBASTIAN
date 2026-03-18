import sys
import logging
import asyncio
from typing import List, Dict, Any, Optional
from telegram import Update, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from src.gateway.core import SebastianGateway, settings

# Configuració de logs
logging.basicConfig(level=logging.ERROR) # Reduir logs per no saturar
logger = logging.getLogger("SEBASTIAN-Telegram")

class TelegramAdapter:
    def __init__(self, gateway: SebastianGateway):
        self.gateway = gateway
        self.app = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()
        self.allowed_users = eval(settings.TELEGRAM_ALLOWED_USERS)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if user_id not in self.allowed_users:
            await update.message.reply_text(f"❌ Accés denegat. El teu ID d'usuari és: {user_id}. Si us plau, demana autorització.")
            return
        
        await update.message.reply_text("👋 Hola Gabriel! Soc en SEBASTIAN, el teu agent d'IA autònom. En què et puc ajudar avui?")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if user_id not in self.allowed_users:
            return

        text = update.message.text
        session_id = f"telegram-{user_id}"
        
        # Mostrar que està pensant
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        response = await self.gateway.process_message(session_id, text)
        await update.message.reply_text(response)

    def run(self):
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self.handle_message))
        
        logger.info("Bot de Telegram iniciat...")
        self.app.run_polling()

if __name__ == "__main__":
    if settings.TELEGRAM_BOT_TOKEN == "PENDING" or not settings.TELEGRAM_BOT_TOKEN:
        print("\n⚠️ ERROR: Falta el TELEGRAM_BOT_TOKEN al fitxer .env\n")
        sys.exit(1)

    print("\n🚀 Iniciant SEBASTIAN Telegram Adapter...")
    gateway = SebastianGateway()
    adapter = TelegramAdapter(gateway)
    adapter.run()
