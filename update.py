from config import POINTS, get_punten_spel, get_points, ALL_TYPES
from session import Session
from model import Games, User, Ranking, Team
from poule import Poule


class UpdatePuntenSpel:

    def __init__(self):
        teams = {}

        with Session() as session:
            for typ in ALL_TYPES:
                poule = Poule(typ)

                for team in poule:
                    if team not in teams:
                        teams[team] = poule[team][Poule.GAME_POINTS]
                    else:
                        teams[team] += poule[team][Poule.GAME_POINTS]

            for team, punten in teams.items():
                session.merge(Team(id=session.query(Team.id).filter(Team.team == team).scalar(), punten=punten))


class UpdateScore:

    def __init__(self, game_id):
        self.game_id = game_id

    def update(self, goals_home, goals_away):
        with Session() as session:
            session.merge(Games(id=self.game_id, stage='home', goals=goals_home))
            session.merge(Games(id=self.game_id, stage='away', goals=goals_away))

        UpdatePuntenSpel()

    def reset(self):
        with Session() as conn:
            conn.merge(Games(id=self.game_id, goals_home=None, goals_away=None))


class AddNewUser:

    def build_ranking_objs(self, conn, team_list):
        return

    def __init__(self, naam, team_naam, leeftijd, email, topscoorder, bonusvraag_gk, bonusvraag_rk, bonusvraag_goals,
            betaald, rankings):
        with Session() as session:
            session.add(
                User(
                    naam=naam,
                    team_naam=team_naam,
                    leeftijd=leeftijd,
                    email=email,
                    topscoorder=topscoorder,
                    bonusvraag_gk=bonusvraag_gk,
                    bonusvraag_rk=bonusvraag_rk,
                    bonusvraag_goals=bonusvraag_goals,
                    betaald=betaald,
                    rankings=[
                        Ranking(team=session.query(Team).filter_by(team=team).first(), waarde=points)
                        for team, points in zip(rankings, POINTS)
                    ]
                ))
