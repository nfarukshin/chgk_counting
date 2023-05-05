import requests
from tournament_date import get_tournament_date, get_year_print
from roman_arabic_numerals import conv
import sys
import argparse
from operator import attrgetter


id_team_name = {}
id_town_name = {}
id_team_name_id_town = {}


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file')
    parser.add_argument('-c', '--cyr')

    return parser


class Awardee:
    def __init__(self, id):
        self.id = id
        self.sum = 0
        self.gold = 0
        self.silver = 0
        self.bronze = 0


class Team:
    def __init__(self, id, name, city, players):
        self.id = id
        self.name = name
        self.city = city
        self.players = players


class Player:
    def __init__(self, id, name, surname):
        self.id = id
        self.name = name
        self.surname = surname


def count_champions(awardees_counting_dict, id, place):
    awardee = awardees_counting_dict.get(id)
    if awardee is None:
        awardee = Awardee(id)

    if place == 1:
        awardee.gold += 1
    elif place == 2:
        awardee.silver += 1
    elif place == 3:
        awardee.bronze += 1
    else:
        print(f"Error with place={place} from awardee with id={id}")
    awardee.sum += 1
    awardees_counting_dict[id] = awardee

    return awardees_counting_dict


def get_player(raw_player):
    id_player = raw_player['player']['id']
    name_player = raw_player['player']['name']
    surname_player = raw_player['player']['surname']
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
    players = raw_team['teamMembers']
    team = Team(team_id, team_name, team_city, players)

    return team


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

    try:
        list_t = r.json()
    except:
        print(f"json doesn't work with id={id_tournament}")

    # check championship flags

    for l in list_t:
        flags = l['flags']
        if len(flags) > 0:
            flag = flags[0]['id']
            if flag == 50:
                country_contributors.append(l)
    if len(country_contributors) == 0:
        country_contributors = list_t

    return country_contributors


def transform_file2list(file):
    file = open(file, 'r', encoding='utf-8')
    lines = file.readlines()
    lines = [line.rstrip('\n') for line in lines]

    file.close()

    return lines


def get_stats(filename, country_cyrillic):
    f = transform_file2list(filename)
    country = filename[:-4]
    number_champ = len(f)
    ff = open(f'{country}_output.txt', 'w')
    f_cap = open(f'{country}_output_cap.txt', 'w')
    f_count = open(f'{country}_output_count.txt', 'w')
    team_count = dict()
    player_count = dict()
    player_id_name = dict()

    for id_tournament in f:
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

        city_tournament = get_city_tournament(city_id)
        tournament_date = get_tournament_date(date_start, date_end)
        ey = get_year_print(date_end)
        country_contributors = get_country_contributors(id_tournament)

        name_tournament = f'{conv.arab_rom(number_champ)} чемпионат {country_cyrillic}'

        team_1 = get_prizer(id_tournament, country_contributors, 0)
        team_count = count_champions(team_count, team_1.id, 1)

        ff.write(f'\n**{name_tournament}** прошёл {tournament_date} в {city_tournament}е. <a name="{ey}"></a>\n')
        ff.write(f"Победитель: **[{team_1.name} ({team_1.city})](https://rating.chgk.info/team/{team_1.id})**\n")
        for p in team_1.players:
            player = get_player(p)
            name_surname = f"{player.name} {player.surname}"
            player_id_name.update({player.id: name_surname})
            player_count = count_champions(player_count, player.id, 1)

            ff.write(f'- {name_surname}\n')

        team_2 = get_prizer(id_tournament, country_contributors, 1)
        team_count = count_champions(team_count, team_2.id, 2)
        for p in team_2.players:
            player = get_player(p)
            name_surname = f"{player.name} {player.surname}"
            player_id_name.update({player.id: name_surname})
            player_count = count_champions(player_count, player.id, 2)

        team_3 = get_prizer(id_tournament, country_contributors, 2)
        team_count = count_champions(team_count, team_3.id, 3)
        for p in team_3.players:
            player = get_player(p)
            name_surname = f"{player.name} {player.surname}"
            player_id_name.update({player.id: name_surname})
            player_count = count_champions(player_count, player.id, 3)

        ff.write(
            f'\nВторое место заняла команда [{team_2.name}'
            f'](https://rating.chgk.info/team/{team_2.id}) '
            f'({team_2.city}), третье — [{team_3.name}]'
            f'(https://rating.chgk.info/team/{team_3.id}) ({team_3.city}).\n')
        ff.write(f'\nПолные результаты на [турнирном сайте](https://rating.chgk.info/tournament/{id_tournament}).\n')
        ff.write(f'\n<small>*[К списку чемпионатов](#years)*</small>\n')

        f_cap.write(f'- [{name_tournament} ({ey})](#{ey})\n')

        number_champ = number_champ - 1

    f_cap.write(f'\n<small>*[Наверх](#atop)*</small>\n')

    sorted_teams_by_championship = sorted(team_count.values(), key=attrgetter('sum', 'gold', 'silver', 'bronze'),
                                          reverse=True)
    # converted_teams = dict(sorted_teams_by_championship)

    sorted_players_by_championship = sorted(player_count.values(), key=attrgetter('sum', 'gold', 'silver', 'bronze'),
                                           reverse=True)
    # converted_players = dict(sorted_players_by_championship)

    # teams hall of fame

    f_count.write(f"## Зал славы чемпионата {country_cyrillic}\n")
    f_count.write(f'\n### Команды <a name="teams"></a>\n')
    f_count.write(f'\n<table class="uk-table uk-table-divider uk-table-hover uk-width-1-2">\n<thead>\n<tr>'
                  f'\n<th>Название</th>\n')
    f_count.write(f'<th>Город</th>\n<th class ="uk-text-center">∑</th>\n')
    f_count.write(f'<th class ="uk-text-center">I</th>\n<th class ="uk-text-center">II</th>\n')
    f_count.write(f'<th class ="uk-text-center">III</th>\n</tr>\n')
    f_count.write('</thead>\n<tbody>\n')

    for team in sorted_teams_by_championship:
        champion_name = id_team_name.get(team.id)
        champion_town = id_town_name.get(id_team_name_id_town.get(team.id))
        f_count.write(f'<tr>\n<td><a href="https://rating.chgk.info/teams/{team.id}">{champion_name}</a></td>\n')
        f_count.write(f'<td>{champion_town}</td>\n<td class ="uk-text-center">{team.sum}</td>\n')
        f_count.write(f'<td class ="uk-text-center">{team.gold}</td>\n')
        f_count.write(f'<td class ="uk-text-center">{team.silver}</td>\n')
        f_count.write(f'<td class ="uk-text-center">{team.bronze}</td>\n</tr>\n')

    f_count.write(f'</tbody>\n</table>\n')
    f_count.write(f'\n<small>*[Наверх](#atop)*</small>\n')

    # players hall of fame

    f_count.write(f'\n## Игроки <a name="players"></a>\n')
    f_count.write(f'\n<table class="uk-table uk-table-divider uk-table-hover uk-width-1-2">\n<thead>\n<tr>'
                  f'\n<th>Имя</th>\n')
    f_count.write(f'<th class ="uk-text-center">∑</th>\n')
    f_count.write(f'<th class ="uk-text-center">I</th>\n')
    f_count.write(f'<th class ="uk-text-center">II</th>\n')
    f_count.write(f'<th class ="uk-text-center">III</th>\n</tr>\n')
    f_count.write(f'</thead>\n<tbody>\n')

    for player in sorted_players_by_championship:
        name_champion_player = player_id_name.get(player.id)
        f_count.write(f'<tr>\n<td><a href="https://rating.chgk.info/player/{player.id}">'
                      f'{name_champion_player}</a></td>\n')
        f_count.write(f'<td class ="uk-text-center">{player.sum}</td>\n')
        f_count.write(f'<td class ="uk-text-center">{player.gold}</td>\n')
        f_count.write(f'<td class ="uk-text-center">{player.silver}</td>\n')
        f_count.write(f'<td class ="uk-text-center">{player.bronze}</td>\n</tr>\n')

    f_count.write(f'</tbody>\n</table>\n')
    f_count.write(f'\n<small>*[Наверх](#atop)*</small>\n')

    ff.close()
    f_cap.close()
    f_count.close()


if __name__ == '__main__':
    parser = create_parser()
    namespace = parser.parse_args(sys.argv[1:])

    if namespace.file:
        filename = namespace.file
    if namespace.cyr:
        country_cyrillic = namespace.cyr

    get_stats(filename, country_cyrillic)
