from telegram import Update
from telegram.ext import ContextTypes
import database
import os

ADMIN_ID = int(os.getenv("ADMIN_TELEGRAM_ID"))

async def ajouter_credit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return await update.message.reply_text("❌ Accès refusé.")

    try:
        user_id = int(context.args[0])
        montant_val = float(context.args[1])
        database.update_solde(user_id, montant_val)
        await update.message.reply_text(f"✅ {montant_val} € ajoutés à l'utilisateur {user_id}.")
    except (IndexError, ValueError):
        await update.message.reply_text("❌ Format attendu : /ajouter_credit <user_id> <montant>")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return await update.message.reply_text("❌ Accès refusé.")

    message = ' '.join(context.args)
    if not message:
        return await update.message.reply_text("❌ Message vide.")

    users = database.get_all_user_ids()
    sent = 0
    for user_id in users:
        try:
            await context.bot.send_message(chat_id=user_id, text=f"📢 {message}")
            sent += 1
        except:
            continue
    await update.message.reply_text(f"✅ Message envoyé à {sent} utilisateurs.")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return await update.message.reply_text("❌ Accès refusé.")

    total_users = database.count_users()
    total_docs = database.count_documents()
    revenu = total_docs * 15

    await update.message.reply_text(
        f"📊 Statistiques :\n"
        f"👥 Utilisateurs : {total_users}\n"
        f"📄 Documents générés : {total_docs}\n"
        f"💶 Revenu estimé : {revenu:.2f} €"
    )
