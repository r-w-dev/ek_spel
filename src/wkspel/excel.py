import os.path

import pandas as pd


class ExcelFile:

    SHEET: str
    FILENAME: str
    HEADER: int
    COLUMNS: list[str | int]
    NAMES: list[str]

    _ENGINE: str

    @classmethod
    def read(cls, path: str) -> pd.DataFrame:
        assert len(cls.COLUMNS) == len(cls.NAMES), f"Lengths do not match: {len(cls.COLUMNS)} != {len(cls.NAMES)}"
        # noinspection PyTypeChecker
        return pd.read_excel(
            path,
            cls.SHEET,
            header=cls.HEADER,
            names=cls.NAMES,
            usecols=cls.COLUMNS,
            dtype=str,
            engine=cls._ENGINE
        ).dropna(how="all", axis=0)


class EKspel2021(ExcelFile):

    SHEET = "programma + uitslag"
    FILENAME = "EKspel2021.xls"
    HEADER = 1
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
    FILENAME = "WKspel2022.xlsx"
    HEADER = 4
    COLUMNS = [0, 1, 2, 3, 4, 5, 6, 7, 9]
    NAMES = [
        'fase',
        'poule',
        'datum',
        'tijd',
        'home_team',
        'away_team',
        'stadium',
        'home_goals',
        'away_goals'
    ]

    _ENGINE = "openpyxl"


class ExcelParser:

    PARSER_HANDLERS = {
        "EKspel2021.xls": EKspel2021,
        "wk-2022-speelschema.xlsx": WKspel2022
    }

    @classmethod
    def read(cls, filepath: str) -> pd.DataFrame:
        _, filename = os.path.split(filepath)
        try:
            return cls.PARSER_HANDLERS[filename].read(filepath)
        except KeyError:
            raise FileNotFoundError
