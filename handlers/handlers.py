
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ContextTypes
import database
import utils
import requests
import qrcode
import threading
import time
import telegram
import os

NOWPAYMENTS_API_KEY = os.getenv("NOWPAYMENTS_API_KEY")

# --- MENU PRINCIPAL ---

def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    data = query.data

    if data == 'profile':
        show_profile(query)
    elif data == 'shop':
        show_shop(query)
    elif data == 'deposit':
        show_deposit_options(query)
    elif data == 'retry_deposit':
        retry_deposit(update, context)
    else:
        print(f"Commande inconnue : {data}")

# --- PROFIL ---

def show_profile(query):
    user = database.get_user(query.from_user.id)
    query.edit_message_text(
        text=(
            f"🔱 Nom d'utilisateur: @{user[1]}
"
            f"🔱 Votre ID: {user[0]}
"
            f"🔱 Grade: Membre
"
            f"🔱 Solde: {user[2]:.2f}€
"
            f"🔱 Dépôts Total: {user[3]:.2f}$"
        ),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠 Accueil", callback_data='start')]
        ])
    )

# --- SHOP ---

def show_shop(query):
    products = database.get_products()
    keyboard = [
        [InlineKeyboardButton(f"{p['name']} (Stock: {p['stock']})", callback_data=f"buy_{p['id']}")]
        for p in products
    ]
    keyboard.append([InlineKeyboardButton("🏠 Accueil", callback_data='start')])
    query.edit_message_text(
        text="🔱 HORUS SHOP 🔱
Choisissez un produit ci-dessous.
Contact support : @horus_tlg",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# --- DÉPÔT CRYPTO ---

def show_deposit_options(query):
    user = database.get_user(query.from_user.id)
    keyboard = [
        [InlineKeyboardButton("BTC", callback_data='deposit_btc')],
        [InlineKeyboardButton("ETH", callback_data='deposit_eth')],
        [InlineKeyboardButton("LTC", callback_data='deposit_ltc')],
        [InlineKeyboardButton("🏠 Accueil", callback_data='start')]
    ]
    query.edit_message_text(
        text=f"🔱 Salut, @{user[1]} !
💰 Solde: {user[2]:.2f}€
Choisissez une crypto pour recharger :",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def recharge_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    query.answer()
    currency = query.data.split('_')[1]
    context.user_data['currency'] = currency
    context.user_data['state'] = 'ASK_AMOUNT'

    await query.message.reply_text(
        f"💸 Entrez le montant à déposer en {currency.upper()} (minimum 10€) :",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Retour", callback_data="deposit")],
            [InlineKeyboardButton("🏠 Accueil", callback_data="start")]
        ])
    )

def retry_deposit(update: Update, context: CallbackContext):
    query = update.callback_query
    ask_deposit_amount(query, context.user_data.get('currency'), context)

def ask_deposit_amount(query, currency, context):
    context.user_data['currency'] = currency
    context.user_data['state'] = 'ASK_AMOUNT'
    query.edit_message_text(
        text="💸 Entrez le montant à déposer (minimum 10€) :",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Retour", callback_data="deposit")],
            [InlineKeyboardButton("🏠 Accueil", callback_data="start")]
        ])
    )

def handle_message(update: Update, context: CallbackContext):
    state = context.user_data.get('state')
    if state == "ASK_AMOUNT":
        try:
            amount = float(update.message.text)
            if amount >= 10:
                currency = context.user_data['currency']
                handle_crypto_deposit(update.message.chat_id, currency, amount, context)
            else:
                update.message.reply_text("⚠️ Le montant minimum est de 10€.")
        except ValueError:
            update.message.reply_text("⚠️ Veuillez entrer un montant valide.")
    else:
        update.message.reply_text("❌ Commande non reconnue.")

def create_payment_request(amount, currency, user_id):
    headers = {
        'x-api-key': NOWPAYMENTS_API_KEY,
        'Content-Type': 'application/json'
    }
    data = {
        'price_amount': amount,
        'price_currency': 'EUR',
        'pay_currency': currency.upper(),
        'order_id': f"{user_id}_deposit",
        'order_description': 'Crédit via bot Telegram'
    }
    response = requests.post('https://api.nowpayments.io/v1/payment', headers=headers, json=data)
    return response.json()

def handle_crypto_deposit(chat_id, currency, amount, context):
    user_id = chat_id
    response = create_payment_request(amount, currency, user_id)
    if response.get('payment_status') == 'waiting':
        address = response['pay_address']
        pay_amount = response['pay_amount']
        expiration_time = 19 * 60

        qr = qrcode.make(address)
        qr_path = '/tmp/qrcode.png'
        qr.save(qr_path)

        message = context.bot.send_photo(
            chat_id=chat_id,
            photo=open(qr_path, 'rb'),
            caption=f"🔱 Envoyez {pay_amount} {currency.upper()} à :
`{address}`
⏱️ Temps restant : 19:00",
            parse_mode='Markdown'
        )

        context.user_data['message_id'] = message.message_id
        threading.Thread(target=start_countdown, args=(context, chat_id, message.message_id, expiration_time)).start()

        try:
            os.remove(qr_path)
        except:
            pass
    else:
        context.bot.send_message(chat_id=chat_id, text="❌ Erreur de génération d'adresse. Veuillez réessayer.")

def start_countdown(context, chat_id, message_id, expiration_time):
    previous_time_str = ""
    while expiration_time > 0:
        minutes, seconds = divmod(expiration_time, 60)
        time_str = f"{minutes:02}:{seconds:02}"
        if time_str != previous_time_str:
            try:
                context.bot.edit_message_caption(
                    chat_id=chat_id,
                    message_id=message_id,
                    caption=f"⏱️ Temps restant : {time_str}
Envoyez votre paiement avant expiration.",
                    parse_mode='Markdown'
                )
            except telegram.error.BadRequest:
                pass
            previous_time_str = time_str
        time.sleep(1)
        expiration_time -= 1

    context.bot.edit_message_caption(
        chat_id=chat_id,
        message_id=message_id,
        caption="🔴 Temps expiré. Veuillez recommencer.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔁 Recommencer", callback_data='retry_deposit')],
            [InlineKeyboardButton("🏠 Accueil", callback_data='start')]
        ])
    )
