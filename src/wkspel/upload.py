import json
from abc import abstractmethod
from pathlib import Path
from random import shuffle

import pandas as pd

from wkspel.config import config
from wkspel.excel import ExcelParser
from wkspel.model import Team, Games, Ranking, User, recreate_table, has_table
from wkspel.update import AddNewTeams, AddNewGames, AddNewUsers, UpdateScores


def generate_ranking():
    teams = list(config.TEAMS)
    shuffle(teams)

    assert len(teams) == len(config.POINTS)
    return [Ranking(team=Team(team=team), waarde=point) for team, point in zip(teams, config.POINTS)]


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

        assert has_table(self.base), f"Table '{self.base.__table__}' not present"
        self.data = None

    @abstractmethod
    def upload(self):
        raise NotImplementedError


class UploadTeams(UploadBase):
    base = Team
    depends_on = []

    def find_teams(self):
        return sorted(set(self.data["home_team"]) | set(self.data["away_team"]))

    def upload(self):
        AddNewTeams(*self.find_teams()).commit()
        return self

    def read(self, filepath: str):
        self.data = ExcelParser.read(filepath)
        self.update_final_mapper(filepath)
        return self

    @staticmethod
    def update_final_mapper(filepath: str):
        final_mapper_json = Path(filepath).parent / "final_mapper.json"

        if final_mapper_json.exists():
            print("Reading final mapper:", final_mapper_json)

            with open(final_mapper_json, "r", encoding="utf-8") as fp:
                data = json.load(fp)

            for key, val in data.items():
                assert key in config.FINALS_MAPPER.keys(), f"'{key}'"
                assert val in config.TEAMS or val == "", f"'{val}'"

            config.FINALS_MAPPER = data
            print(json.dumps(config.FINALS_MAPPER, indent=2, ensure_ascii=False))

        else:
            print("Writing final mapper:", final_mapper_json)
            final_mapper_json.write_text(
                json.dumps(config.FINALS_MAPPER, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )


class UploadGames(UploadBase):
    depends_on = [UploadTeams]
    base = Games

    def _add_datum_tijd(self):
        df = self.data
        df["date"] = df["datum"].str.removesuffix("00:00:00") + df["tijd"].str.removeprefix("1900-01-02 ")
        df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d %H:%M:%S")

    def upload(self):
        self._add_datum_tijd()
        AddNewGames(*(row._asdict() for row in self.data.itertuples(index=True))).commit()
        return self

    def upload_scores(self):
        self._add_datum_tijd()
        iterator = self.data[["poule", "date", "stadium", "home_goals", "away_goals"]].itertuples()

        UpdateScores(iterator).commit()
        return self

    def read(self, filepath: str):
        self.data = ExcelParser.read(filepath)
        return self


class UploadUsers(UploadBase):

    base = User
    depends_on = [UploadTeams, UploadGames]

    ENGINE = "openpyxl"
    GLOB = "*.xlsx"

    @staticmethod
    def get_bonus(file) -> dict:
        key_map = {
            "Aantal gele kaarten": "bonusvraag_gk",
            "Aantal rode kaarten": "bonusvraag_rk",
            "Aantal doelpunten": "bonusvraag_goals",
            "Topscoorder WK2022": "topscoorder",
            "Topscoorder EK2024": "topscoorder"
        }
        return (
            pd.read_excel(file, usecols="F:G", skiprows=6, engine="openpyxl", dtype=str)
            .dropna(axis=0, how="all")
            .set_index("Bonusvragen")
            .rename(index=key_map)
            .squeeze()
            .map(str.strip, na_action="ignore")
            .fillna("")
            .to_dict()
        )

    @staticmethod
    def get_user(file) -> dict:
        return {
            "naam": Path(file).stem,  # no suffix
            "team_naam": None,
            "leeftijd": None,
            "email": None,
            "betaald": False
        }

        # key_map = {
        #     'Naam': 'naam',
        #     'Teamnaam': 'team_naam',
        #     'Leeftijd': 'leeftijd',
        #     'Email': 'email',
        #     'Betaald': 'betaald'
        # }
        #
        # return (
        #     pd.read_excel(file, usecols='I:J', skiprows=1, engine="openpyxl", dtype=str)
        #     .dropna(axis=0, how='all')
        #     .set_index('Gebruiker')
        #     .squeeze()
        #     .map(str.strip, na_action='ignore')
        #     .rename(index=key_map)
        #     .fillna('')
        #     .to_dict()
        # )

    @staticmethod
    def get_ranking(file) -> list:
        values = pd.read_excel(
            file,
            skiprows=6,
            usecols="C:D",
            engine="openpyxl",
            dtype=str
        )
        assert tuple(values.iloc[:, 1].astype(int)) == config.POINTS, "Points inconsistent"
        return [Team.clean(val) for val in values.iloc[:, 0]]

    def read(self, path: str):
        self.data = [
            {"rankings": self.get_ranking(file)} | self.get_bonus(file) | self.get_user(file)
            for file in Path(path).glob(self.GLOB)
            if not file.name.startswith("_")
        ]
        return self

    def upload(self):
        AddNewUsers(*self.data).commit()
        return self
