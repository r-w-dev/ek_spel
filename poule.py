from config import WINST, GELIJK, VERLIES, get_points, get_punten_spel, ALL_TYPES, POULES
from model import Games, Team
from update import get_session


class Poule:

    TEAM = 'Team'
    PLAYED = 'Gespeeld'
    POINTS = 'Punten'
    WON = 'Winst'
    DRAW = 'Gelijk'
    LOST = 'Verlies'
    GOALS_MADE = 'Voor'
    GOALS_HAD = 'Tegen'
    GOALS_SALDO = 'Saldo'
    GAME_POINTS = 'Punten spel'

    INDEX = TEAM
    COLUMNS = PLAYED, POINTS, WON, DRAW, LOST, GOALS_MADE, GOALS_HAD, GOALS_SALDO, GAME_POINTS

    def new_team(self, team):
        self.data[team] = {key: 0 for key in self.COLUMNS}

    def __getitem__(self, item):
        return self.data.get(item, None)

    def __iter__(self):
        yield from self.data

    def __init__(self, poule):
        if poule not in ALL_TYPES:
            raise ValueError(f"Poule onbekend: {poule}")

        self.data = {}
        self.poule_id = poule
        session = get_session()

        poule = (
            session
            .query(Games.id, Games.poule, Team.team, Games.goals)
            .join(Team)
            .filter(Games.poule == poule)
            .order_by(Games.id)
        )

        home_games = poule.filter(Games.stage == 'home').all()
        away_games = poule.filter(Games.stage == 'away').all()

        for home, away in zip(home_games, away_games):
            if home.team not in self.data:
                self.new_team(home.team)
            if away.team not in self.data:
                self.new_team(away.team)

            self.add_values(home.team, home.goals, away.goals)
            self.add_values(away.team, away.goals, home.goals)

        session.flush()

    def add_values(self, team, goals_home, goals_away):
        cur_points = get_points(goals_home, goals_away)
        cur_team = self.data[team]

        cur_team[self.PLAYED] += 1 if goals_home is not None else 0
        cur_team[self.POINTS] += cur_points or 0
        cur_team[self.WON] += cur_points == WINST
        cur_team[self.DRAW] += cur_points == GELIJK
        cur_team[self.LOST] += cur_points == VERLIES
        cur_team[self.GOALS_MADE] += goals_home or 0
        cur_team[self.GOALS_HAD] += goals_away or 0
        cur_team[self.GOALS_SALDO] = self.saldo(team)
        cur_team[self.GAME_POINTS] += get_punten_spel(cur_points, goals_home)

    def saldo(self, team):
        return self.data[team][self.GOALS_MADE] - self.data[team][self.GOALS_HAD]

    def to_dataframe(self):
        from pandas import DataFrame
        return (
            DataFrame
            .from_dict(self.data, columns=self.COLUMNS, orient='index')
            .rename_axis(f'Groep {self.poule_id}')
            .sort_values([self.POINTS, self.GOALS_SALDO], ascending=False)
        )


class PouleDatabase:

    def __init__(self):
        self.poules = []

    def add(self, poule: Poule):
        self.poules.append(poule)
        return self

    def add_all(self):
        for poule in POULES:
            self.add(Poule(poule))
        return self

    def print(self):
        print()
        for poule in sorted(self.poules, key=lambda x: x.poule_id):
            print(poule.to_dataframe().to_markdown(), end='\n\n\n')
