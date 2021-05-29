from config import POINTS, ALL_TYPES
from model import Games, User, Ranking, Team, engine
from sqlalchemy.orm import Session


_session = Session(bind=engine)


def commit():
    _session.commit()
    _session.close()


def get_session():
    return _session


class UpdatePuntenSpel:

    def __init__(self):
        from poule import Poule
        teams = {}

        for typ in ALL_TYPES:
            poule = Poule(typ)

            for team in poule:
                if team not in teams:
                    teams[team] = poule[team][Poule.GAME_POINTS]
                else:
                    teams[team] += poule[team][Poule.GAME_POINTS]

        for team, punten in teams.items():
            _session.merge(Team(id=_session.query(Team.id).filter(Team.team == team).scalar(), punten=punten))

        _session.commit()


class UpdateScore:

    def __init__(self, game_id):
        self.game_id = game_id

    def update(self, goals_home, goals_away):
        _session.merge(Games(id=self.game_id, stage='home', goals=goals_home))
        _session.merge(Games(id=self.game_id, stage='away', goals=goals_away))
        _session.flush()

        UpdatePuntenSpel()

    def reset(self):
        _session.merge(Games(id=self.game_id, goals_home=None, goals_away=None))
        _session.flush()


class AddNewUser:

    def __init__(self, *, naam, team_naam, leeftijd, email, topscoorder, bonusvraag_gk, bonusvraag_rk, bonusvraag_goals,
                 betaald, rankings):
        user = User(
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
                Ranking(team=_session.query(Team).filter_by(team=team).first(), waarde=points)
                for team, points in zip(rankings, POINTS)
            ]
        )
        _session.add(user)


class AddNewGame:

    def create_game(self, *, id, date, stadium, poule, setting, **kwargs):
        team = kwargs[f'{setting}_team']

        return Games(
            id=id,
            date=date,
            stadium=stadium,
            poule=poule,
            type=Games.get_type(poule),
            stage=setting,
            team_id=(
                _session
                .query(Team.id)
                .filter(Team.team == Team.clean(team))
                .scalar()
            )
        )

    def __init__(self, id, date, stadium, poule, **kwargs):
        kwargs |= {
            'id': id,
            'date': date,
            'poule': poule,
            'stadium': stadium
        }
        _session.add(self.create_game(**kwargs | {'setting': 'home'}))
        _session.add(self.create_game(**kwargs | {'setting': 'away'}))


class AddNewTeam:

    def __init__(self, team):
        _session.add(Team(team=team))
