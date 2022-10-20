from time import process_time
from datetime import date
from Team import Team
from Game import Game
from Player import Player

import sqlite3
from sqlite3 import Error

conn = None


def create_connection(db_file):
    """ create a database connection to a SQLite database """
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)

    return conn


def select_all(conn, table):

    players = ()
    cur = conn.cursor()
    cur.execute("SELECT * FROM " + table)

    rows = cur.fetchall()

    for row in rows:
        if table == "Player":
            players_temp = players + (Player(*row),)
            players = players_temp

    return players


def update_table(conn, table):

    cur = conn.cursor()

    if table == "Player":
        for player in players:
            sql = f''' UPDATE Player
                      SET motm = {player.motm},
                          scored_goals = {player.scored_goals},
                          minutes_played = {player.minutes_played},
                          cards = {player.cards}
                      WHERE number = {player.number}; '''

            cur.execute(sql)

    conn.commit()


if __name__ == '__main__':
    conn = create_connection(r"C:\Users\André\PycharmProjects\TeamProject\SQLite_Python.db")
    players = select_all(conn, "Player")


team_main = Team("ATM")

date_game_list = ("16/09/2022", "15/09/2022", "14/09/2022")

i = 0

for dates in date_game_list:
    game_list = (Game(team_main, "CTF", "0-0", dates),
                 Game(team_main, "RM", "0-0", dates),
                 Game(team_main, "TJI", "0-0", dates))

minutes = 0
count1 = 0.0
count2 = 0.0
end = False
event = False
hg = 0
ag = 0
selected_players = 0
chronometer_start = 0.0
chronometer_end = 0.0
game_started = False
paused_game = False
today = date.today()

for dates in date_game_list:
    if dates == today.strftime("%d/%m/%Y"):
        print("Date of the game: " + dates)
        i = 0

        for player in players:
            print(str(i) + " - " + player.name)
            i += 1

        print("Select 11 players to be the initial team.")
        while selected_players < 11:
            answer_player_name = input()

            found = False
            for player in players:
                if player.name == answer_player_name:
                    found = True
                    selected_players += 1
                    player.bench = False
                    break

            if not found:
                print("ERROR: Invalid player name. Type another name.")
                print()
                break

        for game in game_list:
            if game.date == dates:
                print("Game: " + game.team1 + " vs " + game.team2)
                print("Initial result: " + game.result)

        answer_event = ""
        while not answer_event == "E" or "Quit":
            print("S - Start game")
            print("P - Pause game")
            print("U - Unpause game")
            print("E - End game")
            print("1 - Add a home goal")
            print("2 - Add an away goal")
            print("3 - Add a card")
            print("4 - Add a substitution")
            print("Quit - Close program")
            answer_event = input("Type an event: ")

            match answer_event:
                case "S":
                    if game_started:
                        print("WARNING: Game already started. Add another event.")
                    else:
                        chronometer_start = process_time()
                        game_started = True
                        print("Game started.")

                case "P":
                    if paused_game:
                        print("WARNING: Game already paused. Add another event.")
                    else:
                        chronometer_end = process_time()
                        paused_game = True
                        print("Game paused.")

                case "U":
                    if paused_game:
                        chronometer_start = chronometer_end - chronometer_start
                        paused_game = False
                        print("Game unpaused.")
                    else:
                        print("WARNING: Game in not paused. Add another event.")
                        break

                case "E":
                    if not end:
                        chronometer_end = process_time()
                        end = True

                    print("Total game time: " + str(round((chronometer_end - chronometer_start) // 60)) + "minutes")
                    answer_player_name = input("Type the name for man of the match: ")

                    found = False
                    for player in players:
                        if player.name == answer_player_name:
                            found = True
                            player.motm = 1
                            break

                    if not found:
                        print("ERROR: Invalid player name.")
                        print("Action rolling back. Enter 'E' for End game again.")
                        break

                    '''for player in players:
                        print("Nome: " + player.name + " MOTM: " + str(player.motm) + " Golos marcados: " + str(player.scored_goals) +
                              " Minutos jogados: " + str(player.minutes_played) + " Cartões: " + str(player.cards))'''

                    update_table(conn, "Player")
                    break

                case "1":
                    if not paused_game:
                        hg += 1
                        print("Result: " + str(hg) + "-" + str(ag))
                        answer_player_name = input("Type the name of the player who scored: ")

                        found = False
                        for player in players:
                            if player.name == answer_player_name and not player.bench:
                                found = True
                                player.scored_goals += 1
                                break

                        if not found:
                            print("ERROR: Invalid player name.")
                            print("Action rolling back. Re-enter the goal.")
                            break

                    else:
                        print("WARNING: Game is paused. Add another event.")
                        break

                case "2":
                    if not paused_game:
                        ag += 1
                        print("Result: " + str(hg) + "-" + str(ag))
                    else:
                        print("WARNING: Game is paused. Add another event.")
                        break

                case "3":
                    if not paused_game:
                        answer_player_name = input("Type the name of the player who has been booked: ")

                        found = False
                        for player in players:
                            if player.name == answer_player_name and not player.bench:
                                found = True
                                '''Adding yellows and reds later'''
                                player.cards += 1
                                break

                        if not found:
                            print("ERROR: Invalid player name.")
                            print("Action rolling back. Re-enter the card.")
                            break

                    else:
                        print("WARNING: Game is paused. Add another event.")
                        break

                case "4":
                    if not paused_game:
                        answer_player_field_name = input("Type the name of the player to be benched: ")

                        found = False
                        for player in players:
                            if player.name == answer_player_field_name:
                                found = True
                                if not player.bench:
                                    player_field = player
                                    break
                                else:
                                    print("WARNING: Player is already benched.")
                                    print("Action rolling back. Re-enter substitution.")
                                    break

                        if not found:
                            print("ERROR: Invalid player name.")
                            print("Action rolling back. Re-enter substitution.")
                            break

                        answer_player_bench_name = input("Type the name of the player to join game: ")

                        for player in players:
                            found = False
                            if player.name == answer_player_bench_name:
                                found = True
                                if player.bench:
                                    player_bench = player
                                    break
                                else:
                                    print("WARNING: Player is not benched.")
                                    print("Action rolling back. Re-enter substitution.")
                                    break

                        if not found:
                            print("ERROR: Invalid player name.")
                            print("Action rolling back. Re-enter substitution.")
                            break

                        for player in players:
                            if player.name == player_field.name:
                                chronometer = process_time()
                                player.minutes_played = round((chronometer - chronometer_start) // 60)
                                player.bench = True
                                break

                            elif player.name == player_bench.name:
                                player.bench = False
                                '''Add some minutes played counter'''
                                break
                    else:
                        print("WARNING: Game is paused. Add another event.")
                        break

                case _:
                    print("Inexisting event")
                    break

        break
