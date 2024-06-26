import os.path
from typing import Union

import pandas as pd

from wkspel.config import config


class ExcelFile:

    SHEET: str
    SKIPROWS: int
    COLUMNS: list[Union[str, int]]
    NAMES: list[str]

    _ENGINE: str

    @classmethod
    def read(cls, path: str) -> pd.DataFrame:
        assert len(cls.COLUMNS) == len(cls.NAMES), f"Lengths do not match: {len(cls.COLUMNS)} != {len(cls.NAMES)}"

        with open(path, "rb") as fp:
            # noinspection PyTypeChecker
            return pd.read_excel(
                fp,
                cls.SHEET,
                header=None,
                names=cls.NAMES,
                usecols=cls.COLUMNS,
                skiprows=cls.SKIPROWS,
                dtype=str,
                engine=cls._ENGINE
            ).dropna(how="all", axis=0)  # drop empty rows


class EKspel2021(ExcelFile):

    SHEET = "programma + uitslag"
    SKIPROWS = 2
    COLUMNS = [0, 1, 2, 3, 4, 6, 7, 8, 10]
    NAMES = [
        'fase',
        'datum',
        'tijd',
        'poule',
        'home_team',
        'away_team',
        'stadium',
        'home_goals',
        'away_goals'
    ]

    _ENGINE = "xlrd"


class WKspel2022(ExcelFile):

    SHEET = "speelschema"
    SKIPROWS = 5
    COLUMNS = [0, 1, 2, 3, 4, 5, 6, 7, 9]
    NAMES = [
        "fase",
        "poule",
        "datum",
        "tijd",
        "stadium",
        "home_team",
        "away_team",
        "home_goals",
        "away_goals"
    ]

    _ENGINE = "openpyxl"


class EKspel2024(ExcelFile):

    SHEET = "speelschema"
    SKIPROWS = 1
    COLUMNS = [0, 1, 2, 3, 4, 5, 6, 7, 9]
    NAMES = [
        "fase",
        "poule",
        "datum",
        "tijd",
        "stadium",
        "home_team",
        "away_team",
        "home_goals",
        "away_goals"
    ]

    _ENGINE = "openpyxl"


class ExcelParser:

    PARSER_HANDLERS = {
        "EKspel2021.xls": EKspel2021,
        "wk-2022-speelschema.xlsx": WKspel2022,
        "ek-2024-speelschema.xlsx": EKspel2024
    }

    @staticmethod
    def validate_teams(data: pd.DataFrame):
        for team in data["home_team"]:
            if team not in set(config.TEAMS) | config.FINALS_MAPPER.keys():
                raise ValueError(f"'{team}'")

        for team in data["away_team"]:
            if team not in set(config.TEAMS) | config.FINALS_MAPPER.keys():
                raise ValueError(f"'{team}'")

    @classmethod
    def read(cls, filepath: str) -> pd.DataFrame:
        _, filename = os.path.split(filepath)
        try:
            data = cls.PARSER_HANDLERS[filename].read(filepath)
        except KeyError:
            raise KeyError("Config not found: " + filename)

        cls.validate_teams(data)
        return data
