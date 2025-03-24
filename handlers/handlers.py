from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
import os
import utils
import database
import requests

NOWPAYMENTS_API_KEY = os.getenv("NOWPAYMENTS_API_KEY")

async def recharge_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    database.create_user_if_not_exists(user_id, username)
    user = database.get_user(user_id)

    keyboard = [
        [InlineKeyboardButton("BTC", callback_data='deposit_btc')],
        [InlineKeyboardButton("ETH", callback_data='deposit_eth')],
        [InlineKeyboardButton("LTC", callback_data='deposit_ltc')]
    ]
    text = f"💳 Recharger votre compte :\nSolde actuel : {user[2]:.2f} €"
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def recharge_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    currency = query.data.split('_')[1]
    context.user_data['currency'] = currency
    context.user_data['state'] = 'ASK_AMOUNT'

    await query.edit_message_text(
        text=f"🔱 Combien voulez-vous déposer en {currency.upper()} ? (Minimum 10€)"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = context.user_data.get('state')
    if state == "ASK_AMOUNT":
        try:
            amount = float(update.message.text)
            if amount >= 10:
                currency = context.user_data['currency']
                address = f"{currency.upper()}_ADDRESS_HERE"
                qr_path = utils.generate_qr_code(address)

                await update.message.reply_photo(
                    photo=open(qr_path, 'rb'),
                    caption=f"💳 Envoyez {amount} {currency.upper()} à l'adresse suivante :\n`{address}`",
                    parse_mode='Markdown'
                )
                context.user_data['state'] = None
            else:
                await update.message.reply_text("🚫 Le montant minimum est de 10€.")
        except ValueError:
            await update.message.reply_text("❌ Veuillez entrer un montant valide.")
    else:
        await update.message.reply_text("❌ Commande non reconnue.")
