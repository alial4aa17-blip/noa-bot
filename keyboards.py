from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

province_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="بغداد"), KeyboardButton(text="البصرة")],
        [KeyboardButton(text="أربيل"), KeyboardButton(text="النجف")],
        [KeyboardButton(text="كربلاء"), KeyboardButton(text="نينوى")],
        [KeyboardButton(text="كركوك"), KeyboardButton(text="الأنبار")],
        [KeyboardButton(text="بابل"), KeyboardButton(text="ديالى")]
    ],
    resize_keyboard=True
)

size_type_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="عادي")],
        [KeyboardButton(text="HAF")]
    ],
    resize_keyboard=True
)

color_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="أسود"), KeyboardButton(text="أبيض")],
        [KeyboardButton(text="وردي"), KeyboardButton(text="جوزي")],
        [KeyboardButton(text="أوف وايت"), KeyboardButton(text="نيلي")]
    ],
    resize_keyboard=True
)

finish_photos_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="إنهاء الصور")]
    ],
    resize_keyboard=True
)

def order_buttons(code):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="رفع / تحديث التصميم",
                    callback_data=f"design:{code}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="تمت الموافقة والطباعة",
                    callback_data=f"printing:{code}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="تم التجهيز",
                    callback_data=f"ready:{code}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="عند شركة التوصيل",
                    callback_data=f"delivery:{code}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="تم التسليم",
                    callback_data=f"done:{code}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="راجع",
                    callback_data=f"returned:{code}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="ملغي",
                    callback_data=f"cancel:{code}"
                )
            ]
        ]
    )