from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup


def footer_keyboard():

    keyboard = [

        [
            InlineKeyboardButton(
                "⭐ Default",
                callback_data="footer_default"
            )
        ]

    ]

    return InlineKeyboardMarkup(keyboard)