
class BaseConfig:

    POINTS: tuple[int]
    TEAMS: tuple[str]
    POULES: tuple[str]
    TYPES: dict
    FINALS_MAPPER: dict

    WINST = 3
    GELIJK = 1
    VERLIES = 0

    MULTIPLIER = {
        WINST: 3,
        GELIJK: 2,
        VERLIES: 1
    }

    @classmethod
    def all_types(cls) -> list[str]:
        return [v for k in cls.TYPES for v in cls.TYPES[k]]

    @classmethod
    def get_points(cls, goals_home: int, goals_away: int):
        if goals_home is None or goals_away is None:
            return None
        elif goals_home == goals_away:
            return cls.GELIJK
        elif goals_home > goals_away:
            return cls.WINST
        else:
            return cls.VERLIES

    @classmethod
    def get_punten_spel(cls, points: int, goals: int):
        if points is None:
            return 0
        return cls.MULTIPLIER[points] * (goals + 1)


class EKspel2021Config(BaseConfig):

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


class WKspel2022Config(BaseConfig):

    POINTS = (100, 91, 83, 76, *range(70, 25, -5), 27, *range(24, 12, -2), *range(12, 0, -1))

    TEAMS = (
        "Argentinië",
        "Australië",
        "België",
        "Brazilië",
        "Canada",
        "Costa Rica",
        "Denemarken",
        "Duitsland",
        "Ecuador",
        "Engeland",
        "Frankrijk",
        "Ghana",
        "Iran",
        "Japan",
        "Kameroen",
        "Kroatië",
        "Marokko",
        "Mexico",
        "Nederland",
        "Polen",
        "Portugal",
        "Qatar",
        "Saudi-Arabië",
        "Senegal",
        "Servië",
        "Spanje",
        "Tunesië",
        "Uruguay",
        "Verenigde Staten",
        "Wales",
        "Zuid-Korea",
        "Zwitserland"
    )

    assert len(TEAMS) == len(POINTS) == 32

    POULES = tuple("ABCDEFGH")

    TYPES = {
        "Poule": POULES,
        "8_FINAL": ("8F1", "8F2", "8F3", "8F4", "8F5", "8F6", "8F7", "8F8"),
        "Q_FINAL": ("QF1", "QF2", "QF3", "QF4"),
        "S_FINAL": ("SF1", "SF2"),
        "FINAL": ("FINAL", "BRONZE")
    }

    FINALS_MAPPER = {
        # Eighth finals - first and second in poule
        "1A": "",
        "1B": "",
        "1C": "",
        "1D": "",
        "1E": "",
        "1F": "",
        "1G": "",
        "1H": "",

        "2A": "",
        "2B": "",
        "2C": "",
        "2D": "",
        "2E": "",
        "2F": "",
        "2G": "",
        "2H": "",

        # Quarter finals - Winner Eight finals
        "W8F1": "",
        "W8F2": "",
        "W8F3": "",
        "W8F4": "",
        "W8F5": "",
        "W8F6": "",
        "W8F7": "",
        "W8F8": "",

        # Semi finals - Winner Quater Final
        "WQF1": "",
        "WQF2": "",
        "WQF3": "",
        "WQF4": "",

        # Final - Winner Semi Final
        "WSF1": "",
        "WSF2": "",

        # Bronze final - Loser Semi Final
        "LSF1": "",
        "LSF2": ""
    }


# define config
config = WKspel2022Config
