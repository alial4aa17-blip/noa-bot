import asyncio
import json
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, InputMediaPhoto
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from config import *
from states import OrderState, DesignState
from keyboards import *
from database import *

bot = Bot(BOT_TOKEN)
dp = Dispatcher()


def is_full_access(user_id):
    return user_id in FULL_ACCESS_IDS


@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await message.answer("ارسل رقم الهاتف")
    await state.set_state(OrderState.phone)


@dp.message(OrderState.phone)
async def phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("اختر المحافظة", reply_markup=province_keyboard)
    await state.set_state(OrderState.province)


@dp.message(OrderState.province)
async def province(message: Message, state: FSMContext):
    await state.update_data(province=message.text)
    await message.answer("ارسل العنوان", reply_markup=ReplyKeyboardRemove())
    await state.set_state(OrderState.address)


@dp.message(OrderState.address)
async def address(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    await message.answer("اختر نوع القياس", reply_markup=size_type_keyboard)
    await state.set_state(OrderState.size_type)


@dp.message(OrderState.size_type)
async def size_type(message: Message, state: FSMContext):
    await state.update_data(size_type=message.text)
    await message.answer("اكتب القياس", reply_markup=ReplyKeyboardRemove())
    await state.set_state(OrderState.size)


@dp.message(OrderState.size)
async def size(message: Message, state: FSMContext):
    await state.update_data(size=message.text)
    await message.answer("ارسل العدد")
    await state.set_state(OrderState.quantity)


@dp.message(OrderState.quantity)
async def quantity(message: Message, state: FSMContext):
    quantity = int(message.text)
    data = {"quantity": message.text}

    if quantity == 1:
        data["price"] = "20000"
    elif quantity == 2:
        data["price"] = "35000"
    elif quantity == 3:
        data["price"] = "50000"
    else:
        await state.update_data(quantity=message.text)
        await message.answer("ادخل السعر يدويًا")
        await state.set_state(OrderState.manual_price)
        return

    await state.update_data(**data)
    await message.answer("اختر اللون", reply_markup=color_keyboard)
    await state.set_state(OrderState.color)


@dp.message(OrderState.manual_price)
async def manual_price(message: Message, state: FSMContext):
    await state.update_data(price=message.text)
    await message.answer("اختر اللون", reply_markup=color_keyboard)
    await state.set_state(OrderState.color)


@dp.message(OrderState.color)
async def color(message: Message, state: FSMContext):
    await state.update_data(color=message.text)
    await message.answer("اكتب ملاحظة الطلب أو اكتب لا يوجد")
    await state.set_state(OrderState.note)

@dp.message(OrderState.note)
async def note(message: Message, state: FSMContext):
    await state.update_data(
        note=message.text,
        photos=[]
    )

    await message.answer(
        "ارسل الصور، وبعد الانتهاء اضغط إنهاء الصور",
        reply_markup=finish_photos_keyboard
    )
    await state.set_state(OrderState.photos)

@dp.message(OrderState.photos, F.photo)
async def collect_photos(message: Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photos", [])
    photos.append(message.photo[-1].file_id)
    await state.update_data(photos=photos)
    await message.answer("تم حفظ الصورة")


@dp.message(OrderState.photos)
async def finish_photos(message: Message, state: FSMContext):
    if message.text != "إنهاء الصور":
        return

    data = await state.get_data()
    photos = data["photos"]
    code = get_next_code()

    caption = f"""
الكود : {code}
الرقم : {data['phone']}
المحافظة : {data['province']}
العنوان : {data['address']}
القياس : {data['size']}
العدد : {data['quantity']}
اللون : {data['color']}
الملاحظة : {data['note']}
السعر : {data['price']}
الحالة : تم الرفع
"""

    media = []

    for i, photo in enumerate(photos):
        if i == 0:
            media.append(InputMediaPhoto(media=photo, caption=caption))
        else:
            media.append(InputMediaPhoto(media=photo))

    await bot.send_media_group(
        chat_id=GROUP_ID,
        message_thread_id=TOPIC_NEW,
        media=media
    )

    sent = await bot.send_message(
        chat_id=GROUP_ID,
        message_thread_id=TOPIC_NEW,
        text=f"تحكم بالطلب {code}",
        reply_markup=order_buttons(code)
    )

    save_order((
        code,
        data['phone'],
        data['province'],
        data['address'],
        data['size'],
        data['quantity'],
        data['color'],
        data['price'],
        json.dumps(photos),
        "تم الرفع",
        sent.message_id
    ))

    await message.answer(f"""
تم تأكيد طلبك بنجاح 🤍✨

🆔 كود الطلب:
{code}

📌 يرجى الاحتفاظ بالكود للمتابعة أو الاستفسار.

🎨 بعد بدء الطباعة لا يمكن تعديل أو إلغاء الطلب.

🛡️ البيج تحت الحماية القانونية.

📞 الدعم:
07825034506
""", reply_markup=ReplyKeyboardRemove())

    await state.clear()
    await message.answer("➕ لرفع طلب جديد اكتب /start")


@dp.callback_query(lambda c: c.data.startswith("design:"))
async def design_callback(callback: CallbackQuery, state: FSMContext):
    if not is_full_access(callback.from_user.id):
        await callback.answer("ليس لديك صلاحية")
        return

    code = callback.data.split(":")[1]
    await state.update_data(order_code=code)
    await callback.message.answer(f"ارسل التصميم الجديد للطلب {code}")
    await state.set_state(DesignState.waiting_photo)


@dp.message(DesignState.waiting_photo, F.photo)
async def upload_design(message: Message, state: FSMContext):
    data = await state.get_data()
    code = data["order_code"]
    file_id = message.photo[-1].file_id
    update_photos(code, [file_id])
    await message.answer("تم تحديث التصميم")
    await state.clear()


@dp.callback_query(
    lambda c: ":" in c.data and c.data.split(":")[0] in
    ["printing", "ready", "delivery", "done", "returned", "cancel"]
)
async def move_order(callback: CallbackQuery):
    if not is_full_access(callback.from_user.id):
        await callback.answer("ليس لديك صلاحية")
        return

    action, code = callback.data.split(":")
    order = get_order(code)

    mapping = {
        "printing": ("تمت الموافقة والطباعة", TOPIC_PRINTING),
        "ready": ("تم التجهيز", TOPIC_READY),
        "delivery": ("عند شركة التوصيل", TOPIC_DELIVERY),
        "done": ("تم التسليم", TOPIC_DONE),
        "returned": ("راجع", TOPIC_RETURNED),
        "cancel": ("ملغي", TOPIC_CANCELLED)
    }

    status, topic = mapping[action]
    update_status(code, status)

    try:
        await bot.delete_message(chat_id=GROUP_ID, message_id=order[11])
    except:
        pass

    photos = json.loads(order[9])

    caption = f"""
الكود : {code}
الرقم : {order[2]}
المحافظة : {order[3]}
العنوان : {order[4]}
القياس : {order[5]}
العدد : {order[6]}
اللون : {order[7]}
السعر : {order[8]}
الحالة : {status}
"""

    sent = await bot.send_photo(
        chat_id=GROUP_ID,
        message_thread_id=topic,
        photo=photos[0],
        caption=caption,
        reply_markup=order_buttons(code)
    )

    update_message_id(code, sent.message_id)
    await callback.answer("تم النقل")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
