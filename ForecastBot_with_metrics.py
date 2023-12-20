import pandas
import requests
from bs4 import BeautifulSoup
import telebot
from telebot import types
import csv
from collections import defaultdict
import datetime

token = '6251441992:AAH0M7hYNl81Clpa7coj8kPijBySNZq_yuw'
admin_chat_id = 307192030
bot = telebot.TeleBot(token)
standardized_team_names = {
            'АК БАРС': 'АК БАРС',
            'АКБАРС': 'АК БАРС',
            'КУНЬЛУНЬ': 'КУНЬЛУНЬ РЕД СТАР',
            'КУНЬЛУНЬ РЕД СТАР': 'КУНЬЛУНЬ РЕД СТАР',
            'КУНЬЛУНЬРЕДСТАР': 'КУНЬЛУНЬ РЕД СТАР',
            'ДИНАМО МСК': 'ДИНАМО МСК',
            'ДИНАМОМСК': 'ДИНАМО МСК',
            'ДИНАМО МОСКВА': 'ДИНАМО МСК',
            'ДИНАМОМОСКВА': 'ДИНАМО МСК',
            'ДИНАМО МН': 'ДИНАМО МН',
            'ДИНАМОМН': 'ДИНАМО МН',
            'ДИНАМО МИНСК': 'ДИНАМО МН',
            'ДИНАМОМИНСК': 'ДИНАМО МН',
            'ЦСКА': 'ЦСКА',
            'СКА': 'СКА',
            'МЕТАЛЛУРГ': 'МЕТАЛЛУРГ МГ',
            'МЕТАЛЛУРГ МГ': 'МЕТАЛЛУРГ МГ',
            'МЕТАЛЛУРГМГ': 'МЕТАЛЛУРГ МГ',
            'МЕТАЛЛУРГ МАГНИТОГОРСК': 'МЕТАЛЛУРГ МГ',
            'МЕТАЛЛУРГМАГНИТОГОРСК': 'МЕТАЛЛУРГ МГ',
            'САЛАВАТ': 'САЛАВАТ ЮЛАЕВ',
            'САЛАВАТ ЮЛАЕВ': 'САЛАВАТ ЮЛАЕВ',
            'САЛАВАТЮЛАЕВ': 'САЛАВАТ ЮЛАЕВ',
            'АВТО': 'АВТОМОБИЛИСТ',
            'АВТОМОБИЛИСТ': 'АВТОМОБИЛИСТ',
            'ТРАКТОР': 'ТРАКТОР',
            'СПАРТАК': 'СПАРТАК',
            'ЛАДА': 'ЛАДА',
            'АВАНГАРД': 'АВАНГАРД',
            'ЛОКОМОТИВ': 'ЛОКОМОТИВ',
            'ЛОКО': 'ЛОКОМОТИВ',
            'ТОРПЕДО': 'ТОРПЕДО',
            'СЕВЕРСТАЛЬ': 'СЕВЕРСТАЛЬ',
            'АМУР': 'АМУР',
            'НЕФТЕХИМИК': 'НЕФТЕХИМИК',
            'СИБИРЬ': 'СИБИРЬ',
            'СОЧИ': 'СОЧИ',
            'БАРЫС': 'БАРЫС',
            'ВИТЯЗЬ': 'ВИТЯЗЬ',
            'АДМИРАЛ': 'АДМИРАЛ'
        }
HELP = '''
Список доступных команд:
⚠️/start  - для запуска программы
⚠️/statistics - для просмотра статистики бота
'''
def statistics(user_id, command):
    data = datetime.datetime.today().strftime("%Y-%m-%d")
    with open('data.csv', 'a', newline="", encoding='UTF-8') as fil:
        wr = csv.writer(fil, delimiter=';')
        wr.writerow([data, user_id, command])

@bot.message_handler(commands=['statistics'])
def statistics_command(message):
    # Здесь получите идентификатор чата текущего пользователя
    chat_id = message.chat.id
    # Проверка идентификатора чата, чтобы предоставить доступ только одному пользователю
    if chat_id == admin_chat_id:
        bot.reply_to(message, "Вы имеете доступ к команде '/statistics'.")
        stats_by_date = defaultdict(lambda: defaultdict(int))
        unique_users = set()

        # Чтение данных из файла data.csv с указанием кодировки
        with open('data.csv', 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=';')
            for row in reader:
                date, user_id, *commands = row

                # Добавляем пользователя в множество уникальных пользователей
                unique_users.add(user_id)

                # Определяем команды для подсчета
                relevant_commands = ['/start', '/help']
                special_commands = ['Таблица КХЛ', 'Рассчитать исход матча']

                # Увеличиваем счетчики для команд и вводов пользователей
                for cmd in commands:
                    if cmd in relevant_commands:
                        stats_by_date[date][cmd] += 1
                    elif cmd in special_commands:
                        stats_by_date[date][cmd] += 1
                    else:
                        stats_by_date[date]['Ввод команд'] += 1

        # Формируем текст статистики для отправки
        total_unique_users = len(unique_users)
        statistics_text = f"Статистика использования бота:\n"
        statistics_text += f"За все время бота использовало: {total_unique_users} пользователей\n"

        for date, commands in stats_by_date.items():
            statistics_text += f"\nСтатистика за дату {date}:\n"
            for command, count in commands.items():
                statistics_text += f"{command}: {count} раз\n"

        # Отправляем статистику в Telegram
        bot.send_message(message.chat.id, statistics_text)
    else:
        # Если идентификатор чата не совпадает, сообщите о запрете доступа
        bot.reply_to(message, "Извините, у вас нет доступа к этой команде.")

@bot.message_handler(commands=['help'])
def help(message):
    statistics(message.chat.id, message.text)
    bot.send_message(message.chat.id, HELP)


@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    statistics(message.chat.id, message.text)
    btn1 = types.KeyboardButton("Таблица КХЛ")
    btn2 = types.KeyboardButton("Рассчитать исход матча")
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id,
                     text="Привет, {0.first_name}! Кто же сегодня выиграет?".format(
                         message.from_user), reply_markup=markup)


def exception_checking(team):
        return standardized_team_names.get(team.upper(), team)


def find_team_rating(team_name):
    url = "https://pribalt.info/hokkei/khl/tablica/chempionat"
    response = requests.get(url)
    if response.status_code == 200:
        html_code = response.text
        soup = BeautifulSoup(html_code, 'html.parser')
        club_data = []
        for div in soup.find_all('div', class_='stroka_blok'):
            club_name_elem = div.find('a')
            games_played_elems = div.find_all('div', class_='sbn_tab_igry')
            goals_elem = div.find('div', class_='sbn_tab_shaiby')
            club_points_elem = div.find('div', class_='sbn_tab_ochki')
            if club_name_elem and len(games_played_elems) == 7 and goals_elem and club_points_elem:
                club_name = club_name_elem.text.strip()
                wins = int(games_played_elems[1].text.strip())  # ПОБЕД В ОСНОВУ
                wins_overtime = int(games_played_elems[2].text.strip())  # ВО
                wins_shootout = int(games_played_elems[3].text.strip())  # ВБ
                losses_shootout = int(games_played_elems[4].text.strip())  # ПБ
                losses_overtime = int(games_played_elems[5].text.strip())  # ПО
                losses = int(games_played_elems[6].text.strip())  # П
                goals = goals_elem.text.strip()
                club_points = int(club_points_elem.text.strip())
                draws = wins_overtime + wins_shootout + losses_shootout + losses_overtime
                goals_for = int(goals.split('—')[0])
                goals_against = int(goals.split('—')[1])
                goal_difference = goals_for / goals_against if goals_against != 0 else 0
                rating = 10 + wins * 1 + draws * 0.5 + losses * 0 + goal_difference + (wins / (wins + draws + losses))
                club_data.append({
                    'Клуб': club_name,
                    'Выигрыши': wins,
                    'Ничья': draws,
                    'Проигрыши': losses,
                    'Забито': goals_for,
                    'Пропущено': goals_against,
                    'Шайб З/П': round(goal_difference, 2),
                    'Очки': club_points,
                    'Рейтинг': round(rating, 2)
                })

        df = pandas.DataFrame(club_data)
        # Удаление чисел и точек из названий клубов, приведение к верхнему регистру без пробелов
        df['Клуб'] = df['Клуб'].str.replace(r'[^a-zA-Zа-яА-Я\s]', '', regex=True).str.upper()
        clubs_dict = dict(zip(df['Клуб'].str.strip(), df['Рейтинг']))
        ratingteam = clubs_dict.get(team_name)
        return ratingteam

command_one = ""
command_two = ""
@bot.message_handler(content_types='text')
def message_reply(message):
    if message.text == "Таблица КХЛ":
        statistics(message.chat.id, message.text)
        bot.send_message(message.chat.id, khl_table())
    elif message.text == 'Рассчитать исход матча':
        chat_id = message.chat.id
        get_command_one(message)
forecasts = []

def get_command_one(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Введите первую команду:")
    statistics(message.chat.id, message.text)
    bot.register_next_step_handler(message, save_command_one)

def save_command_one(message):
    global command_one
    chat_id = message.chat.id
    team = exception_checking(message.text)
    while team not in standardized_team_names.values():
        bot.send_message(chat_id, "Такой команды нет!\nВведите первую команду еще раз:")
        bot.register_next_step_handler(message, save_command_one)
        return
    command_one = team
    bot.send_message(chat_id, "Введите вторую команду:")
    statistics(message.chat.id, message.text)
    bot.register_next_step_handler(message, save_command_two)

def save_command_two(message):
    global command_two
    chat_id = message.chat.id
    statistics(message.chat.id, message.text)
    team = exception_checking(message.text)
    while team not in standardized_team_names.values():
        bot.send_message(chat_id, "Такой команды нет!\nВведите вторую команду еще раз:")
        bot.register_next_step_handler(message, save_command_two)
        return
    command_two = team
    df = pandas.DataFrame
    Ra = find_team_rating(command_one)
    Rb = find_team_rating(command_two)
    Pa = 1 / (1 + 10 ** ((Rb - Ra) / 4))
    if Pa > 0.4 and Pa < 0.6:
        bot.send_message(chat_id,
                         f"Команда {command_one} и команда {command_two} играют на равне!\nДавай воздержимся от прогноза на этот матч!")
    elif Pa <= 0.4:
        bot.send_message(chat_id, f"Команда {command_two} выиграет команду {command_one}!")
    elif Pa >= 0.6:
        bot.send_message(chat_id, f"Команда {command_one} выиграет команду {command_two}!")
    forecast = f"Команда {command_one} выиграет команду {command_two}!"
    forecasts.append(forecast)

def khl_table():
    url = "https://pribalt.info/hokkei/khl/tablica/chempionat"
    response = requests.get(url)

    if response.status_code == 200:
        html_code = response.text
        soup = BeautifulSoup(html_code, 'html.parser')
        club_data = []

        for div in soup.find_all('div', class_='stroka_blok'):
            club_name_elem = div.find('a')
            games_played_elems = div.find_all('div', class_='sbn_tab_igry')
            goals_elem = div.find('div', class_='sbn_tab_shaiby')
            club_points_elem = div.find('div', class_='sbn_tab_ochki')

            if club_name_elem and len(games_played_elems) == 7 and goals_elem and club_points_elem:
                club_name = club_name_elem.text.strip()
                club_data.append({
                    'Таблица КХЛ': club_name,
                })

        df = pandas.DataFrame(club_data)

        df['Таблица КХЛ'] = df['Таблица КХЛ'].str.ljust(30)

        return (df.to_string(index=False))
# Run the bot
bot.polling(interval=5)
