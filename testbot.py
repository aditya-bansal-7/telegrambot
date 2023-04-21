
import telebot
import json
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from bs4 import BeautifulSoup
import os
from telebot import types
import random 

TOKEN = "1638155581:AAGe4dxE4Cz3GXC2NAuHesSAKpeRgwhmQuw"

bot = telebot.TeleBot(TOKEN)

LEADERBOARD_FILE = 'leaderboard.json'

API_KEY = "2748b8f5-8e99-4210-845d-78176b3a1f62"

REMOVEBG_API_KEY = "wZn1yvKMJoNqfXcwanvbgP8k"


user_to_count = {}


MIN_PIN = 0
MAX_PIN4 = 9999
MAX_PIN6 = 999999
# Define the win xp and score allocation
WIN_XP = 10
SCORE_PER_PIN = 100

# Define the path to the file that stores the user's XP
XP_FILE = os.path.join(os.getcwd(), "user_xp.txt")


# Define the number of attempts
NUM_ATTEMPT4 = random.randint(10, 25)
NUM_ATTEMPT6 = random.randint(15, 30)
# Generate a random PIN code

pin4 = random.randint(MIN_PIN, MAX_PIN4)
pin4_str = '{:04d}'.format(pin4)


pin6 = random.randint(MIN_PIN, MAX_PIN6)
pin6_str = '{:04d}'.format(pin6)


@bot.message_handler(commands=['start'])
def start_command(message):
    markup = types.InlineKeyboardMarkup()
    markup.row(
    types.InlineKeyboardButton('Crypto 💰', callback_data='crypto_menu'),
    types.InlineKeyboardButton('Sticker🎁', callback_data='stic'),
    types.InlineKeyboardButton('Cricket🏏', callback_data='cric'),
    types.InlineKeyboardButton('Games🧩', callback_data='games')
)

    bot.send_message(
        chat_id=message.chat.id,
        text='Welcome to my bot!\n Select One Option 📥',
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
        markup.add(types.InlineKeyboardButton('Return to Main Menu', callback_data='main_menu', 
            # set the button width to be 2/3 of the available space and height to be 2x the default size
            callback_game={'width': 2, 'height': 2}))
        
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
        markup.add(types.InlineKeyboardButton('Return to Main Menu', callback_data='main_menu', 
            # set the button width to be 2/3 of the available space and height to be 2x the default size
            callback_game={'width': 2, 'height': 2}))

            
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

        bot.answer_callback_query(call.id, response_text)


    elif call.data == 'cbin':
        crypto_amount = "1"
        crypto_symbol = "BTC"
        currency = "USD"
        result = convert(crypto_amount, crypto_symbol, currency)
        response_text = f'<code>{crypto_amount} {crypto_symbol} is worth {result:.8f} {currency}</code>.\n\n'
        response_text += f'✨ {crypto_amount} <b>{crypto_symbol}</b> = <code>{result:.5f} {currency}</code> \n\n'
        bot.send_message(call.message.chat.id, response_text, parse_mode="HTML")
    elif call.data == 'cric':
        bot.send_message(
            chat_id=call.message.chat.id,
            text= '<code>/cri</code> - To get all cricket live matches score\n\n <code>/ipl</code> - To get <b>IPL</b> Live match score ',
            parse_mode= "HTML"
        )
    elif call.data == 'main_menu':
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton('Crypto 💰', callback_data='crypto_menu'),
            types.InlineKeyboardButton('Sticker🎁', callback_data='stic'),
            types.InlineKeyboardButton('Cricket🏏', callback_data='cric'),
            types.InlineKeyboardButton('Games🧩', callback_data='games')
        )
        bot.send_message(
            chat_id=call.message.chat.id,
            text='Main Menu',
            reply_markup=markup
        )
    elif call.data == 'games':
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton(
                'Hack ATM 🏧',
                callback_data='atm'
            )
        )
        bot.send_message(
            chat_id=call.message.chat.id,
            text='Available Games ',
            reply_markup=markup
        )
    elif call.data == 'atm':
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton('Start hacking 🏧 x4', callback_data='hack4'),
            types.InlineKeyboardButton('Start hacking 🏧 x6', callback_data='hack6')
        )
        markup.row(
            types.InlineKeyboardButton('ℹ️ Hints 🏧', callback_data='atmhint'),
            types.InlineKeyboardButton('💰 Reward 🏧', callback_data='atmreward'),
            
        )
        markup.row(
            types.InlineKeyboardButton('Return To Main Menu', callback_data='main_menu'),
            
        )
        bot.send_message(
            chat_id=call.message.chat.id,
            text='🏧 Hacking ATMs 🏧\n ➖➖➖➖➖➖ \n🔢 4x PIN (use : /play4x)\n• 10-25 attempts \n• Reward: 250 XP\n• Attempt 10 XP\n➖➖➖➖➖➖\n🔢 6x PIN (use : /play6x)\n• 15-30 attempts\n• Reward: 300 XP\n• Attempt 10 XP',
            reply_markup=markup
        )
    elif call.data == 'hack4':
            global NUM_ATTEMPT4
            NUM_ATTEMPT4 = random.randint(10, 25)
            global pin4
            pin4 = random.randint(MIN_PIN, MAX_PIN4)
            global pin4_str
            pin4_str = '{:04d}'.format(pin4)
            bot.send_message(call.message.chat.id, 'Welcome to the Guess the PIN Code game! You have {} attempts to guess the PIN code.'.format(NUM_ATTEMPT4))
    elif call.data == 'hack6':
            global NUM_ATTEMPT6
            NUM_ATTEMPT6 = random.randint(15, 30)
            global pin6
            pin6 = random.randint(MIN_PIN, MAX_PIN6)
            global pin6_str
            pin6_str = '{:06d}'.format(pin6)
            bot.send_message(call.message.chat.id, 'Welcome to the Guess the PIN Code game! You have {} attempts to guess the PIN code.'.format(NUM_ATTEMPT6))
    elif call.data == 'atmhint':
        message_text = "ℹ️ Hints:\nUse numbers from 0 to 9.\nIf the number is in its place, it will be displayed as 'X'.\nIf the number is in the PIN code but not in its place, then it will be displayed as '0'.\nIf there is no such number, it will be displayed as '_'\n\nFor example, you entered PIN 1234.\nAnd saw the answer _X00\nSo there are no digits 1 in the PIN code, digit 2 is in its place and digits 3 and 4 are out of place.\nTry to enter 3245\nGetting an answer XXX_\nThe first three digits we guessed, it remains to determine the last digit.\nThe principle for hacking a six-digit PIN is the same.\nNumbers in the PIN code can be repeated, for example 3643 or 9299 or 7777\nThat's all."

        bot.send_message(
            chat_id=call.message.chat.id,
            text=message_text
        )
    elif call.data == 'atmreward':
        message_text = "💰 Reward \n🔢 4x PIN\n• 10-25 attempts \n• Reward: 250 XP\n• Attempt 10 XP\n➖➖➖➖➖➖\n🔢 6x PIN\n• 15-30 attempts\n• Reward: 300 XP\n• Attempt 10 XP"

        bot.send_message(
            chat_id=call.message.chat.id,
            text= message_text
        )



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
    # Add inline button for refresh
    markup = types.InlineKeyboardMarkup()
    refresh_button = types.InlineKeyboardButton(text='Refresh', callback_data=f'refresh_{symbol}')
    markup.add(refresh_button)

    bot.reply_to(message, response_text, reply_markup=markup)




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

def generate_image(text, font_path, font_size, text_color, border_color, border_size, padding=10):
    # Create a new image with a transparent background
    # Calculate the required image size based on the text dimensions and padding
    font = ImageFont.truetype(font_path, size=font_size)
    words = text.split()
    max_word_width = max(font.getsize(word)[0] for word in words)
    text_height = sum(font.getsize(word)[1] for word in words)
    size = (max_word_width + 2 * padding, text_height + (len(words) - 1) * padding)

    image = Image.new('RGBA', size, (0, 0, 0, 0))

    # Draw the text onto the image
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_path, size=font_size)

    # Split the text into words
    text = text.replace("kaddu", "luldeep")
    words = text.split()

    # Set the initial y-coordinate
    y = padding // 2

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


def generate_sticker(text, font_path, font_size=100, text_color=(0, 255, 255), border_color=(0, 0, 0), border_size=10):
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

@bot.message_handler(commands=['ipl'])
def send_ipl_scores(message):
    try:
        # Fetch live scores of ongoing IPL matches
        url_data = "https://www.cricbuzz.com/cricket-match/live-scores"
        r = requests.get(url_data)
        soup = BeautifulSoup(r.content, 'html.parser')
        div = soup.find("div", attrs={"ng-show": "active_match_type == 'league-tab'"})
        matches = div.find_all(class_="cb-mtch-lst cb-col cb-col-100 cb-tms-itm")
        
        if len(matches) == 0:
            # No ongoing matches, fetch scores of recently completed matches
            recent_data = "https://www.cricbuzz.com/cricket-match/live-scores/recent-matches"
            r = requests.get(recent_data)
            soup = BeautifulSoup(r.content, 'html.parser')
            div = soup.find("div", attrs={"ng-show": "active_match_type == 'league-tab'"})
            if len(matches) == 0:
                # No ongoing or recently completed matches
                bot.reply_to(message, "No IPL live matches at the moment.")
                return
        
        # Send the live scores to the user
        for match in matches:
            team_names = match.find("h3").text.strip().replace(",", "")
            score = match.find_all("div", attrs={"style": "display:inline-block; width:140px"})[0].text.strip() if match.find_all("div", attrs={"style": "display:inline-block; width:140px"})[0].text.strip() else 'Not yet Started'
            score_two = match.find_all("div", attrs={"style": "display:inline-block; width:140px"})[1].text.strip() if match.find_all("div", attrs={"style": "display:inline-block; width:140px"})[1].text.strip() else 'Not yet Started'
            team_one = match.find_all("div", attrs={"class": "cb-ovr-flo cb-hmscg-tm-nm"})[0].text.strip()
            team_two = match.find_all("div", attrs={"class": "cb-ovr-flo cb-hmscg-tm-nm"})[1].text.strip()
            message_text = f"<b>{team_names}</b>\n\n"\
               f"<a href=''>{team_one}</a> - <code>{score}</code>\n"\
               f"<a href=''>{team_two}</a> - <code>{score_two}</code>"
            bot.reply_to(message, message_text, parse_mode="HTML")
    
    except requests.exceptions.RequestException as e:
        bot.reply_to(message, "Error fetching data. Please try again later.")
        print(e)
bot.delete_webhook()

# get the live cricket score feed
url = "http://static.cricinfo.com/rss/livescores.xml"
r = requests.get(url)
soup = BeautifulSoup(r.text, "lxml")

# create a dictionary of match links
match_links = {}
for item in soup.findAll("item"):
    match_links[item.find("description").text] = item.find("guid").text

# send the match options when the user starts the bot
@bot.message_handler(commands=['cri'])
def handle_start(message):
    bot.send_message(message.chat.id, "This feature is in Beta .")
    send_match_options(message.chat.id)

# function to send the match options to the user
def send_match_options(chat_id):
    message = "All Live Cricket Matches:"
    keyboard = []
    for match in match_links:
        keyboard.append([types.InlineKeyboardButton(match, callback_data=match)])
    reply_markup = types.InlineKeyboardMarkup(keyboard)
    bot.send_message(chat_id, message, reply_markup=reply_markup)

# function to handle callback queries
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    match = call.data
    url = match_links[match]
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "lxml")
    score = soup.find("title").text
    bot.send_message(call.message.chat.id, score)

# function to send the live cricket score every 10 seconds
def send_live_score(chat_id, match):
    url = match_links[match]
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "lxml")
    score = soup.find("title")
    r.raise_for_status()
    current_score_string = str(score[0].text)
    bot.send_message(chat_id, current_score_string)
    bot.send_message(chat_id, score)
@bot.message_handler(commands=['rmbg'])
def remove_background(message):
    # Check if the message has a photo in reply
    if message.reply_to_message and message.reply_to_message.photo:
        # Get the photo file ID
        file_id = message.reply_to_message.photo[-1].file_id
        # Download the photo
        file_info = bot.get_file(file_id)
        file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(TOKEN, file_info.file_path))
        # Save the photo locally
        with open('image.jpg', 'wb') as f:
            f.write(file.content)
        # Send a "working" message
        bot.send_message(message.chat.id, "Removing background...")
        # Send a request to remove.bg API
        response = requests.post(
            'https://api.remove.bg/v1.0/removebg',
            files={'image_file': open('image.jpg', 'rb')},
            data={'size': 'auto'},
            headers={'X-Api-Key': REMOVEBG_API_KEY},
        )
        # Check for errors
        if response.status_code == requests.codes.ok:
            # Save the output image locally
            with open('output.png', 'wb') as f:
                f.write(response.content)
            # Send the output image
            with open('output.png', 'rb') as f:
                bot.send_photo(message.chat.id, f)
        else:
            bot.send_message(message.chat.id, "Failed to remove background.")
        # Delete the temporary files
        os.remove('image.jpg')
        os.remove('output.png')
    else:
        bot.reply_to(message, "Please reply to a photo with /rmbg to remove its background.")


# Define a command handler
@bot.message_handler(commands=['play4x'])
def start(message):
    global NUM_ATTEMPT4
    NUM_ATTEMPT4 = random.randint(10, 25)
    global pin4
    pin4 = random.randint(MIN_PIN, MAX_PIN4)
    global pin4_str
    pin4_str = '{:04d}'.format(pin4)
    bot.send_message(message.chat.id, 'Welcome to the Guess the PIN Code game! You have {} attempts to guess the PIN code.'.format(NUM_ATTEMPT4))

@bot.message_handler(commands=['play6x'])
def start(message):
    global NUM_ATTEMPT6
    NUM_ATTEMPT6 = 35
    global pin6
    pin6 = random.randint(MIN_PIN, MAX_PIN6)
    global pin6_str
    pin6_str = '{:06d}'.format(pin6)
    bot.send_message(message.chat.id, 'Welcome to the Guess the PIN Code game! You have {} attempts to guess the PIN code.'.format(NUM_ATTEMPT6))

@bot.message_handler(commands=['level'])
def level(message):
    user_id = message.from_user.id
    result = get_user_level(user_id)
    level, xpoints = result
    bot.send_message(message.chat.id, f"You are at level {level} with {xpoints} XP points.")

@bot.message_handler(commands=['guess'])
def guess(message):
    user_id = message.from_user.id
    xpq = 10 + get_user_xp(user_id)
    xp_points = update_user_xp(user_id, xpq)
    bot.send_message(message, f"You guessed it right! You now have {xp_points} XP points.")

@bot.message_handler(commands=['stop4x'])
def stop(message):
    bot.send_message(message.chat.id, 'Game over. The PIN code was {}.'.format(pin4_str))

@bot.message_handler(commands=['stop6x'])
def stop(message):
    bot.send_message(message.chat.id, 'Game over. The PIN code was {}.'.format(pin6_str))

@bot.message_handler(func=lambda message: True)
def guess(message):
    global NUM_ATTEMPT4, NUM_ATTEMPT6  # Declare the variables as global before using them
    try:
        # Parse the user's guess
        guess_str = message.text
        guess = int(guess_str)
    except ValueError:
       None
       return

    # Determine which pin and number of attempts to use based on the length of the guess string
    if len(guess_str) == 4:
        pin = pin4
        pin_str = pin4_str
        NUM_ATTEMPTS = NUM_ATTEMPT4
        xp = WIN_XP * NUM_ATTEMPT4
        score = SCORE_PER_PIN * pin4
    elif len(guess_str) == 6:
        pin = pin6
        pin_str = pin6_str
        NUM_ATTEMPTS = NUM_ATTEMPT6
        xp = WIN_XP * NUM_ATTEMPT6
        score = SCORE_PER_PIN * pin6
    else:
        return

    # Check if the guess is correct
    if guess == pin:
        try:
            user_id = message.from_user.id
            xp_points = xp + get_user_xp(user_id)
            update_user_xp(user_id, xp_points)
        except IOError:
            bot.send_message(message.chat.id, "Sorry, an error occurred while updating your XP points. Please try again later.")
            return
        bot.send_message(message.chat.id, 'Congratulations! You guessed the PIN code and won {} XP and {} score.'.format(xp, score))
        change_pin()
        
    else:
        # Decrement the number of attempts
        NUM_ATTEMPTS -= 1  # Use the variable after declaring it as global
        if NUM_ATTEMPTS == 0:
            bot.send_message(message.chat.id, 'Game over. The PIN code was {}.'.format(pin_str))
            return
        else:
            # Give the user a hint
            hint = ''
            for i in range(len(pin_str)):
                if guess_str[i] == pin_str[i]:
                    hint += 'X'
                elif guess_str[i] in pin_str:
                    hint += '0'
                else:
                    hint += '_'
            bot.send_message(message.chat.id, 'Hint: {}'.format(hint))
            return

def change_pin():
    global pin4, pin4_str, pin6 ,pin6_str
    pin4 = random.randint(MIN_PIN, MAX_PIN4)
    pin4_str = '{:04d}'.format(pin4)


    pin6 = random.randint(MIN_PIN, MAX_PIN6)
    pin6_str = '{:04d}'.format(pin6)

# function to update user's XP points
def update_user_xp(user_id, xp_points):
    xp_file = os.path.join(os.getcwd(), "user_xp.txt")
    try:
        with open(xp_file, "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        bot.send_message(user_id, "Sorry, there was an error updating your XP points. Please try again later.")
        return

    # find the line for the user
    for i in range(len(lines)):
        if lines[i].startswith(str(user_id)):
            lines[i] = str(user_id) + ": " + str(xp_points) + "\n"
            break
    else:
        # if the user is not found in the file, add a new line for them
        lines.append(str(user_id) + ": " + str(xp_points) + "\n")

    try:
        # write the updated contents back to the file
        with open(xp_file, "w") as f:
            f.writelines(lines)
    except IOError:
        bot.send_message(user_id, "Sorry, there was an error updating your XP points. Please try again later.")
        return
    
    return xp_points

def get_user_xp(user_id):
    with open("user_xp.txt", "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith(str(user_id)):
                xp_points = int(line.split(":")[1])
                return xp_points
    return 0  # If the user ID is not found in the file, return 0 XP points

# Define the XP thresholds for each level
LEVEL_XP_THRESHOLDS = [0, 1000, 2000, 4000, 8000, 16000, 32000, 99999]

# function to get user's level
def get_user_level(user_id):
    xp = get_user_xp(user_id)
    level = 0
    for i, threshold in enumerate(LEVEL_XP_THRESHOLDS):
        if xp >= threshold:
            level = i
            xpoints= f'{xp} / {threshold}'
    return level, xpoints

bot.infinity_polling()
