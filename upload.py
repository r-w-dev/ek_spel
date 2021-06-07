from abc import abstractmethod
from pathlib import Path
from random import shuffle

import pandas as pd

from config import SOURCE_FILE, SHEET_PROGRAMMA, POINTS, TEAMS, USER_FOLDER
from model import Team, Games, Ranking, User, recreate_table, has_table
from update import AddNewTeams, AddNewGames, AddNewUsers


def drop_empty(data):
    return data.dropna(how='all', axis=0)


def drop_col_only_containing(data, char):
    for col in data.columns:
        if data[col].eq(char).all():
            del data[col]
    return data


def read() -> pd.DataFrame:
    data = pd.read_excel(SOURCE_FILE, sheet_name=SHEET_PROGRAMMA, header=1, dtype=str, usecols='A:K', engine='xlrd')
    data = drop_col_only_containing(drop_empty(data), '-')
    data.columns = ['fase', 'datum', 'tijd', 'poule', 'home_team', 'away_team', 'stadium', 'home_goals', 'away_goals']
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


class UploadTeams(UploadBase):
    base = Team
    depends_on = []

    def __init__(self, recreate: bool = False):
        super().__init__(recreate)
        self.data = read()

    def find_teams(self):
        return sorted(set(self.data['home_team']) | set(self.data['away_team']))

    def upload(self):
        AddNewTeams(*self.find_teams()).commit()
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
        AddNewGames(*(row._asdict() for row in self.data.itertuples(index=True))).commit()
        return self


class UploadUsers(UploadBase):

    base = User
    depends_on = [UploadTeams, UploadGames]

    ENGINE = 'openpyxl'
    GLOB = '*.xlsx'

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
            .map(str.strip, na_action='ignore')
            .fillna('')
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
            pd.read_excel(file, usecols='I:J', skiprows=1, engine=self.ENGINE, dtype=str)
            .dropna(axis=0, how='all')
            .set_index('Gebruiker')
            .squeeze()
            .map(str.strip, na_action='ignore')
            .rename(index=key_map)
            .fillna('')
            .to_dict()
        )

    def get_ranking(self, file) -> list:
        values = pd.read_excel(file, skiprows=1, usecols='C', squeeze=True, engine=self.ENGINE, dtype=str).to_list()
        return [Team.clean(val) for val in values]

    def read(self):
        for file in Path(USER_FOLDER).glob(self.GLOB):
            yield {'rankings': self.get_ranking(file)} | self.get_bonus(file) | self.get_user(file)

    def upload(self):
        AddNewUsers(*self.read()).commit()
        return self
