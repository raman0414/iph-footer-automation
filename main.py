import os

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

from config import BOT_TOKEN
from bot.image_processor import ImageProcessor
from bot.keyboards import footer_keyboard
from bot.template_manager import TemplateManager


# ---------------------------------------
# Create folders if they don't exist
# ---------------------------------------
os.makedirs("temp", exist_ok=True)
os.makedirs("output", exist_ok=True)


# ---------------------------------------
# /start
# ---------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    current_template = TemplateManager.get_template(
        update.effective_user.id
    )

    await update.message.reply_text(
        "🏥 *IPH Footer Bot*\n\n"
        f"Current Footer: ⭐ *{current_template.capitalize()}*\n\n"
        "Select a footer template below.",
        parse_mode="Markdown",
        reply_markup=footer_keyboard()
    )


# ---------------------------------------
# Footer Selected
# ---------------------------------------
async def footer_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    template = query.data.replace("footer_", "")

    TemplateManager.set_template(
        query.from_user.id,
        template
    )

    await query.edit_message_text(
        "✅ *Footer Updated*\n\n"
        f"Current Footer: ⭐ *{template.capitalize()}*\n\n"
        "📷 Now send one or more photos.",
        parse_mode="Markdown"
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

        # Get selected footer
        template = TemplateManager.get_template(
            update.effective_user.id
        )

        # Process image
        ImageProcessor.process(
            image_path=input_path,
            output_path=output_path,
            template=template
        )

        # Send processed image
        with open(output_path, "rb") as processed_image:

            await update.message.reply_photo(
                photo=processed_image,
                caption=f"✅ Footer applied\n\nTemplate: ⭐ {template.capitalize()}"
            )

    except Exception as e:

        print(e)

        await update.message.reply_text(
            f"❌ Something went wrong.\n\n{e}"
        )

    finally:

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
        CallbackQueryHandler(
            footer_selected,
            pattern="^footer_"
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