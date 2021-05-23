from abc import abstractmethod
from random import shuffle

import pandas as pd

from config import SOURCE_FILE, SHEET_PROGRAMMA, POINTS, TEAMS
from session import Session
from model import Team, Games, Ranking, recreate_table, has_table


def drop_empty(data):
    return data.dropna(how='all', axis=0).dropna(how='all', axis=1)


def drop_col_only_containing(data, char):
    for col in data.columns:
        if data[col].eq(char).all():
            del data[col]
    return data


def read() -> pd.DataFrame:
    data = pd.read_excel(SOURCE_FILE, sheet_name=SHEET_PROGRAMMA, header=1, dtype=str)
    data = drop_col_only_containing(drop_empty(data), '-')
    data.columns = ['fase', 'datum', 'tijd', 'poule', 'home_team', 'away_team', 'stadium']
    return data


def generate_ranking():
    teams = list(TEAMS)
    shuffle(teams)

    assert len(teams) == len(POINTS)
    return [
        Ranking(team=Team(team=team), waarde=point)
        for team, point in zip(teams, POINTS)
    ]


class UploadBase:

    @property
    @abstractmethod
    def base(self):
        pass

    @property
    @abstractmethod
    def depends_on(self):
        pass

    def __init__(self, truncate: bool = False, recreate: bool = False):
        if self.depends_on:
            for obj in self.depends_on:
                if not has_table(obj.base):
                    raise ValueError(f"Table not present: {str(obj)}")

        if recreate:
            recreate_table(self.base)
        elif truncate:
            with Session() as conn:
                conn.truncate(self.base)

    @abstractmethod
    def upload(self):
        pass


class UploadTeams(UploadBase):
    base = Team
    depends_on = []

    def __init__(self, truncate: bool = False, recreate: bool = False):
        super().__init__(truncate, recreate)
        self.data = read()

    def find_teams(self):
        return sorted(set(self.data['home_team']) | set(self.data['away_team']))

    def upload(self):
        teams = self.find_teams()

        with Session() as conn:
            conn.add(Team(team=team) for team in teams)


class UploadGames(UploadBase):
    depends_on = [UploadTeams]
    base = Games

    def __init__(self, truncate: bool = False, recreate: bool = False):
        super().__init__(truncate, recreate)
        self.data = read()
        self._add_datum_tijd()

    def _add_datum_tijd(self):
        df = self.data
        df['date'] = df['datum'].str.rstrip('00:00:00') + df['tijd']
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d %H:%M:%S')

    def upload(self):
        def create_game(row, setting):
            team = getattr(row, f'{setting}_team')
            return Games(
                id=row.Index,
                date=row.date,
                stadium=row.stadium,
                poule=row.poule,
                type=Games.get_type(row.poule),
                team_id=(
                    conn
                    .query(Team.id)
                    .filter(Team.team == Team.clean(team))
                    .scalar()
                ),
                stage=setting
            )

        with Session() as conn:
            for row in self.data.itertuples(index=True):
                conn.add(create_game(row, 'home'))
                conn.add(create_game(row, 'away'))
