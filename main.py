
import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
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
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    database.create_user_if_not_exists(user.id, user.username)

    text = (
        f"Bonjour {user.first_name} !

"
        f"ID utilisateur : {user.id}
"
        f"Nom d'utilisateur : @{user.username}

"
        "Bienvenue dans notre AutoShop de documents. Voici ce que vous pouvez faire :"
    )

    keyboard = [
        [InlineKeyboardButton("💳 Recharger", callback_data="menu_recharger")],
        [InlineKeyboardButton("💼 Solde", callback_data="menu_solde")],
        [InlineKeyboardButton("🔢 Infos", callback_data="menu_info")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, reply_markup=reply_markup)

async def solde(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = database.get_user(user.id)
    if user_data:
        await update.message.reply_text(f"💼 Solde actuel : {user_data[2]:.2f} €")
    else:
        await update.message.reply_text("❌ Utilisateur non trouvé.")

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "📄 *Documents disponibles* :

"
        "🇫🇷 France : Carte ID, Passeport, EDF, Banque, etc.
"
        "🇺🇸 USA : SSN, Factures, Bank Statement
"
        "🇬🇧 UK, 🇨🇦 Canada, 🇩🇪 Allemagne, etc.

"
        "🧾 Pour usage test, démo, développement uniquement."
    )
    await update.message.reply_markdown(msg)

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    await query.answer()

    if data == "menu_recharger":
        await handlers.recharge_menu(update, context)
    elif data == "menu_solde":
        user = update.effective_user
        user_data = database.get_user(user.id)
        if user_data:
            await query.message.reply_text(f"💼 Votre solde : {user_data[2]:.2f} €")
        else:
            await query.message.reply_text("❌ Utilisateur non trouvé.")
    elif data == "menu_info":
        await query.message.reply_text(
            "📄 *Documents disponibles* :

"
            "🇫🇷 France : Carte ID, Passeport, EDF, etc.
"
            "🇺🇸 USA : SSN, Relevé bancaire
"
            "🇬🇧 UK, 🇨🇦 Canada...
",
            parse_mode='Markdown'
        )

async def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("solde", solde))
    application.add_handler(CommandHandler("info", info))
    application.add_handler(CommandHandler("recharger", handlers.recharge_menu))

    application.add_handler(CallbackQueryHandler(handle_buttons))
    application.add_handler(CallbackQueryHandler(handlers.recharge_buttons, pattern="^deposit_"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_message))

    application.add_handler(CommandHandler("ajouter_credit", admin_handlers.ajouter_credit))
    application.add_handler(CommandHandler("broadcast", admin_handlers.broadcast))
    application.add_handler(CommandHandler("stats", admin_handlers.stats))

    logging.info("✅ Bot lancé avec succès.")
    await application.run_polling()

if __name__ == "__main__":
    import asyncio
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.get_event_loop().run_until_complete(main())
