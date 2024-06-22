import requests
from t_fashion import get_tournament_date, get_year_print, inflect_town
from roman_arabic_numerals import conv
import sys
import argparse
from operator import attrgetter
import os
import csv
import json
import constants

id_team_name = {}
id_town_name = {}
id_team_name_id_town = {}


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file')
    parser.add_argument('-c', '--cyr')
    parser.add_argument('-n', '--number')
    parser.add_argument('-g', '--game')
    parser.add_argument('-t', '--test')

    return parser


class Awardee:
    def __init__(self, id, game='chgk'):
        self.id = id
        self.game = game
        self.sum = 0
        self.gold = 0
        self.silver = 0
        self.bronze = 0

    def __dict__(self):
        return {"id": id, "game": game, "sum": sum, "gold": gold, "silver": silver, "bronze": bronze}


class superAwardee(Awardee):
    games = {}  # example: {'chgk': Awardee, 'br': Awardee}

    def add_game(self, awardee):
        if self.id == awardee.id:
            self.games[awardee.game] = awardee
        else:
            print('Не совпадают id у добавляемого призёра.')

        self.sum += awardee.sum
        self.gold += awardee.gold
        self.silver += awardee.silver
        self.bronze += awardee.bronze


class Team:
    def __init__(self, id, name, city, players):
        self.id = id
        self.name = name
        self.city = city
        self.players = players

    def __dict__(self):
        return {"id": id, "name": name, "city": city, "players": players}

class Player:
    def __init__(self, id, name, surname):
        self.id = id
        self.name = name
        self.surname = surname

    def __dict__(self):
        return {"id": id, "name": name, "surname": surname}


def count_champions(awardees_counting_dict, id, place, game='chgk'):
    awardee = awardees_counting_dict.get(id)
    if awardee is None:
        awardee = Awardee(id)

    if place == 0:
        awardee.gold += 1
    elif place == 1:
        awardee.silver += 1
    elif place == 2:
        awardee.bronze += 1
    else:
        print(f"Error with place={place} from awardee with id={id}")
    awardee.sum += 1
    awardees_counting_dict[id] = awardee

    return awardees_counting_dict


def count_other_game(csv, game):
    pass


def get_player(raw_player):
    id_player = raw_player['id']
    name_player = raw_player['name']
    surname_player = raw_player['surname']
    player = Player(id_player, name_player, surname_player)

    return player


def get_prizer(id_tournament, list_tournament, place):
    try:
        raw_team = list_tournament[place]
    except:
        print(f"Problems with choice team № {place} in tournament id={id_tournament}")
    team_id = get_prizer_id(raw_team)
    team_name = get_prizer_name(raw_team)
    team_city = get_prizer_town(raw_team)
    try:
        players = raw_team['teamMembers']
    except:
        players = []
    team = Team(team_id, team_name, team_city, players)

    return team

def get_team_dict(team, players):
    return {"id": team.id, "name": team.name, "actual_name": "", "city": team.city, "players": players}

def get_player_dict(player):
    return {"name": player.name, "old_name": "", "surname": player.surname, "old_surname": ""}

def get_prizer_name(team):
    team_name = team['team']['name']
    team_id = get_prizer_id(team)
    id_team_name.update({team_id: team_name})

    return team_name


def get_prizer_id(team):
    return team['team']['id']


def get_prizer_town(team):
    team_town_id = team['team']['town']['id']
    team_town = team['team']['town']['name']
    id_team_name_id_town.update({get_prizer_id(team): team_town_id})
    id_town_name.update({team_town_id: team_town})

    return team_town


def get_city_tournament(city_id):
    city_tournament = id_town_name.get(city_id)

    if city_tournament is None:
        try:
            url_town = f'https://api.rating.chgk.net/towns/{city_id}.json'
            t = requests.get(url_town)
            object_city = t.json()
            city_tournament = object_city['name']
        except:
            print(f'Problems with url_town={city_id}')

    return city_tournament


def get_country_contributors(id_tournament):
    url_results = f'https://api.rating.chgk.net/tournaments/{id_tournament}/' \
                  f'results.json?includeTeamMembers=1&includeTeamFlags=1'
    r = requests.get(url_results)
    country_contributors = []

    # check championship flags
    try:
        list_t = r.json()
        for l in list_t:
            flags = l['flags']
            if len(flags) > 0:
                flag = flags[0]['id']
                if flag == 50:
                    country_contributors.append(l)
        if len(country_contributors) == 0:
            country_contributors = list_t
    except:
        print(f"json doesn't work with id={id_tournament}")
        url_results = f'https://api.rating.chgk.net/tournaments/{id_tournament}/results.json'
        r = requests.get(url_results)
        country_contributors = r.json()

    return country_contributors


def transform_file2list(file):
    file = open(file, 'r', encoding='utf-8')
    lines = file.readlines()
    lines = [line.rstrip('\n') for line in lines]

    file.close()

    return lines


def save_to_json(list_tournaments, country):
    with open(f'{country}_json.txt', 'w') as outfile:
        json.dump(list_tournaments, outfile)


def open_from_json(country):
    with open(f'{country}_json.txt') as json_file:
        country_info = json.load(json_file)
    return country_info


def update_by_id(id):

    # TODO
    pass


def update_name_team(name):
    # TODO
    pass

def get_list_tournaments(list):
    # TODO
    pass

def get_tournament_info(id_tournament):
    url_common_info = f'https://api.rating.chgk.net/tournaments/{id_tournament}.json'

    k = requests.get(url_common_info)
    try:
        list_tour = k.json()
    except:
        print(f'problems with tournament id={id_tournament} in url_common_info')

    try:
        date_start = list_tour['dateStart']
        date_end = list_tour['dateEnd']
        city_id = list_tour['idtown']
    except:
        print(f'Problem with extracting dates and town tournament id={id_tournament}')

    try:
        city_tournament = inflect_town(get_city_tournament(city_id))
    except:
        print(f"Problem with inflecting town at tournament with id {id_tournament}")

    tournament_date = get_tournament_date(date_start, date_end)
    ey = get_year_print(date_end)
    country_contributors = get_country_contributors(id_tournament)

    return tournament_date, city_tournament, ey, country_contributors


def calculate_from_ids(filename, country_cyrillic, game, number):
    f = transform_file2list(filename)
    country = filename[:-4]


    if number is None:
        number_champ = len(f)
    else:
        number_champ = number

    country_info = dict()

    team_count = {}
    player_count = {}
    player_id_name = {}
    country_info[country] = {"country_cyrillic": country_cyrillic,
                             "first_year": None,
                             "description": "",
                             "years": {}
                             }
    t_errors = {'first': [], 'second': [], 'third': []}

    for id_tournament in f:
        champ = {}
        awardees_counting_dict_teams = {}
        awardees_counting_dict_players = {}
        tournament_date, city_tournament, ey, country_contributors = get_tournament_info(id_tournament)

        champ["number"] = number_champ
        champ["game"] = game
        champ["date"] = tournament_date
        champ["city"] = city_tournament
        champ["year"] = ey
        champ["links"] = []

        for i in range(0, 3):
            team = get_prizer(id_tournament, country_contributors, i)
            team_count = count_champions(team_count, team.id, i)
            if len(team.players) > 0:
                for p in team.players:
                    player = get_player(p['player'])
                    player_id_name.update({player.id: f"{player.name} {player.surname}"})
                    player_count = count_champions(player_count, player.id, 0)
                    awardees_counting_dict_players[player.id] = get_player_dict(player)
            else:
                t_errors['first'].append(id_tournament)

            awardees_counting_dict_teams[i] = get_team_dict(team, awardees_counting_dict_players)

        champ['awardees'] = awardees_counting_dict_teams
        link = f'https://rating.chgk.info/tournament/{id_tournament}'
        champ['links'].append(link)
        champ['links_description'] = f'\nПолные результаты на [турнирном сайте]({link})\n'
        country_info[country]["years"][id_tournament] = champ

        number_champ -= 1

    awardees_counting_dict_teams = {}
    for t in team_count.values():
        team = {'name': id_team_name.get(t.id), 'city': id_town_name.get(id_team_name_id_town.get(t.id)),
                'sum': t.sum, 'gold': t.gold, 'silver': t.silver, 'bronze': t.bronze}
        awardees_counting_dict_teams[t.id] = team

    country_info[country]["count_teams"] = {game: awardees_counting_dict_teams}

    awardees_counting_dict_players = {}
    for p in player_count.values():
        player = {"name_surname": player_id_name.get(p.id), "sum": p.sum, "gold": p.gold, "silver": p.silver,
                  "bronze": p.bronze}
        awardees_counting_dict_players[p.id] = player

    country_info[country]["count_players"] = {game: awardees_counting_dict_players}

    save_to_json(country_info, country)

def get_chgk_stats_from_id(filename, country_cyrillic, number):
    f = transform_file2list(filename)
    country = filename[:-4]

    if number is None:
        number_champ = len(f)
    else:
        number_champ = number

    ff = open(f'{constants.FILE_PATH}{country}_output_years.txt', 'w')
    f_cap = open(f'{constants.FILE_PATH}{country}_output_cap.txt', 'w')
    f_count = open(f'{constants.FILE_PATH}{country}_output_count.txt', 'w')
    f_errors = open(f'{constants.FILE_PATH}{country}_errors.txt', 'w')
    team_count = {}
    player_count = {}
    player_id_name = {}
    t_errors = {'first': [], 'second': [], 'third': []}

    for id_tournament in f:
        tournament_date, city_tournament, ey, country_contributors = get_tournament_info(id_tournament)

        name_tournament = f'{conv.arab_rom(number_champ)} чемпионат {country_cyrillic}'

        team_1 = get_prizer(id_tournament, country_contributors, 0)
        team_count = count_champions(team_count, team_1.id, 0)

        ff.write(f'\n**{name_tournament}** прошёл {tournament_date} в {city_tournament}. <a name="{ey}"></a>\n')
        ff.write(f"\nПобедитель: **[{team_1.name} ({team_1.city})](https://rating.chgk.info/teams/{team_1.id})**\n")

        if len(team_1.players) > 0:
            for p in team_1.players:
                player = get_player(p['player'])
                name_surname = f"{player.name} {player.surname}"
                player_id_name.update({player.id: name_surname})
                player_count = count_champions(player_count, player.id, 0)

                ff.write(f'- {name_surname}\n')
        else:
            ff.write(f'\n{constants.PLAYERS_ERROR}\n')
            t_errors['first'].append(id_tournament)
            f_errors.write(f'- [{name_tournament}](https://rating.chgk.info/tournament/{id_tournament}) '
                           f'— нет состава победителей.\n')

        team_2 = get_prizer(id_tournament, country_contributors, 1)
        team_count = count_champions(team_count, team_2.id, 1)

        if len(team_2.players) > 0:
            for p in team_2.players:
                player = get_player(p['player'])
                name_surname = f"{player.name} {player.surname}"
                player_id_name.update({player.id: name_surname})
                player_count = count_champions(player_count, player.id, 1)
        else:
            t_errors['second'].append(id_tournament)
            f_errors.write(f'- [{name_tournament}](https://rating.chgk.info/tournament/{id_tournament}) '
                           f'— нет состава серебряных призёров.\n')

        team_3 = get_prizer(id_tournament, country_contributors, 2)
        team_count = count_champions(team_count, team_3.id, 2)

        if len(team_3.players) > 0:
            for p in team_3.players:
                player = get_player(p['player'])
                name_surname = f"{player.name} {player.surname}"
                player_id_name.update({player.id: name_surname})
                player_count = count_champions(player_count, player.id, 2)
        else:
            t_errors['third'].append(id_tournament)
            f_errors.write(f'- [{name_tournament}](https://rating.chgk.info/tournament/{id_tournament}) '
                           f'— нет состава бронзовых призёров.\n')

        ff.write(
            f'\nВторое место заняла команда [{team_2.name}'
            f'](https://rating.chgk.info/teams/{team_2.id}) '
            f'({team_2.city}), третье — [{team_3.name}]'
            f'(https://rating.chgk.info/teams/{team_3.id}) ({team_3.city}).\n')
        ff.write(f'\nПолные результаты на [турнирном сайте](https://rating.chgk.info/tournament/{id_tournament}).\n')
        ff.write(f'\n<small>*[{constants.YEARS_LINK_TEXT}](#{constants.YEARS_ANCHOR})*</small>\n')

        f_cap.write(f'- [{name_tournament} ({ey})](#{ey})\n')

        number_champ -= 1

    f_cap.write(f'\n<small>*[Наверх](#atop)*</small>\n')

    # teams hall of fame

    sorted_teams_by_championship = sorted(team_count.values(), key=attrgetter('gold', 'silver', 'bronze', 'sum'),
                                          reverse=True)
    f_count.write(f'\n### {constants.TEAMS_CONTENTS} <a name="{constants.TEAMS_ANCHOR}"></a>\n')
    f_count.write(f'\n<table class="{constants.TABLE_TEAMS_STYLE}">\n<thead>\n<tr>'
                  f'\n<th>Название</th>\n')
    f_count.write(f'<th>Город</th>\n<th class ="{constants.ROW_STYLE}">I</th>\n')
    f_count.write(f'<th class ="{constants.ROW_STYLE}">II</th>\n<th class ="{constants.ROW_STYLE}">III</th>\n')
    f_count.write(f'<th class ="{constants.ROW_STYLE}">∑</th>\n</tr>\n')
    f_count.write('</thead>\n<tbody>\n')

    for team in sorted_teams_by_championship:
        champion_name = id_team_name.get(team.id)
        champion_town = id_town_name.get(id_team_name_id_town.get(team.id))
        f_count.write(f'<tr>\n<td><a href="https://rating.chgk.info/teams/{team.id}">{champion_name}</a></td>\n')
        f_count.write(f'<td>{champion_town}</td>\n<td class ="{constants.ROW_STYLE}">{team.gold}</td>\n')
        f_count.write(f'<td class ="{constants.ROW_STYLE}">{team.silver}</td>\n')
        f_count.write(f'<td class ="{constants.ROW_STYLE}">{team.bronze}</td>\n')
        f_count.write(f'<td class ="{constants.ROW_STYLE}">{team.sum}</td>\n</tr>\n')

    f_count.write(f'</tbody>\n</table>\n')
    f_count.write(f'\n<small>*[Наверх](#atop)*</small>\n')

    # players hall of fame
    sorted_players_by_championship = sorted(player_count.values(),
                                            key=attrgetter('gold', 'silver', 'bronze', 'sum'),
                                            reverse=True)

    f_count.write(f'\n## {constants.PLAYERS_CONTENTS} <a name="{constants.PLAYERS_ANCHOR}"></a>\n')
    f_count.write(f'\n<table class="{constants.TABLE_PLAYERS_STYLE}">\n<thead>\n<tr>'
                  f'\n<th>Имя</th>\n')
    f_count.write(f'<th class ="{constants.ROW_STYLE}">I</th>\n')
    f_count.write(f'<th class ="{constants.ROW_STYLE}">II</th>\n')
    f_count.write(f'<th class ="{constants.ROW_STYLE}">III</th>\n')
    f_count.write(f'<th class ="{constants.ROW_STYLE}">∑</th>\n</tr>\n')
    f_count.write(f'</thead>\n<tbody>\n')

    for player in sorted_players_by_championship:
        name_champion_player = player_id_name.get(player.id)
        f_count.write(f'<tr>\n<td><a href="https://rating.chgk.info/player/{player.id}">'
                      f'{name_champion_player}</a></td>\n')
        f_count.write(f'<td class ="{constants.ROW_STYLE}">{player.gold}</td>\n')
        f_count.write(f'<td class ="{constants.ROW_STYLE}">{player.silver}</td>\n')
        f_count.write(f'<td class ="{constants.ROW_STYLE}">{player.bronze}</td>\n')
        f_count.write(f'<td class ="{constants.ROW_STYLE}">{player.sum}</td>\n</tr>\n')

    f_count.write(f'</tbody>\n</table>')


    ff.close()
    f_cap.close()
    f_count.close()
    f_errors.close()

    make_file(country, country_cyrillic)


def make_file(country, country_cyrillic):
    cap = open(f'{constants.FILE_PATH}{country}_output_cap.txt', 'r')
    count = open(f'{constants.FILE_PATH}{country}_output_count.txt', 'r')
    years = open(f'{constants.FILE_PATH}{country}_output_years.txt', 'r')
    errors = open(f'{constants.FILE_PATH}{country}_errors.txt', 'r')
    result = open(f'{constants.FILE_PATH}{country}_result.txt', 'w')

    result.write(f'{constants.PREAMBLE}\n\n{constants.HALL_OF_FAME_TEXT}{country_cyrillic}{constants.ATOP_TEXT}\n - '
                 f'[{constants.TEAMS_CONTENTS}'
                 f'](#{constants.TEAMS_ANCHOR})\n - [{constants.PLAYERS_CONTENTS}](#{constants.PLAYERS_ANCHOR})\n'
                 f' - [{constants.YEARS_CONTENTS}](#{constants.YEARS_ANCHOR})\n')
    for l in count:
        result.write(l)

    if os.stat(f'{constants.FILE_PATH}{country}_errors.txt').st_size != 0:
        result.write(f'\n\n{constants.PLAYERS_STATS_ERROR}')
        for l in errors:
            result.write(l)

    result.write(f'\n\n<small>*[Наверх](#atop)*</small>\n')

    result.write(f'\n### {constants.YEARS_CONTENTS} <a name="{constants.YEARS_ANCHOR}"></a>\n\n')

    for l in cap:
        result.write(f'{l}')
    for l in years:
        result.write(f'{l}')

    result.close()
    cap.close()
    years.close()
    count.close()
    errors.close()


if __name__ == '__main__':
    parser = create_parser()
    namespace = parser.parse_args(sys.argv[1:])

    if namespace.file:
        filename = namespace.file
    if namespace.cyr:
        country_cyrillic = namespace.cyr
    if namespace.number:
        number = int(namespace.number)
    else:
        number = None
    if namespace.game:
        game = namespace.game
    else:
        game = 'chgk'

    if namespace.test == "on":
        country_cyrillic = "Ирана"
        calculate_from_ids(filename, country_cyrillic, game, number)
    elif game == 'chgk':
        get_chgk_stats_from_id(filename, country_cyrillic, number)
