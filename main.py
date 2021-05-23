from random import shuffle

from config import TEAMS
from update import UpdateScore, AddNewUser
from poule import Poule
from upload import *
from model import *

if __name__ == '__main__':
    # print(has_table(Team))

    UploadTeams(recreate=True).upload()
    UploadGames(recreate=True).upload()
    # generate_ranking()


    # UpdateScore(game_id=1).update(0, 3)

    # Poule("A")
    # recreate_table(User)
    # recreate_table(Ranking)

    # teams = [idx for idx, _ in enumerate(TEAMS, start=0)]
    teams = list(TEAMS)
    shuffle(teams)

    AddNewUser(
        naam='Naam',
        team_naam='Naam vh team',
        leeftijd=42,
        email='mail@mail.nl',
        topscoorder='Ryan Babel',
        bonusvraag_gk='80',
        bonusvraag_rk=8,
        bonusvraag_goals=121,
        betaald=False,
        rankings=teams
    )
