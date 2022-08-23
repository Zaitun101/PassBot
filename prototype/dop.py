import datetime
import time


def get_status_symbol(row):
    status = ''
    if row[6] == 0:
        status = '⏳'
    elif row[6] == 1:
        status = '✅'
    elif row[6] == 2:
        status = '⛔️'
    elif row[6] == 3:
        status = 'Использован'
    if row[6] != 3 and delta_days(row[5]) == -1:
        status = 'Истек'
    return status


def delta_days(date_str):
    try:
        time.strptime(date_str, '%d.%m.%Y')   # for try
        obj = datetime.datetime.strptime(date_str, '%d.%m.%Y')
        if obj > datetime.datetime.today():
            return 1
        elif obj < datetime.datetime.today():
            return -1
    except ValueError:
        return 0
