from pathlib import Path

DB_CONFIG = {
    'drivername': 'sqlite',
    'username': None,
    'password': None,
    'host': None,
    'port': None,
    'database': 'data.sqlite'
}
SOURCE_FILE = 'EKspel2021.xls'
SHEET_PROGRAMMA = 'programma + uitslag'

USER_FOLDER = Path.cwd() / 'invullijsten'

POINTS = (50, 43, 38, 33, 30, 27, *range(24, 12, -2), *range(12, 0, -1))

TEAMS = (
    'België',
    'Denemarken',
    'Duitsland',
    'Engeland',
    'Finland',
    'Frankrijk',
    'Hongarije',
    'Italië',
    'Kroatië',
    'Nederland',
    'Noord-Macedonië',
    'Oekraïne',
    'Oostenrijk',
    'Polen',
    'Portugal',
    'Rusland',
    'Schotland',
    'Slowakije',
    'Spanje',
    'Tsjechië',
    'Turkije',
    'Wales',
    'Zweden',
    'Zwitserland',
)

assert len(TEAMS) == len(POINTS) == 24

POULES = tuple('ABCDEF')

TYPES = {
    'Poule': POULES,
    '8_FINAL': ('8F1', '8F2', '8F3', '8F4', '8F5', '8F6', '8F7', '8F8'),
    'Q_FINAL': ('QF1', 'QF2', 'QF3', 'QF4'),
    'S_FINAL': ('SF1', 'SF2'),
    'FINAL': ('FINAL',)
}

ALL_TYPES = [v for k in TYPES for v in TYPES[k]]

FINALS_MAPPER = {
    # eighth finals
    '2A': '',
    '2B': '',
    '1A': '',
    '2C': '',
    '1C': '',
    '3DEF': '',
    '1B': '',
    '3ADEF': '',
    '2D': '',
    '2E': '',
    '1F': '',
    '3ABC': '',
    '1D': '',
    '2F': '',
    '1E': '',
    '3ABCD': '',

    # quarter finals
    'WINNAAR 8F6': '',
    'WINNAAR 8F5': '',
    'WINNAAR 8F4': '',
    'WINNAAR 8F2': '',
    'WINNAAR 8F3': '',
    'WINNAAR 8F1': '',
    'WINNAAR 8F8': '',
    'WINNAAR 8F7': '',

    # semi finals
    'WINNAAR QF2': '',
    'WINNAAR QF1': '',
    'WINNAAR QF4': '',
    'WINNAAR QF3': '',

    # final
    'WINNAAR SF1': '',
    'WINNAAR SF2': ''
}


WINST = 3
GELIJK = 1
VERLIES = 0

MULTIPLIER = {
    WINST: 3,
    GELIJK: 2,
    VERLIES: 1
}


def get_points(goals_home, goals_away):
    if goals_home is None or goals_away is None:
        return None
    elif goals_home == goals_away:
        return GELIJK
    elif goals_home > goals_away:
        return WINST
    else:
        return VERLIES


def get_punten_spel(points, goals):
    if points is None:
        return 0
    return MULTIPLIER[points] * (goals + 1)
