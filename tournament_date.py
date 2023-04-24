from datetime import datetime, date

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


