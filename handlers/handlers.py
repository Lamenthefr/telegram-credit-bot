from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
import database

async def recharge_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    user = database.get_user(user_id)
    if not user:
        database.create_user_if_not_exists(user_id, username)
        user = database.get_user(user_id)

    keyboard = [
        [InlineKeyboardButton("BTC", callback_data='deposit_btc')],
        [InlineKeyboardButton("ETH", callback_data='deposit_eth')],
        [InlineKeyboardButton("LTC", callback_data='deposit_ltc')],
    ]
    text = f"💳 Recharger votre compte :\nSolde actuel : {user[2]:.2f} €"
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
