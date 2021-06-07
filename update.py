import json
import sys

from sqlalchemy.orm import Session

from config import POINTS, ALL_TYPES
from model import Games, User, Ranking, Team, engine

_session = Session(bind=engine)


class Sessie:
    sessie = _session

    def commit(self):
        _session.commit()
        _session.close()
        return self

    def flush(self):
        _session.flush()
        return self


class UpdatePuntenSpel(Sessie):

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
            self.sessie.merge(Team(id=Query.team_id_by_name(team), punten=punten))


class UpdateUserPoints(Sessie):

    def __init__(self):
        from ranking import UserRanking

        for user in self.sessie.query(User):
            UserRanking(user.id).totaal()


class UpdateScore(Sessie):

    def __init__(self, game_id: int):
        self.game_id = game_id

    def update(self, goals_home: int, goals_away: int):
        self.sessie.merge(Games(id=self.game_id, stage='home', goals=goals_home))
        self.sessie.merge(Games(id=self.game_id, stage='away', goals=goals_away))
        self.flush()

        UpdatePuntenSpel()

    def reset(self):
        self.sessie.merge(Games(id=self.game_id, goals_home=None, goals_away=None))
        self.flush()


class AddNewUsers(Sessie):

    def field_check(self, data, field, required=False):
        if field not in data or not data.get(field):
            if required:
                print(f'WARNING: Required field: `{field}` not in data or empty for user:')
                print(json.dumps(data, sort_keys=False, indent=2))
                sys.exit(1)
            return
        else:
            return data[field]

    def __init__(self, *users: dict):
        self.sessie.add_all(
            User(
                naam=self.field_check(user, 'naam', required=True),
                team_naam=self.field_check(user, 'team_naam'),
                leeftijd=self.field_check(user, 'leeftijd'),
                email=self.field_check(user, 'email'),
                topscoorder=self.field_check(user, 'topscoorder', required=True),
                bonusvraag_gk=self.field_check(user, 'bonusvraag_gk', required=True),
                bonusvraag_rk=self.field_check(user, 'bonusvraag_rk', required=True),
                bonusvraag_goals=self.field_check(user, 'bonusvraag_goals', required=True),
                betaald=user['betaald'],
                rankings=[
                    Ranking(team=Query.team_obj_by_name(team), waarde=points)
                    for team, points in zip(user['rankings'], POINTS)
                ]
            ) for user in users
        )


class AddNewGames(Sessie):

    def create_game(self, *, id, date, stadium, poule, setting, **kwargs) -> Games:
        team = kwargs.get(f'{setting}_team')
        goals = kwargs.get(f'{setting}_goals')

        return Games(
            id=id,
            date=date,
            stadium=stadium,
            poule=poule,
            type=Games.get_type(poule),
            stage=setting,
            team_id=Query.team_id_by_name(team),
            goals=goals
        )

    def __init__(self, *games: dict):
        for game in games:
            assert isinstance(game, dict)
            game['id'] = game.pop('Index')

            self.sessie.add(self.create_game(**game | {'setting': 'home'}))
            self.sessie.add(self.create_game(**game | {'setting': 'away'}))


class AddNewTeams(Sessie):

    def __init__(self, *teams: str):
        self.sessie.add_all(Team(team=team, team_finals=Team.get_final_team(team)) for team in teams)


class Query(Sessie):

    @classmethod
    def games_from_poule(cls, poule: str, stage: str = None) -> list:
        filter_by = [Games.poule == poule]

        if stage:
            filter_by += [Games.stage == stage]

        return (
            cls.sessie
            .query(Games.id, Games.poule, Team.team, Games.goals)
            .join(Team)
            .filter(*filter_by)
            .order_by(Games.id)
            .all()
        )

    @classmethod
    def team_id_by_name(cls, team: str) -> int:
        return cls.sessie.query(Team.id).filter(Team.team == Team.clean(team)).scalar()

    @classmethod
    def team_obj_by_name(cls, team: str) -> Team:
        return cls.sessie.query(Team).filter(Team.team == Team.clean(team)).first()
