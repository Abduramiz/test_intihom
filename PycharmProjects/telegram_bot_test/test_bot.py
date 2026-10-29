import telebot
from telebot import types, custom_filters
from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage
from config import TOKEN
import db

bot = telebot.TeleBot(
    TOKEN,
    state_storage=StateMemoryStorage()
)

SAVOL = (
    "Python'da ro'yxat qanday belgilanadi?",
    ["[ ]", "{ }", "( )"],
    0
)

SAVOL2 = (
    "❓ 2-savol: 2 ** 3 nechaga teng?",
    ["6", "8", "9"],
    1
)

SAVOL3 = (
    "❓ 3-savol: Bot tokenini kim beradi?",
    ["@BotFather", "@Python", "@Google"],
    0
)

data_test = {}


class Royxat(StatesGroup):
    ism = State()
    test = State()
    test2 = State()
    test3 = State()


def menyu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True)
    m.row("🎮 Boshlash", "ℹ️ Yordam")
    return m


def savol_yubor(message, savol_data, prefix):
    savol, variantlar, _ = savol_data

    markup = types.InlineKeyboardMarkup()

    for i, variant in enumerate(variantlar):
        markup.add(
            types.InlineKeyboardButton(
                variant,
                callback_data=f"{prefix}_{i}"
            )
        )

    bot.send_message(
        message.chat.id,
        "🧠 " + savol,
        reply_markup=markup
    )


@bot.message_handler(commands=["start"])
def start(message):
    bot.set_my_commands([
        types.BotCommand("start", "Botni ishga tushirish"),
        types.BotCommand("boshlash", "Testni boshlash"),
        types.BotCommand("yordam", "Yordam"),
        types.BotCommand("cancel", "Testni to'xtatish")
    ])

    bot.send_message(
        message.chat.id,
        "Salom! 🧠 Mini viktorinaga xush kelibsiz.",
        reply_markup=menyu()
    )


@bot.message_handler(commands=["boshlash"])
@bot.message_handler(func=lambda m: m.text == "🎮 Boshlash")
def test_boshlash(message):
    chat_id = message.chat.id

    data_test[chat_id] = {
        "ism": "",
        "javoblar": []
    }

    bot.set_state(
        message.from_user.id,
        Royxat.ism,
        chat_id
    )

    bot.send_message(
        chat_id,
        "Ismingizni kiriting:",
        reply_markup=types.ReplyKeyboardRemove()
    )


@bot.message_handler(state=Royxat.ism)
def ism_qabul(message):
    ism = message.text.strip()

    if not ism:
        bot.send_message(
            message.chat.id,
            "Iltimos, ismingizni kiriting."
        )
        return

    chat_id = message.chat.id
    data_test[chat_id]["ism"] = ism

    bot.set_state(
        message.from_user.id,
        Royxat.test,
        chat_id
    )

    test(message)


@bot.message_handler(state=Royxat.test)
def test(message):
    savol_yubor(message, SAVOL, "javob")


@bot.message_handler(state=Royxat.test2)
def test2(message):
    savol_yubor(message, SAVOL2, "javob2")


@bot.message_handler(state=Royxat.test3)
def test3(message):
    savol_yubor(message, SAVOL3, "javob3")


def javobni_tekshir(call, savol_data, keyingi_state=None):
    chat_id = call.message.chat.id
    user_id = call.from_user.id

    user = data_test.get(chat_id)

    if user is None:
        bot.answer_callback_query(
            call.id,
            "Testni qaytadan boshlang!"
        )
        return

    tanlangan = int(call.data.split("_")[1])

    savol, variantlar, togri_index = savol_data
    togri_javob = variantlar[togri_index]

    if tanlangan == togri_index:
        user["javoblar"].append(1)
        matn = f"✅ To'g'ri! Javob: {togri_javob}"
    else:
        user["javoblar"].append(0)
        matn = f"❌ Noto'g'ri! To'g'ri javob: {togri_javob}"

    db.user_saqla(
        chat_id,
        user["ism"],
        user["javoblar"]
    )

    bot.answer_callback_query(call.id)

    bot.edit_message_text(
        matn,
        chat_id,
        call.message.message_id
    )

    if keyingi_state is not None:
        bot.set_state(
            user_id,
            keyingi_state[0],
            chat_id
        )

        keyingi_state[1](call.message)

    else:
        ism = user["ism"]
        natija = sum(user["javoblar"])

        bot.send_message(
            chat_id,
            f"🏁 Test tugadi,{natija}/3 {ism}!",
            reply_markup=menyu()
        )

        bot.delete_state(user_id, chat_id)
        data_test.pop(chat_id, None)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("javob_")
)
def test_qabul(call):
    javobni_tekshir(
        call,
        SAVOL,
        (Royxat.test2, test2)
    )


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("javob2_")
)
def test2_qabul(call):
    javobni_tekshir(
        call,
        SAVOL2,
        (Royxat.test3, test3)
    )


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("javob3_")
)
def test3_qabul(call):
    javobni_tekshir(
        call,
        SAVOL3
    )


@bot.message_handler(commands=["yordam"])
@bot.message_handler(func=lambda m: m.text == "ℹ️ Yordam")
def yordam(message):
    bot.send_message(
        message.chat.id,
        "ℹ️ Yordami\n\n"
        "🎮 Boshlash — testni boshlaydi.\n"
        "🧠 Sizga 3 ta savol beriladi.\n"
        "📊 Har bir to'g'ri javob uchun 1 ball.\n"
        "/cancel — testni to'xtatish.",
        reply_markup=menyu()
    )


@bot.message_handler(
    state="*",
    commands=["cancel"]
)
def cancel(message):
    data_test.pop(message.chat.id, None)

    bot.delete_state(
        message.from_user.id,
        message.chat.id
    )

    bot.send_message(
        message.chat.id,
        "❌ Test bekor qilindi.",
        reply_markup=menyu()
    )


@bot.message_handler(func=lambda m: True)
def echo(message):
    bot.send_message(
        message.chat.id,
        "Tushunmadim 🤔\nPastdagi tugmalardan foydalaning.",
        reply_markup=menyu()
    )


if __name__ == "__main__":
    bot.add_custom_filter(
        custom_filters.StateFilter(bot)
    )

    bot.infinity_polling(
        timeout=30,
        long_polling_timeout=20,
        restart_on_change=False
    )
