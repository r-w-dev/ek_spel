import pandas as pd

from config import WINST, GELIJK, VERLIES, get_points, get_punten_spel, ALL_TYPES
from flask_model import Team
from update import Query


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

    @property
    def empty(self):
        return not any(key for key, values in self.data.items() if values[self.PLAYED] > 0)

    def __getitem__(self, item):
        return self.data.get(item, None)

    def __iter__(self):
        yield from self.data

    def __init__(self, poule):
        if poule not in ALL_TYPES:
            raise ValueError(f"Poule onbekend: {poule}")

        self.data = {}
        self.poule_id = poule

        home_games = Query.games_from_poule(self.poule_id, stage='home')
        away_games = Query.games_from_poule(self.poule_id, stage='away')

        for home, away in zip(home_games, away_games):
            if home.team not in self.data:
                self.new_team(home.team)
            if away.team not in self.data:
                self.new_team(away.team)

            self.add_values(home.team, home.goals, away.goals)
            self.add_values(away.team, away.goals, home.goals)

    def add_values(self, team, goals_made, goals_had):
        cur_points = get_points(goals_made, goals_had)
        cur_team = self.data[team]

        cur_team[self.PLAYED] += 1 if goals_made is not None else 0
        cur_team[self.POINTS] += cur_points or 0
        cur_team[self.WON] += cur_points == WINST
        cur_team[self.DRAW] += cur_points == GELIJK
        cur_team[self.LOST] += cur_points == VERLIES
        cur_team[self.GOALS_MADE] += goals_made or 0
        cur_team[self.GOALS_HAD] += goals_had or 0
        cur_team[self.GOALS_SALDO] = self.saldo(team)
        cur_team[self.GAME_POINTS] += get_punten_spel(cur_points, goals_made)

    def saldo(self, team):
        return self.data[team][self.GOALS_MADE] - self.data[team][self.GOALS_HAD]

    def to_dataframe(self) -> pd.DataFrame:
        from pandas import DataFrame

        data = {Team.get_final_team(key): val for key, val in self.data.items()}

        df: DataFrame = (
            DataFrame
            .from_dict(data, columns=self.COLUMNS, orient='index')
            .rename_axis(f'Groep {self.poule_id}')
        )

        # sorting not correct: needs 'onderling resultaat'
        return df.sort_index(ascending=True) if self.empty else \
            df.sort_values(
                by=[self.POINTS, self.GOALS_SALDO, self.PLAYED, self.GAME_POINTS],
                ascending=[False, False, True, False]
            )


class PouleDatabase:

    def __init__(self):
        self.poules = []

    def add(self, poule: Poule):
        self.poules.append(poule)
        return self

    def add_all(self):
        for poule in ALL_TYPES:
            self.add(Poule(poule))
        return self

    def print(self):
        print()
        for poule in self.poules:
            print(poule.to_dataframe().to_markdown(), end='\n\n\n')

    def to_html(self, **kwargs):
        return "<br /></br />".join(poule.to_dataframe().to_html(**kwargs) for poule in self.poules)
