from datetime import datetime
import requests


def transform_date(date):
    return datetime.strptime(date[:10], "%Y-%m-%d")


def get_month(date):
    month = date.month

    if month == 1:
        month = "января"
    elif month == 2:
        month = "февраля"
    elif month == 3:
        month = "марта"
    elif month == 4:
        month = "апреля"
    elif month == 5:
        month = "мая"
    elif month == 6:
        month = "июня"
    elif month == 7:
        month = "июля"
    elif month == 8:
        month = "августа"
    elif month == 9:
        month = "сентября"
    elif month == 10:
        month = "октября"
    elif month == 11:
        month = "ноября"
    elif month == 12:
        month = "декабря"

    return month


def get_day(date):
    return date.day


def get_year(date):
    return date.year


def get_year_print(str_date):
    date = transform_date(str_date)
    return date.year


def get_tournament_date(date_start, date_end):
    start = transform_date(date_start)
    end = transform_date(date_end)

    sy = get_year(start)
    sm = get_month(start)
    sd = get_day(start)
    ey = get_year(end)
    em = get_month(end)
    ed = get_day(end)

    return prepare_tournament_date(sd, ed, sm, em, sy, ey)


def get_short_tournament_date(date_start, date_end):
    start = transform_date(date_start)
    end = transform_date(date_end)

    sm = get_month(start)
    sd = get_day(start)
    em = get_month(end)
    ed = get_day(end)

    return prepare_short_date(sd, ed, sm, em)


def inflect_town(town_name):
    common_consonants = 'бвгджзклмнпрстфхцчшщ'
    uncommon_consonants = 'ь'
    common_vowels = 'ая'
    # uncommon_vowels = 'еиуыёюэ'
    # special_vowels = 'о'

    if town_name[-1] in common_consonants:
        inflected_town_name = town_name + 'е'
    elif town_name[-1] in uncommon_consonants:
        inflected_town_name = town_name[:-1] + 'и'
    elif town_name[-1] in common_vowels:
        inflected_town_name = town_name[:-1] + 'е'
    else:
        inflected_town_name = town_name

    return inflected_town_name


def prepare_tournament_date(sd, ed, sm, em, sy, ey):
    if sy == ey:
        if sm == em:
            if sd == ed:
                tournament_date = f"{sd} {sm} {sy} года"
            else:
                tournament_date = f"{sd}–{ed} {sm} {sy} года"
        else:
            tournament_date = f"{sd} {sm}–{ed} {em} {ey} года"
    else:
        tournament_date = f"{sd} {sm} {sy} года – {ed} {em} {ey} года"

    return tournament_date


def prepare_short_date(sd, ed, sm, em):
    if sm == em:
        if sd == ed:
            tournament_date = f"{sd} {sm}"
        else:
            tournament_date = f"{sd}–{ed} {sm}"
    else:
        tournament_date = f"{sd} {sm}–{ed} {em}"

    return tournament_date


def get_city_tournament(city_id):
    try:
        url_town = f'https://api.rating.chgk.net/towns/{city_id}.json'
        t = requests.get(url_town)
        object_city = t.json()
        city_tournament = object_city['name']
    except:
        print(f'Problems with url_town={city_id}')

    return city_tournament


def get_inflected_city_tournament(city_id):
    city_name = get_city_tournament(city_id)

    return inflect_town(city_name)

