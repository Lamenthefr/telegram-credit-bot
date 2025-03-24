import os
import logging
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)
from dotenv import load_dotenv
import database
import handlers.handlers as handlers
import handlers.admin as admin_handlers

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    database.create_user_if_not_exists(user.id, user.username)
    text = (
        f"🔱 Bienvenue @{user.username} !\n\n"
        "Bienvenue sur notre AutoShop Telegram.\n"
        "Vous pouvez ici générer plusieurs types de documents officiels à usage privé, test ou formation.\n\n"
        "💳 /recharger — Déposer des fonds en crypto\n"
        "💼 /solde — Voir votre solde\n"
        "📄 /generer — Générer un document\n"
        "ℹ️ /info — Liste des documents disponibles\n"
        "❌ /cancel — Annuler une action\n\n"
        "⚠️ *Avertissement* : L'utilisation illégale des documents générés est strictement interdite."
    )
    await update.message.reply_markdown(text)

async def solde(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = database.get_user(user.id)
    if user_data:
        await update.message.reply_text(f"💼 Solde actuel : {user_data[2]:.2f} €")
    else:
        await update.message.reply_text("❌ Utilisateur non trouvé.")

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "📄 *Documents disponibles* :\n\n"
        "🇫🇷 France : Carte ID, Passeport, Relevé bancaire, EDF, etc.\n"
        "🇺🇸 USA : SSN, Bank statement, Factures\n"
        "🇬🇧 UK, 🇨🇦 Canada, 🇩🇪 Allemagne, etc.\n\n"
        "🧾 Livraison rapide, format PDF ou image.\n"
        "🎯 Usage : test, dev, formation uniquement."
    )
    await update.message.reply_markdown(msg)

async def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("solde", solde))
    application.add_handler(CommandHandler("info", info))
    application.add_handler(CommandHandler("recharger", handlers.recharge_menu))
    application.add_handler(CallbackQueryHandler(handlers.recharge_buttons, pattern="^deposit_"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_message))

    # Admin
    application.add_handler(CommandHandler("ajouter_credit", admin_handlers.ajouter_credit))
    application.add_handler(CommandHandler("broadcast", admin_handlers.broadcast))
    application.add_handler(CommandHandler("stats", admin_handlers.stats))

    await application.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
