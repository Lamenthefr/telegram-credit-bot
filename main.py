import os
import logging
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, ContextTypes
)
from dotenv import load_dotenv
import database
import handlers.handlers as handlers
import handlers.admin as admin_handlers

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    database.create_user_if_not_exists(user.id, user.username)
    welcome_text = (
        f"🔱 Bienvenue @{user.username} !\n\n"
        "Bienvenue sur notre AutoShop Telegram.\n"
        "Vous pouvez ici générer plusieurs types de documents officiels à usage privé, test, formation ou démonstration.\n\n"
        "💳 /recharger — Déposer des fonds en crypto (NowPayments)\n"
        "💼 /solde — Consulter votre solde disponible\n"
        "📄 /generer — Générer un document\n"
        "ℹ️ /info — Voir les documents disponibles et leur description\n\n"
        "⚠️ *Avertissement* : Toute utilisation illégale des documents générés est strictement interdite.\n"
        "Ce service est destiné exclusivement à des fins de test, formation, développement ou démonstration."
    )
    await update.message.reply_markdown(welcome_text)

async def solde(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = database.get_user(user.id)
    if user_data:
        await update.message.reply_text(f"💼 Votre solde est de {user_data[2]:.2f} €")
    else:
        await update.message.reply_text("❌ Erreur lors de la récupération de votre profil.")

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc_info = (
        "📄 *Documents disponibles à la génération* :\n\n"
        "🇫🇷 *France* : Carte ID, Passeport, Permis, Relevé bancaire, EDF, Orange, SFR, Avis d'imposition, Salaire\n"
        "🇺🇸 *USA* : Passeport, Permis, SSN, Bank statement, Utility bill\n"
        "🇬🇧 *UK* : Passeport, Permis, Bank statement, NHS, Factures\n"
        "🇨🇦 *Canada* : Passeport, Permis, Assurance santé, Hydro, Relevé bancaire\n"
        "🇩🇪🇪🇸🇮🇹🇧🇪🇳🇱 Autres pays disponibles : Carte ID, Passeport, Permis\n\n"
        "💡 Tous les documents sont générés en haute qualité et livrés sous 1 minute.\n"
        "🎯 Usage recommandé : tests, développement, formation, démonstration uniquement.\n\n"
        "⚠️ *Avertissement légal* : Toute utilisation frauduleuse ou illégale est strictement interdite.\n"
        "Vous êtes seul responsable de l'usage que vous faites des documents générés."
    )
    await update.message.reply_markdown(doc_info)

async def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("solde", solde))
    application.add_handler(CommandHandler("info", info))
    application.add_handler(CommandHandler("recharger", handlers.recharge_menu))
    application.add_handler(CallbackQueryHandler(handlers.recharge_buttons, pattern="^deposit_"))
    application.add_handler(CommandHandler("generer", handlers.generer_document))
    application.add_handler(CommandHandler("verifier", handlers.check_payment_status))
    application.add_handler(CommandHandler("ajouter_credit", admin_handlers.ajouter_credit))
    application.add_handler(CommandHandler("broadcast", admin_handlers.broadcast))
    application.add_handler(CommandHandler("stats", admin_handlers.stats))
    application.add_handler(MessageHandler(filters.TEXT & filters.User(user_id=None), handlers.handle_message))
    await application.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())