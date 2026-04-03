import telebot
import requests
from telebot import types

# --- CONFIGURATION ---
API_TOKEN = '8011202030:AAGQFlzxvr7345NvYnA9yBziN1vL6jHlX5I'
bot = telebot.TeleBot(API_TOKEN)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

COUNTRIES = {
    "🇺🇸 USA": "United-States",
    "🇬🇧 UK": "United-Kingdom",
    "🇨🇦 Canada": "Canada",
    "🇳🇱 Netherlands": "Netherlands",
    "🇫🇷 France": "France"
}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [types.InlineKeyboardButton(text=name, callback_data=f"get_{code}") for name, code in COUNTRIES.items()]
    markup.add(*buttons)
    bot.reply_to(message, "Welcome Boss! Select a country to get a number:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('get_'))
def callback_get_num(call):
    country_code = call.data.split('_')[1]
    bot.answer_callback_query(call.id, f"Fetching {country_code} number...")
    try:
        url = f"https://quackr.io/api/messages/country/{country_code}"
        response = requests.get(url, headers=HEADERS, timeout=10).json()
        if 'data' in response and len(response['data']) > 0:
            latest_num = response['data'][0]['number']
            msg = f"✅ Country: {country_code}\n📞 Number: `{latest_num}`\n\nClick below to check OTP:"
            check_markup = types.InlineKeyboardMarkup()
            check_markup.add(types.InlineKeyboardButton("📩 Check OTP", callback_data=f"check_{latest_num}"))
            bot.send_message(call.message.chat.id, msg, parse_mode="Markdown", reply_markup=check_markup)
        else:
            bot.send_message(call.message.chat.id, "No numbers available for this country.")
    except:
        bot.send_message(call.message.chat.id, "Server error. Please try again.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('check_'))
def callback_check_otp(call):
    num = call.data.split('_')[1]
    bot.answer_callback_query(call.id, "Checking for OTP...")
    try:
        url = f"https://quackr.io/api/messages/number/{num}"
        response = requests.get(url, headers=HEADERS, timeout=10).json()
        if 'data' in response:
            messages = response['data'][:3]
            if not messages:
                bot.send_message(call.message.chat.id, f"❌ No messages for `{num}` yet.")
                return
            res = f"📩 Latest OTP for `{num}`:\n\n"
            for m in messages:
                res += f"📌 From: {m.get('from')}\n💬 Msg: {m.get('message')}\n---\n"
            bot.send_message(call.message.chat.id, res, parse_mode="Markdown")
        else:
            bot.send_message(call.message.chat.id, "Messages not found.")
    except:
        bot.send_message(call.message.chat.id, "Error fetching OTP.")

if __name__ == '__main__':
    bot.infinity_polling()
          
