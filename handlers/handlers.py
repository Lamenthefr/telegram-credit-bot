from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import database
import utils
import os
import requests

NOWPAYMENTS_API_KEY = os.getenv("NOWPAYMENTS_API_KEY")

# 📲 Menu de recharge (boutons crypto)
async def recharge_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    username = query.from_user.username

    database.create_user_if_not_exists(user_id, username)
    user = database.get_user(user_id)

    if not user:
        await query.message.reply_text("Erreur lors de la création du profil utilisateur.")
        return

    keyboard = [
        [InlineKeyboardButton("BTC", callback_data='deposit_btc')],
        [InlineKeyboardButton("ETH", callback_data='deposit_eth')],
        [InlineKeyboardButton("LTC", callback_data='deposit_ltc')],
    ]

    text = f"💰 Solde: {user[2]:.2f} €\n\nChoisissez une crypto pour recharger :"
    await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


# 💬 Après clic sur crypto → demander le montant
async def recharge_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    currency = query.data.split('_')[1]
    context.user_data['currency'] = currency
    context.user_data['state'] = 'ASK_AMOUNT'

    await query.message.reply_text(f"💸 Entrez le montant à déposer en {currency.upper()} (minimum 10€) :")


# 🧠 Gestion du message texte pour entrer le montant
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = context.user_data.get('state')
    if state == "ASK_AMOUNT":
        try:
            amount = float(update.message.text)
            if amount >= 10:
                currency = context.user_data['currency']
                await update.message.reply_text(f"🔄 Création de la demande de paiement de {amount:.2f}€ en {currency.upper()}...")

                # Ici tu pourrais ajouter un appel vers une vraie fonction qui génère le lien via NowPayments
                fake_address = f"1FakeAddressFor{currency.upper()}"
                qr_path = utils.generate_qr_code(fake_address)

                await update.message.reply_photo(
                    photo=open(qr_path, 'rb'),
                    caption=f"⚡ Envoyez {amount} {currency.upper()} à :\n`{fake_address}`\n\n⚠️ Le paiement est valide 19 minutes.",
                    parse_mode='Markdown'
                )
                context.user_data['state'] = None
            else:
                await update.message.reply_text("🚫 Le minimum de dépôt est 10€.")
        except ValueError:
            await update.message.reply_text("❌ Veuillez entrer un montant valide.")
    else:
        await update.message.reply_text("❌ Commande non reconnue.")
