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
from bot.album_manager import AlbumManager
from bot.sender import TelegramSender


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
# Process & send a single photo
# ---------------------------------------
async def process_single_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    photo = update.message.photo[-1]
    telegram_file = await photo.get_file()

    input_path = f"temp/{photo.file_unique_id}.jpg"
    output_path = f"output/{photo.file_unique_id}.jpg"

    # Progress message
    status_msg = await update.message.reply_text("⏳ Processing...")

    try:

        await telegram_file.download_to_drive(input_path)

        template = TemplateManager.get_template(
            update.effective_user.id
        )

        ImageProcessor.process(
            image_path=input_path,
            output_path=output_path,
            template=template
        )

        with open(output_path, "rb") as processed_image:
            await update.message.reply_photo(
                photo=processed_image,
                caption=f"✅ Footer applied\n\nTemplate: ⭐ {template.capitalize()}"
            )

        await status_msg.delete()

    except Exception as e:

        print(e)

        await status_msg.edit_text(
            f"❌ Something went wrong.\n\n{e}"
        )

    finally:

        if os.path.exists(input_path):
            os.remove(input_path)

        if os.path.exists(output_path):
            os.remove(output_path)


# ---------------------------------------
# Process & send an album of photos
# ---------------------------------------
async def process_album(photos):
    """
    Callback fired by AlbumManager once all photos
    in a media group have been collected.
    """

    if not photos:
        return

    first = photos[0]
    chat_id = first["chat_id"]
    bot = first["bot"]
    user_id = first["user_id"]
    template = TemplateManager.get_template(user_id)
    total = len(photos)

    # Send initial progress message
    status_msg = await bot.send_message(
        chat_id=chat_id,
        text=f"⏳ Processing photos... (0/{total})"
    )

    output_paths = []

    try:

        for i, photo_info in enumerate(photos, start=1):

            input_path = photo_info["input_path"]
            output_path = photo_info["output_path"]

            # Process image
            ImageProcessor.process(
                image_path=input_path,
                output_path=output_path,
                template=template
            )

            output_paths.append(output_path)

            # Update progress
            await status_msg.edit_text(
                f"⏳ Processing photos... ({i}/{total})"
            )

        # Send all processed photos as an album
        await TelegramSender.send_album(
            chat_id=chat_id,
            bot=bot,
            image_paths=output_paths
        )

        await status_msg.edit_text(
            f"✅ Done! {total} photos processed.\n\n"
            f"Template: ⭐ {template.capitalize()}"
        )

    except Exception as e:

        print(e)

        await status_msg.edit_text(
            f"❌ Something went wrong.\n\n{e}"
        )

    finally:

        # Clean up all temp and output files
        for photo_info in photos:
            for path in [photo_info["input_path"], photo_info["output_path"]]:
                if os.path.exists(path):
                    os.remove(path)


# ---------------------------------------
# Receive Photo (entry point)
# ---------------------------------------
async def receive_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if AlbumManager.is_album(update):

        # --- Album photo ---
        photo = update.message.photo[-1]
        telegram_file = await photo.get_file()

        input_path = f"temp/{photo.file_unique_id}.jpg"
        output_path = f"output/{photo.file_unique_id}.jpg"

        await telegram_file.download_to_drive(input_path)

        photo_info = {
            "input_path": input_path,
            "output_path": output_path,
            "chat_id": update.effective_chat.id,
            "bot": context.bot,
            "user_id": update.effective_user.id,
        }

        album_id = AlbumManager.get_album_id(update)

        await AlbumManager.add_photo(
            media_group_id=album_id,
            photo_info=photo_info,
            callback=process_album
        )

    else:

        # --- Single photo ---
        await process_single_photo(update, context)


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