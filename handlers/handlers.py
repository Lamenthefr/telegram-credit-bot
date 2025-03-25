async def recharge_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    username = query.from_user.username
    user = database.get_user(user_id)
    if not user:
        database.create_user_if_not_exists(user_id, username)
        user = database.get_user(user_id)

    if not user:
        await query.message.reply_text("Erreur lors de la création du profil utilisateur.")
        return

    keyboard = [
        [InlineKeyboardButton("BTC", callback_data='deposit_btc')],
        [InlineKeyboardButton("ETH", callback_data='deposit_eth')],
        [InlineKeyboardButton("LTC", callback_data='deposit_ltc')]
    ]
    text = f"💰 Solde: {user[2]:.2f} €\n\nChoisissez une crypto pour recharger :"
    await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
