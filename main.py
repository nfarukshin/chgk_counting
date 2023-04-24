import requests
from datetime import datetime
from roman_arabic_numerals import conv

id_team_name = {}
id_town_name = {}
id_team_name_id_town = {}

def count_champions(champions_counting_list, id):
    champion_count = champions_counting_list.get(id)
    if champion_count is not None:
        champions_counting_list[id] = champion_count + 1
    else:
        champions_counting_list.update({id: 1})

    return champions_counting_list


def get_prizer(id_tournament, list_tournament, place):
    try:
        team = list_tournament[place]
    except:
        print(f"Problems with choice team № {place} in tournament id={id_tournament}")

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


def transform_file2list(file):
    file = open(file, 'r', encoding='utf-8')
    lines = file.readlines()
    lines = [line.rstrip('\n') for line in lines]

    file.close()

    return lines


def main():
    country = "polska"
    country_cyrillic = "Польши"

    f = transform_file2list(f'{country}_input.txt')
    number_champ = len(f)
    ff = open(f'{country}_output.txt', 'w')
    f_cap = open(f'{country}_output_cap.txt', 'w')
    f_count = open(f'{country}_output_count.txt', 'w')
    team_count = {}
    player_count = {}
    player_id_name = {}

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

        city_tournament = id_town_name.get(city_id)

        if city_tournament is None:
            try:
                url_town = f'https://api.rating.chgk.net/towns/{city_id}.json'
                t = requests.get(url_town)
                object_city = t.json()
                city_tournament = object_city['name']
            except:
                print(f'Problems with url_town={city_id}')

        # making date start and date end

        start = datetime.strptime(date_start[:10], "%Y-%m-%d")
        end = datetime.strptime(date_end[:10], "%Y-%m-%d")

        sy = start.year
        sm = start.month
        sd = start.day
        ey = end.year
        em = end.month
        ed = end.day

        if sm == 1:
            sm = "января"
        elif sm == 2:
            sm = "февраля"
        elif sm == 3:
            sm = "марта"
        elif sm == 4:
            sm = "апреля"
        elif sm == 5:
            sm = "мая"
        elif sm == 6:
            sm = "июня"
        elif sm == 7:
            sm = "июля"
        elif sm == 8:
            sm = "августа"
        elif sm == 9:
            sm = "сентября"
        elif sm == 10:
            sm = "октября"
        elif sm == 11:
            sm = "ноября"
        elif sm == 12:
            sm = "декабря"

        if em == 1:
            em = "января"
        elif em == 2:
            em = "февраля"
        elif em == 3:
            em = "марта"
        elif em == 4:
            em = "апреля"
        elif em == 5:
            em = "мая"
        elif em == 6:
            em = "июня"
        elif em == 7:
            em = "июля"
        elif em == 8:
            em = "августа"
        elif em == 9:
            em = "сентября"
        elif em == 10:
            em = "октября"
        elif em == 11:
            em = "ноября"
        elif em == 12:
            em = "декабря"

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

        name_tournament = f'{conv.arab_rom(number_champ)} чемпионат {country_cyrillic}'

        team_1 = get_prizer(id_tournament, country_contributors, 0)
        name_team_1 = get_prizer_name(team_1)
        town_team_1 = get_prizer_town(team_1)
        id_team_1 = get_prizer_id(team_1)
        team_count = count_champions(team_count, id_team_1)
        players = team_1['teamMembers']

        ff.write(f'\n**{name_tournament}** прошёл {tournament_date} в {city_tournament}е. <a name="{ey}"></a>\n')
        ff.write(f"Победитель: **[{name_team_1} ({town_team_1})](https://rating.chgk.info/team/{id_team_1})**\n")
        for p in players:
            id_player = p['player']['id']
            name = p['player']['name']
            surname = p['player']['surname']
            name_surname = f"{name} {surname}"
            player_id_name.update({id_player: name_surname})
            player_count = count_champions(player_count, id_player)

            ff.write(f'- {name_surname}\n')

        team_2 = get_prizer(id_tournament, country_contributors, 1)
        team_3 = get_prizer(id_tournament, country_contributors, 2)
        ff.write(
            f'\nВторое место заняла команда [{get_prizer_name(team_2)}'
            f'](https://rating.chgk.info/team/{get_prizer_id(team_2)}) '
            f'({get_prizer_town(team_2)}), третье — [{get_prizer_name(team_3)}]'
            f'(https://rating.chgk.info/team/{get_prizer_id(team_3)}) ({get_prizer_town(team_3)}).\n')
        ff.write(f'\nПолные результаты на [турнирном сайте](https://rating.chgk.info/tournament/{id_tournament}).\n')
        ff.write(f'\n<small>*[Наверх](#atop)*</small>\n')

        f_cap.write(f'- [{name_tournament} ({ey})](#{ey})\n')

        number_champ = number_champ - 1

    sorted_teams_by_championship = sorted(team_count.items(), key=lambda x: x[1], reverse=True)
    converted_teams = dict(sorted_teams_by_championship)

    sorted_players_by_championship = sorted(player_count.items(), key=lambda x: x[1], reverse=True)
    converted_players = dict(sorted_players_by_championship)

    # teams hall of fame

    f_count.write(f"## Зал славы чемпионата {country_cyrillic}\n")
    f_count.write(f'\n### Команды <a name="teams"></a>\n')
    f_count.write(f'\n<table class="uk-table uk-table-divider uk-table-hover">\n<thead>\n<tr>\n<th>Команда</th>\n')
    f_count.write(f'<th>Город</th>\n<th>Победы</th>\n</tr>\n</thead>\n<tbody>\n')

    for key, value in converted_teams.items():
        champion_name = id_team_name.get(key)
        champion_town = id_town_name.get(id_team_name_id_town.get(key))
        f_count.write(f'<tr>\n<th><a href="https://rating.chgk.info/teams/{key}">{champion_name}</a></th>\n')
        f_count.write(f'<th>{champion_town}</th>\n<th>{value}</th>\n</tr>\n')

    f_count.write(f'</tbody>\n</table>\n')
    f_count.write(f'\n<small>*[Наверх](#atop)*</small>\n')

    # players hall of fame

    f_count.write(f'\n## Игроки <a name="players"></a>\n')
    f_count.write(f'\n<table class="uk-table uk-table-divider uk-table-hover">\n<thead>\n<tr>\n<th>Игрок</th>\n')
    f_count.write(f'<th>Победы</th>\n</tr>\n</thead>\n<tbody>\n')

    for key, value in converted_players.items():
        name_champion_player = player_id_name.get(key)
        f_count.write(f'<tr>\n<th><a href="https://rating.chgk.info/player/{key}">{name_champion_player}</a></th>\n')
        f_count.write(f'<th>{value}</th>\n</tr>\n')

    f_count.write(f'</tbody>\n</table>\n')
    f_count.write(f'\n<small>*[Наверх](#atop)*</small>\n')

    ff.close()
    f_cap.close()
    f_count.close()


if __name__ == '__main__':
    main()
