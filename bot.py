from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler, MessageHandler, Filters
import qrcode
from PIL import Image
import io

TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"


user_data = {}


def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("🔹 Create QR Code", callback_data='create_qr')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        "សួស្តី! 👋\nសូមចុច Button ខាងក្រោមដើម្បីបង្កើត QR Code:",
        reply_markup=reply_markup
    )


def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    
    if query.data == "create_qr":
        query.message.reply_text("សូមផ្ញើ **link** ដែលអ្នកចង់បង្កើត QR Code:")

        
        user_data[query.from_user.id] = {"state": "waiting_link"}


def handle_message(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    text = update.message.text

    if user_id in user_data:
        state = user_data[user_id]["state"]

        if state == "waiting_link":
            user_data[user_id]["link"] = text
            user_data[user_id]["state"] = "waiting_color"
            update.message.reply_text(
                "បញ្ចូលពណ៌ដែលអ្នកចង់បាន (ឧ. red, blue, #FF5733) ឬចុច enter សម្រាប់ black default:"
            )
        elif state == "waiting_color":
            color = text if text else "black"
            link = user_data[user_id]["link"]

            # Generate QR
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )
            qr.add_data(link)
            qr.make(fit=True)
            img = qr.make_image(fill_color=color, back_color="white")

            # Save to bytes
            bio = io.BytesIO()
            bio.name = 'qr.png'
            img.save(bio, 'PNG')
            bio.seek(0)

            update.message.reply_photo(photo=bio)
            update.message.reply_text("✅ QR Code បានបង្កើតរួច! ចុច /start ដើម្បីបង្កើតថ្មី។")
            
            # Clear user data
            del user_data[user_id]

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    print("Bot is running...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
