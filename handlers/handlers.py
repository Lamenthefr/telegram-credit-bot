
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import database
import utils
import os
import requests

NOWPAYMENTS_API_KEY = "5RN4HYV-71DM8RM-QQQF69A-CWAYMM4"

# 🔘 Étape 1 : Choix de crypto
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


# 🔘 Étape 2 : Choix du montant
async def recharge_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    currency = query.data.split('_')[1]
    context.user_data['currency'] = currency
    context.user_data['state'] = 'ASK_AMOUNT'

    await query.message.reply_text(
        f"💸 Entrez le montant à déposer en {currency.upper()} (minimum 10€) :"
    )


# 🔘 Étape 3 : L'utilisateur entre un montant → appel API NowPayments
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = context.user_data.get('state')
    if state == "ASK_AMOUNT":
        try:
            amount = float(update.message.text)
            if amount < 10:
                await update.message.reply_text("🚫 Le minimum de dépôt est de 10€.")
                return

            currency = context.user_data.get('currency', 'btc')
            user_id = update.effective_user.id

            # 🔌 Appel à NowPayments
            headers = {
                'x-api-key': NOWPAYMENTS_API_KEY,
                'Content-Type': 'application/json'
            }
            data = {
                'price_amount': amount,
                'price_currency': 'eur',
                'pay_currency': currency.lower(),
                'order_description': f'Deposit user {user_id}'
            }

            response = requests.post('https://api.nowpayments.io/v1/payment', json=data, headers=headers)
            res = response.json()

            if 'pay_address' not in res:
                await update.message.reply_text("❌ Erreur : Impossible de créer l'adresse de paiement. Réessayez.")
                return

            pay_address = res['pay_address']
            pay_amount = res['pay_amount']

            # 🧾 Génération du QR code temporaire
            qr_path = utils.generate_qr_code(pay_address)

            # 📤 Envoi au user
            await update.message.reply_photo(
                photo=open(qr_path, 'rb'),
                caption=(
                    f"✅ Adresse générée pour dépôt :\n"
                    f"`{pay_address}`\n\n"
                    f"💸 Montant exact : *{pay_amount} {currency.upper()}*\n\n"
                    f"⏱️ Paiement valide pendant environ 20 minutes."
                ),
                parse_mode="Markdown"
            )

            context.user_data['state'] = None

            # ❌ Optionnel : supprimer le fichier après envoi (si tu veux pas le garder)
            try:
                os.remove(qr_path)
            except:
                pass

        except ValueError:
            await update.message.reply_text("❌ Veuillez entrer un montant valide.")
    else:
        await update.message.reply_text(
            "❌ Commande non reconnue. Cliquez sur *Recharger* puis choisissez une crypto.",
            parse_mode="Markdown"
        )
