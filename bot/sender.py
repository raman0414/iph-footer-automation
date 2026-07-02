from telegram import InputMediaPhoto


class TelegramSender:

    @staticmethod
    async def send_album(chat_id, bot, image_paths):

        media = []

        files = []

        try:

            for path in image_paths:

                file = open(path, "rb")

                files.append(file)

                media.append(
                    InputMediaPhoto(file)
                )

            await bot.send_media_group(
                chat_id=chat_id,
                media=media
            )

        finally:

            for file in files:
                file.close()