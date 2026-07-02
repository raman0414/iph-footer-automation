import os

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from config import BOT_TOKEN
from bot.image_processor import ImageProcessor


# ---------------------------------------
# Create folders if they don't exist
# ---------------------------------------
os.makedirs("temp", exist_ok=True)
os.makedirs("output", exist_ok=True)


# ---------------------------------------
# /start
# ---------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "🏥 Welcome to IPH Footer Bot!\n\n"
        "Current Footer: ⭐ Default\n\n"
        "📷 Send one or more photos and I'll automatically add the footer."
    )


# ---------------------------------------
# Receive Photo
# ---------------------------------------
async def receive_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    photo = update.message.photo[-1]

    telegram_file = await photo.get_file()

    input_path = f"temp/{photo.file_unique_id}.jpg"
    output_path = f"output/{photo.file_unique_id}.jpg"

    try:

        # Download image
        await telegram_file.download_to_drive(input_path)

        # Process image
        ImageProcessor.process(
            image_path=input_path,
            output_path=output_path,
            template="default"
        )

        # Send processed image
        with open(output_path, "rb") as processed_image:

            await update.message.reply_photo(
                photo=processed_image,
                caption="✅ Footer added successfully!"
            )

    except Exception as e:

        print(e)

        await update.message.reply_text(
            f"❌ Something went wrong.\n\n{e}"
        )

    finally:

        # Delete temporary files
        if os.path.exists(input_path):
            os.remove(input_path)

        if os.path.exists(output_path):
            os.remove(output_path)


# ---------------------------------------
# Main
# ---------------------------------------
def main():

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    app.add_handler(
        MessageHandler(
            filters.PHOTO,
            receive_photo
        )
    )

    print("🏥 IPH Footer Bot is running...")

    app.run_polling()


# ---------------------------------------
if __name__ == "__main__":
    main()