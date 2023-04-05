
import telebot
import json
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from bs4 import BeautifulSoup


TOKEN = "1638155581:AAF22vq5PfZx1CjQT1guvgspLIY3kmE9z-Y"

bot = telebot.TeleBot(TOKEN)

LEADERBOARD_FILE = 'leaderboard.json'

API_KEY = "2748b8f5-8e99-4210-845d-78176b3a1f62"

user_to_count = {}

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
    response_text = f'`{crypto_amount}` {crypto_symbol} is worth `{result:.8f}` {currency}.\n\n'
    response_text += f'✨ {crypto_amount} {crypto_symbol} = {result:.5f} {currency} \n\n'
    #response_text += f'✨ Current {crypto_symbol} price: {price:.2f} INR\n'
    #response_text += f'✨ Last 24 hours change: {percent_change_24h:.2f}%'
    bot.reply_to(message, response_text)

def generate_sticker(text):
    # Create a new image with a transparent background
    size = (512, 512)
    image = Image.new('RGBA', size, (0, 0, 0, 0))

    # Draw the text onto the image
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype('C:\\Users\\adibn\\OneDrive\\Desktop\\telegram\\Vampire Wars Italic.ttf', size=100)
    text_color = (255, 255, 255)
    border_color = (0, 0, 0)
    border_size = 10
    words = text.split()
    y = (size[1] - (len(words) * 100)) / 2
    for word in words:
        text_width, text_height = draw.textsize(word, font=font)
        x = (size[0] - text_width) / 2
        draw.text((x, y), word, fill=text_color, font=font, stroke_width=border_size, stroke_fill=border_color)
        y += 100

    # Convert the image to a sticker file
    sticker_file = BytesIO()
    image.save(sticker_file, format='PNG')
    sticker_file.seek(0)

    return sticker_file


# Define a function to handle incoming text messages
@bot.message_handler(commands=['stic'])
def handle_text_message(message):  
    # Check if the message has text
    if len(message.text.split(' ')) > 1:
        # Get the text from the message command
        text = message.text.split(' ', 1)[1]
    else:
        text = "Bnsl Boy"


    # Generate a new sticker from the text
    sticker_file = generate_sticker(text)

    # Send the new sticker back to the user
    bot.send_sticker(message.chat.id, sticker_file)


# Get live match links
url = "http://static.cricinfo.com/rss/livescores.xml"
r = requests.get(url)
soup = BeautifulSoup(r.text, "lxml")

i = 1
links = []
for item in soup.findAll("item"):
    links.append(item.find("guid").text)
    i += 1

# Set up handlers for user input
@bot.message_handler(commands=['cri'])
def handle_start(message):
    bot.send_message(message.chat.id, "Live Cricket Score !")
    send_match_options(message.chat.id)


# Helper functions
def send_match_options(chat_id):
    message = "Select a match:\n"
    i = 1
    for item in soup.findAll("item"):
        message += "👉  " + item.find("description").text + "\n"
        i += 1
    bot.send_message(chat_id, message)

bot.polling()
