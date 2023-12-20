import csv
import datetime

def statistics(user_id, command):
    data = datetime.datetime.today().strftime("%Y-%m-%d")
    with open('data.csv', 'a', newline="", encoding='UTF-8') as fil:
        wr = csv.writer(fil, delimiter=';')
        wr.writerow([data, user_id, command])


