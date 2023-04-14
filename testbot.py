
import telebot
import json
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from bs4 import BeautifulSoup
import os
from telebot import types

TOKEN = "1638155581:AAGe4dxE4Cz3GXC2NAuHesSAKpeRgwhmQuw"

bot = telebot.TeleBot(TOKEN)

LEADERBOARD_FILE = 'leaderboard.json'

API_KEY = "2748b8f5-8e99-4210-845d-78176b3a1f62"

user_to_count = {}


@bot.message_handler(commands=['start'])
def start_command(message):
    markup = types.InlineKeyboardMarkup()
    markup.row(
    types.InlineKeyboardButton('Crypto 💰', callback_data='crypto_menu'),
    types.InlineKeyboardButton('Sticker🎁', callback_data='stic')
)

    bot.send_message(
        chat_id=message.chat.id,
        text='Welcome to my bot!',
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == 'crypto_menu':
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton(
                '/p BTC',
                callback_data='pbtc'
            ),
            types.InlineKeyboardButton(
                '/cnv 1 BTC USD',
                callback_data='cbin'
            )
        )
        bot.send_message(
            chat_id=call.message.chat.id,
            text='<code>/p</code> - Shows the price and 24h change of a cryptocurrency\n(e.g. /p BTC)\n\n<code>/cnv </code> - Converts a cryptocurrency to a given currency \n(e.g. /cnv 1 BTC USD)',
            parse_mode= "HTML",
            reply_markup=markup
        )
    elif call.data == 'stic':
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton(
                'Font 1',
                callback_data='font1'
            ),
            types.InlineKeyboardButton(
                'Font 2',
                callback_data='font2'
            ),
            types.InlineKeyboardButton(
                'Font 3',
                callback_data='font3'
            )
        )
        bot.send_message(
            chat_id=call.message.chat.id,
            text= '<code>/stic</code> - To Genrate Text To Sticker\n(e.g. /stic Bnsl BOy)\n\nWe have three types of fonts \n font 1 - <code>/stic</code> \n font 2 - <code>/stic1</code> \n font 3 - <code>/stic2</code>',
            parse_mode= "HTML",
            reply_markup=markup
        )
    elif call.data == 'font1':
        text = "Bnsl Boy"  # Set the default text for the sticker

        # Generate the sticker based on the text
        font_path = os.path.join(os.getcwd(), "Vampire Wars Italic.ttf")
        sticker_file = generate_sticker(text, font_path)

        # Send the sticker back to the user
        bot.send_sticker(call.message.chat.id, sticker_file)
    elif call.data == 'font2':
        text = "Bnsl Boy"  # Set the default text for the sticker

        # Generate the sticker based on the text
        font_path = os.path.join(os.getcwd(), "Mabook.ttf")
        sticker_file = generate_sticker(text, font_path)

        # Send the sticker back to the user
        bot.send_sticker(call.message.chat.id, sticker_file)
    elif call.data == 'font3':
        text = "Bnsl Boy"  # Set the default text for the sticker

        # Generate the sticker based on the text
        font_path = os.path.join(os.getcwd(), "Game Of Squids.ttf")
        sticker_file = generate_sticker(text, font_path)

        # Send the sticker back to the user
        bot.send_sticker(call.message.chat.id, sticker_file)
    elif call.data == 'pbtc':
        symbol = "BTC"
        result = get_price(symbol)
        price, percent_change_24h = result
        response_text = f"{symbol}: ${price:,.2f}"
        if percent_change_24h is not None:
            change_24h_text = f"{percent_change_24h:.2f}%"
            if percent_change_24h > 0:
                response_text += f" (🟢{change_24h_text})"
            elif percent_change_24h < 0:
                response_text += f" (🔴{change_24h_text})"
            else:
                response_text += f" ({change_24h_text})"
        bot.send_message(call.message.chat.id, response_text)
    elif call.data == 'cbin':
        crypto_amount = "1"
        crypto_symbol = "BTC"
        currency = "USD"
        result = convert(crypto_amount, crypto_symbol, currency)
        response_text = f'<code>{crypto_amount} {crypto_symbol} is worth {result:.8f} {currency}</code>.\n\n'
        response_text += f'✨ {crypto_amount} <b>{crypto_symbol}</b> = <code>{result:.5f} {currency}</code> \n\n'
        bot.send_message(call.message.chat.id, response_text, parse_mode="HTML")



# Load leaderboard data from file on startup
try:
    with open(LEADERBOARD_FILE, 'r') as f:
        user_to_count = json.load(f)
except FileNotFoundError:
    pass

@bot.message_handler(commands=['count'])
def count_members_added(message):
    user_id = message.from_user.id
    if user_id in user_to_count:
        count = user_to_count[user_id]
    else:
        count = 0
    bot.send_message(chat_id=message.chat.id, text=f"You have added {count} members to this group.")

@bot.message_handler(commands=['leaderboard'])
def show_leaderboard(message):
    top_users = sorted(user_to_count.items(), key=lambda x: x[1], reverse=True)[:10]
    if top_users:
        leaderboard = "Leaderboard:\n"
        for i, (user_id, count) in enumerate(top_users):
            user_info = bot.get_chat_member(message.chat.id, user_id)
            user_name = user_info.user.first_name if user_info.user.first_name else user_info.user.username
            leaderboard += f"{i+1}. {user_name}: {count}\n"
        bot.send_message(chat_id=message.chat.id, text=leaderboard)
    else:
        bot.send_message(chat_id=message.chat.id, text="No one has added any members yet!")


@bot.message_handler(commands=['reset'])
def reset_leaderboard(message):
    chat_id = message.chat.id
    chat_members = bot.get_chat_administrators(chat_id)

    # Check if the user is an admin
    user_id = message.from_user.id
    is_admin = False
    for member in chat_members:
        if member.user.id == user_id and member.status in ['creator', 'administrator']:
            is_admin = True
            break

    if is_admin:
        global user_to_count
        user_to_count = {}
        with open(LEADERBOARD_FILE, 'w') as f:
            json.dump(user_to_count, f)
        bot.send_message(chat_id=message.chat.id, text="Leaderboard reset!")
    else:
        bot.reply_to(message, "You must be an admin to use this command.")

@bot.message_handler(func=lambda message: True, content_types=['new_chat_members'])
def handle_new_member(message):
    user_id = message.from_user.id
    if user_id in user_to_count:
        user_to_count[user_id] += 1
    else:
        user_to_count[user_id] = 1
    count = user_to_count[user_id]
    bot.send_message(chat_id=message.chat.id, text=f"You have added {count} members to this group.")
    # Save updated leaderboard data to file
    with open(LEADERBOARD_FILE, 'w') as f:
        json.dump(user_to_count, f)

    # Delete the bot's last message instantly
    messages = bot.messages
    last_message = messages[len(messages)-1]
    if last_message.chat.id == message.chat.id:
        bot.delete_message(chat_id=message.chat.id, message_id=last_message.message_id)


# Function to get the price and 24h change of a given cryptocurrency
def get_price(crypto_symbol):
    url = f'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol={crypto_symbol}&convert=USD'
    headers = {'X-CMC_PRO_API_KEY': API_KEY}
    response = requests.get(url, headers=headers)
    data = response.json()
    if 'status' in data and data['status']['error_code'] == 400:
        return None
    try:
        price = data['data'][crypto_symbol]['quote']['USD']['price']
        percent_change_24h = data['data'][crypto_symbol]['quote']['USD']['percent_change_24h']
        return price, percent_change_24h
    except KeyError:
        return None


# Function to convert a given amount of cryptocurrency to a given currency
def convert(crypto_amount, crypto_symbol, currency):
    url = f'https://pro-api.coinmarketcap.com/v1/tools/price-conversion?amount={crypto_amount}&symbol={crypto_symbol}&convert={currency}'
    headers = {'X-CMC_PRO_API_KEY': API_KEY}
    response = requests.get(url, headers=headers)
    data = response.json()
    if 'status' in data and data['status']['error_code'] == 400:
        return None
    converted_amount = data['data']['quote'][currency]['price']
    return converted_amount

# Command to get the price and 24h change of a cryptocurrency
@bot.message_handler(commands=['p'])
def price(message):
    text = message.text.split()
    if len(text) != 2:
        bot.reply_to(message, 'Please specify a cryptocurrency symbol after the command,\n like /p BTC')
        return
    symbol = text[1].upper()
    result = get_price(symbol)
    if result is None:
        bot.reply_to(message, f'This {symbol} could not be found. Try again.')
        return
    price, percent_change_24h = result
    response_text = f"{symbol}: ${price:,.2f}"
    if percent_change_24h is not None:
        change_24h_text = f"{percent_change_24h:.2f}%"
        if percent_change_24h > 0:
            response_text += f" (🟢{change_24h_text})"
        elif percent_change_24h < 0:
            response_text += f" (🔴{change_24h_text})"
        else:
            response_text += f" ({change_24h_text})"
    bot.reply_to(message, response_text)


# Command to convert a cryptocurrency to a given currency
@bot.message_handler(commands=['cnv'])
def cnv(message):
    text = message.text.split()
    if len(text) != 4:
        bot.reply_to(message, 'Please specify a cryptocurrency symbol, amount, and target currency after the command, like /cnv 2.5 BTC USD')
        return
    crypto_amount = text[1]
    crypto_symbol = text[2].upper()
    currency = text[3].upper()
    result = convert(crypto_amount, crypto_symbol, currency)

    if result is None:
        bot.reply_to(message, f'Error converting {crypto_amount} {crypto_symbol} to {currency}.')
        return
    response_text = f'<code>{crypto_amount} {crypto_symbol} is worth {result:.8f} {currency}</code>.\n\n'
    response_text += f'✨ {crypto_amount} <b>{crypto_symbol}</b> = <code>{result:.5f} {currency}</code> \n\n'
    #response_text += f'✨ Current {crypto_symbol} price: {price:.2f} INR\n'
    #response_text += f'✨ Last 24 hours change: {percent_change_24h:.2f}%'
    bot.reply_to(message, response_text, parse_mode="HTML")
import io
from PIL import Image, ImageDraw, ImageFont

def generate_image(text, font_path, font_size, text_color, border_color, border_size):
    # Create a new image with a transparent background
    size = (512, 512)
    image = Image.new('RGBA', size, (0, 0, 0, 0))

    # Draw the text onto the image
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_path, size=font_size)

    # Split the text into words
    text = text.replace("kaddu", "luldeep")
    words = text.split()

    # Set the initial y-coordinate
    y = (size[1] - (len(words) * font_size)) / 2

    # Draw each word
    for word in words:
        # Determine the font size for this word
        word_font_size = font_size
        if len(word) > 6:
            extra_letters = len(word) - 6
            font_decrease_percent = extra_letters * 10
            word_font_size -= int(font_size * font_decrease_percent / 100)

        # Set the font for this word
        word_font = ImageFont.truetype(font_path, size=word_font_size)

        # Draw the word onto the image
        text_width, text_height = draw.textsize(word, font=word_font)
        x = (size[0] - text_width) / 2
        draw.text((x, y), word, fill=text_color, font=word_font, stroke_width=border_size, stroke_fill=border_color)

        # Update the y-coordinate for the next word
        y += word_font_size

    return image



def generate_sticker(text, font_path, font_size=100, text_color=(255, 255, 255), border_color=(0, 0, 0), border_size=10):
    # Generate the image
    image = generate_image(text, font_path, font_size, text_color, border_color, border_size)

    # Convert the image to a sticker file
    sticker_file = io.BytesIO()
    image.save(sticker_file, format='PNG')
    sticker_file.seek(0)

    return sticker_file

@bot.message_handler(commands=['stic'])
def handle_text_message(message):  
    # Check if the message has text
    
    if len(message.text.split(' ')) > 1:
        # Get the text from the message command
        text = message.text.split(' ', 1)[1]
    else:
        text = "Bnsl Boy"

    font_path = os.path.join(os.getcwd(), "Vampire Wars Italic.ttf")

    sticker_file = generate_sticker(text, font_path)
    # Send the new sticker back to the user
    bot.send_sticker(message.chat.id, sticker_file)

@bot.message_handler(commands=['stic1'])
def handle_text_message(message):  
    # Check if the message has text
    
    if len(message.text.split(' ')) > 1:
        # Get the text from the message command
        text = message.text.split(' ', 1)[1]
    else:
        text = "Bnsl Boy"

    font_path = os.path.join(os.getcwd(), "Mabook.ttf")

    sticker_file = generate_sticker(text, font_path)
    # Send the new sticker back to the user
    bot.send_sticker(message.chat.id, sticker_file)

@bot.message_handler(commands=['stic2'])
def handle_text_message(message):  
    # Check if the message has text
    
    if len(message.text.split(' ')) > 1:
        # Get the text from the message command
        text = message.text.split(' ', 1)[1]
    else:
        text = "Bnsl Boy"

    font_path = os.path.join(os.getcwd(), "Game Of Squids.ttf")

    sticker_file = generate_sticker(text, font_path)
    # Send the new sticker back to the user
    bot.send_sticker(message.chat.id, sticker_file)

trigger_messages = {
    'sahu': ('luldeep', None),
    'aditya': ('BNSL BOY', None)
}

@bot.message_handler(commands=['addstic'])
def add_trigger_message(message):
    if len(message.text.split(' ')) > 2:
        trigger = message.text.split(' ', 2)[1].lower()
        sticker_text = message.text.split(' ', 2)[2]
        trigger_messages[trigger] = (sticker_text, message.chat.id)
        bot.reply_to(message, f"New trigger message added: {trigger} -> {sticker_text}")
    else:
        bot.reply_to(message, "<b>Invalid command</b> Usage: <code>/addstic </code><b>trigger message sticker text</b>]" , parse_mode="HTML" )

@bot.message_handler(func=lambda message: any(trigger in message.text.lower() for trigger in trigger_messages.keys()))
def handle_trigger_message(message):
    for trigger, (sticker_text, chat_id) in trigger_messages.items():
        if trigger == 'sahu' or trigger == 'aditya':  # Check for exceptions
            if trigger in message.text.lower():
                font_path = os.path.join(os.getcwd(), "Vampire Wars Italic.ttf")
                sticker_file = generate_sticker(sticker_text, font_path)
                bot.send_sticker(message.chat.id, sticker_file)
                break
        elif chat_id is None or chat_id == message.chat.id:  # Check chat ID
            if trigger in message.text.lower():
                font_path = os.path.join(os.getcwd(), "Vampire Wars Italic.ttf")
                sticker_file = generate_sticker(sticker_text, font_path)
                bot.send_sticker(message.chat.id, sticker_file)
                break


bot.infinity_polling()
