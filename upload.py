from abc import abstractmethod
from pathlib import Path
from random import shuffle

import pandas as pd

from config import SOURCE_FILE, SHEET_PROGRAMMA, POINTS, TEAMS, USER_FOLDER
from update import AddNewUser, AddNewGame, AddNewTeam, commit as commit_all
from model import Team, Games, Ranking, User, recreate_table, has_table


def drop_empty(data):
    return data.dropna(how='all', axis=0).dropna(how='all', axis=1)


def drop_col_only_containing(data, char):
    for col in data.columns:
        if data[col].eq(char).all():
            del data[col]
    return data


def read() -> pd.DataFrame:
    data = pd.read_excel(SOURCE_FILE, sheet_name=SHEET_PROGRAMMA, header=1, dtype=str, engine='xlrd')
    data = drop_col_only_containing(drop_empty(data), '-')
    data.columns = ['fase', 'datum', 'tijd', 'poule', 'home_team', 'away_team', 'stadium']
    return data


def generate_ranking():
    teams = list(TEAMS)
    shuffle(teams)

    assert len(teams) == len(POINTS)
    return [Ranking(team=Team(team=team), waarde=point) for team, point in zip(teams, POINTS)]


class UploadBase:

    @property
    @abstractmethod
    def base(self):
        pass

    @property
    @abstractmethod
    def depends_on(self):
        pass

    def __init__(self, recreate: bool = False):
        if self.depends_on:
            for obj in self.depends_on:
                if not has_table(obj.base):
                    raise ValueError(f"Table not present: {str(obj)}")

        if recreate:
            recreate_table(self.base)

    @abstractmethod
    def upload(self):
        pass

    @staticmethod
    def commit():
        commit_all()


class UploadTeams(UploadBase):
    base = Team
    depends_on = []

    def __init__(self, recreate: bool = False):
        super().__init__(recreate)
        self.data = read()

    def find_teams(self):
        return sorted(set(self.data['home_team']) | set(self.data['away_team']))

    def upload(self):
        teams = self.find_teams()

        for team in teams:
            AddNewTeam(team)

        return self


class UploadGames(UploadBase):
    depends_on = [UploadTeams]
    base = Games

    def __init__(self, recreate: bool = False):
        super().__init__(recreate)
        self.data = read()
        self._add_datum_tijd()

    def _add_datum_tijd(self):
        df = self.data
        df['date'] = df['datum'].str.rstrip('00:00:00') + df['tijd']
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d %H:%M:%S')

    def upload(self):
        for row_ in self.data.itertuples(index=True):
            kwargs = row_._asdict()
            kwargs['id'] = kwargs.pop('Index')
            AddNewGame(**kwargs)

        return self


class UploadUsers(UploadBase):

    base = User
    depends_on = [UploadTeams, UploadGames]

    ENGINE = 'openpyxl'

    def get_bonus(self, file) -> dict:
        key_map = {
            'Aantal gele kaarten': 'bonusvraag_gk',
            'Aantal rode kaarten': 'bonusvraag_rk',
            'Aantal doelpunten': 'bonusvraag_goals',
            'Topscoorder EK2021': 'topscoorder'
        }
        return (
            pd.read_excel(file, usecols='F:G', skiprows=1, engine=self.ENGINE, dtype=str)
            .dropna(axis=0, how='all')
            .set_index('Bonusvragen')
            .rename(index=key_map)
            .squeeze()
            .map(str.strip)
            .to_dict()
        )

    def get_user(self, file) -> dict:
        key_map = {
            'Naam': 'naam',
            'Teamnaam': 'team_naam',
            'Leeftijd': 'leeftijd',
            'Email': 'email',
            'Betaald': 'betaald'
        }

        return (
            pd.read_excel(file, usecols='I:J', skiprows=1, index_col=0, engine=self.ENGINE, dtype=str)
            .dropna(axis=0, how='all')
            .squeeze()
            .map(str.strip)
            .rename(index=key_map)
            .to_dict()
        )

    def get_ranking(self, file) -> list:
        values = pd.read_excel(file, skiprows=1, usecols='C', squeeze=True, engine=self.ENGINE, dtype=str).to_list()
        return [Team.clean(val) for val in values]

    def read(self):
        for file in Path(USER_FOLDER).glob('*.xlsx'):
            yield {'rankings': self.get_ranking(file)} | self.get_bonus(file) | self.get_user(file)

    def upload(self):
        for data in self.read():
            AddNewUser(**data)

        return self
