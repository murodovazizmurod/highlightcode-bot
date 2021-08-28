import os
from datetime import datetime
from telebot import TeleBot, types

from pygments.lexers import guess_lexer, TextLexer
from pygments.formatters import ImageFormatter
from pygments import highlight
from ormx import Database
from ormx.models import Table, Column

db = Database('data.db')

class Groups(Table):
    idn = Column(int)
    name = Column(str)


class User(Table):
    idn = Column(int)
    name = Column(str)


db.create(Groups)

db.create(User)

bot = TeleBot('1983932455:AAFjFaK9J4Cpy5v1tJDjbN99AxBoXZsZxY4')

def generate_image(code):
    formatter = ImageFormatter(font_size=16, style="native")
    lexer = guess_lexer(code)
    name = datetime.now().strftime('%d%m%Y_%H%M')
    with open(name+".png", "wb") as f:
        f.write(highlight(code, lexer, formatter))
    return name+".png"


def stat_g(m):
    gr = db.get(Groups, idn=m.chat.id)
    if gr is None:
        g = Groups(idn=m.chat.id, name=m.chat.title)
        db.save(g)

def stat_u(m):
    gr = db.get(User, idn=m.chat.id)
    if gr is None:
        g = User(idn=m.chat.id, name=m.from_user.first_name + m.from_user.last_name)
        db.save(g)

@bot.message_handler(commands=['start'])
def start(m):
    if m.chat.type == 'private':
        try:
            stat_u(m)
        except:
            pass
        bot.reply_to(m, "Hello, friend!\n\nAdd me to group for highlighting all code!")


@bot.message_handler(commands=['statistics'])
def stat(m):
    if m.chat.type == 'private' and m.chat.id == 756639030:
        bot.reply_to(m, f"Groups: {db['groups']}\n\nUsers: {db['user']}")



@bot.message_handler(content_types=['text'])
def text(m):
    if m.chat.type == 'group' or m.chat.type == 'supergroup' or m.from_user.id == 756639030:
        try:
            stat_g(m)
        except:
            pass
        if not isinstance(guess_lexer(m.text), TextLexer):
            try:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(f'Remove (for {m.from_user.first_name or m.from_user.last_name})', callback_data=f'remove#{m.from_user.id}'))
                name = generate_image(m.text)
                bot.send_photo(m.chat.id, photo=open(os.path.join(os.getcwd(), name), 'rb'), caption='You are welcome :)', reply_to_message_id=m.message_id, reply_markup=markup)
                os.remove(os.path.join(os.getcwd(), name))
            except:
                pass
    else:
        bot.reply_to(m, "Sorry, but I can work in groups :(")


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data:
        if call.data.startswith('remove#'):
            uid = call.data.split('#')[1]
            if call.from_user.id == int(uid):
                try:
                    bot.delete_message(call.message.chat.id, call.message.message_id)
                except:
                    pass
            else:
                bot.answer_callback_query(call.id, 'This button not for you :)', show_alert=True)



bot.polling(none_stop=True)


