from abc import ABC


class BaseConfig(ABC):

    POINTS: tuple[int]
    TEAMS: tuple[str]
    POULES: tuple[str]
    TYPES: dict[str, tuple[str]]
    FINALS_MAPPER: dict[str, str]
    TEAM_ALIAS: dict[str, str] = {}

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

    TOTAL_GAMES = 64

    POINTS = (80, *range(70, 35, -5), 36, 32, 28, 25, 22, 20, *range(18, 0, -1))

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


class EKspel2024Config(BaseConfig):

    TOTAL_GAMES = 51

    POINTS = (50, 43, 38, 33, 30, 27, *range(24, 12, -2), *range(12, 0, -1))

    TEAMS = (
        "Albanië",
        "België",
        "Denemarken",
        "Duitsland",
        "Engeland",
        "Frankrijk",
        "Georgië",
        "Hongarije",
        "Italië",
        "Kroatië",
        "Nederland",
        "Oekraïne",
        "Oostenrijk",
        "Polen",
        "Portugal",
        "Roemenië",
        "Schotland",
        "Servië",
        "Slovenië",
        "Slowakije",
        "Spanje",
        "Tsjechië",
        "Turkije",
        "Zwitserland",
    )

    TEAM_ALIAS = {
        "Oekraine": "Oekraïne"
    }

    assert len(TEAMS) == len(POINTS) == 24

    POULES = tuple("ABCDEF")

    TYPES = {
        "Poule": POULES,
        "8_FINAL": ("8F1", "8F2", "8F3", "8F4", "8F5", "8F6", "8F7", "8F8"),
        "Q_FINAL": ("QF1", "QF2", "QF3", "QF4"),
        "S_FINAL": ("SF1", "SF2"),
        "FINAL": ("FINAL",)
    }

    FINALS_MAPPER = {
        # Eighth finals - first and second in poule
        "1A": "",
        "1B": "",
        "1C": "",
        "1D": "",
        "1E": "",
        "1F": "",

        "2A": "",
        "2B": "",
        "2C": "",
        "2D": "",
        "2E": "",
        "2F": "",

        # best third place in poule
        "3DEF": "",
        "3ADEF": "",
        "3ABC": "",
        "3ABCD": "",

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
    }


class WKspel2026Config(BaseConfig):
    """Configuration for WKspel 2026."""

    TOTAL_GAMES = 104

    POINTS = (
        150,
        135,
        125,
        120,
        115,
        110,
        105,
        100,
        95,
        91,
        87,
        83,
        79,
        75,
        71,
        67,
        63,
        59,
        55,
        52,
        49,
        46,
        43,
        40,
        37,
        34,
        31,
        28,
        25,
        23,
        21,
        19,
        17,
        15,
        14,
        13,
        12,
        11,
        10,
        9,
        8,
        7,
        6,
        5,
        4,
        3,
        2,
        1,
    )

    TEAMS = (
        "Algerije",
        "Argentinië",
        "Australië",
        "België",
        "Bosnië-Herzegovina",
        "Brazilië",
        "Canada",
        "Colombia",
        "Curacao",
        "Congo",
        "Duitsland",
        "Ecuador",
        "Egypte",
        "Engeland",
        "Frankrijk",
        "Ghana",
        "Haïti",
        "Irak",
        "Iran",
        "Ivoorkust",
        "Japan",
        "Jordanië",
        "Kaapverdië",
        "Kroatië",
        "Marokko",
        "Mexico",
        "Nederland",
        "Nieuw-Zeeland",
        "Noorwegen",
        "Oezbekistan",
        "Oostenrijk",
        "Panama",
        "Paraguay",
        "Portugal",
        "Qatar",
        "Saoedi-Arabië",
        "Schotland",
        "Senegal",
        "Spanje",
        "Tsjechië",
        "Tunesië",
        "Turkije",
        "Verenigde Staten",
        "Uruguay",
        "Zuid-Afrika",
        "Zuid-Korea",
        "Zweden",
        "Zwitserland",
    )

    assert len(TEAMS) == len(POINTS) == 48

    POULES = tuple("ABCDEFGHIJKL")

    TYPES = {
        "Poule": POULES,
        "32_FINAL": (
            "32F1",
            "32F2",
            "32F3",
            "32F4",
            "32F5",
            "32F6",
            "32F7",
            "32F8",
            "32F9",
            "32F10",
            "32F11",
            "32F12",
            "32F13",
            "32F14",
            "32F15",
            "32F16"
        ),
        "16_FINAL": (
            "16F1",
            "16F2",
            "16F3",
            "16F4",
            "16F5",
            "16F6",
            "16F7",
            "16F8"
        ),
        "Q_FINAL": (
            "QF1",
            "QF2",
            "QF3",
            "QF4"
        ),
        "S_FINAL": (
            "SF1",
            "SF2"
        ),
        "FINAL": (
            "FINAL",
            "3RD"
        )
    }

    FINALS_MAPPER = {
        "1A": "",
        "1B": "",
        "1C": "",
        "1D": "",
        "1E": "",
        "1F": "",
        "1G": "",
        "1H": "",
        "1I": "",
        "1J": "",
        "1K": "",
        "1L": "",
        "2A": "",
        "2B": "",
        "2C": "",
        "2D": "",
        "2E": "",
        "2F": "",
        "2G": "",
        "2H": "",
        "2I": "",
        "2J": "",
        "2K": "",
        "2L": "",
        "3ABCDF": "",
        "3AEHIJ": "",
        "3BEFIJ": "",
        "3CDFGH": "",
        "3CEFHI": "",
        "3DEIJL": "",
        "3EFGIJ": "",
        "3EHIJK": "",

        # Winners of Round of 32
        "W32F1": "",
        "W32F2": "",
        "W32F3": "",
        "W32F4": "",
        "W32F5": "",
        "W32F6": "",
        "W32F7": "",
        "W32F8": "",
        "W32F9": "",
        "W32F10": "",
        "W32F11": "",
        "W32F12": "",
        "W32F13": "",
        "W32F14": "",
        "W32F15": "",
        "W32F16": "",

        # Winners of Round of 16
        "W16F1": "",
        "W16F2": "",
        "W16F3": "",
        "W16F4": "",
        "W16F5": "",
        "W16F6": "",
        "W16F7": "",
        "W16F8": "",

        # Winners of Quarter finals
        "WQF1": "",
        "WQF2": "",
        "WQF3": "",
        "WQF4": "",

        # Winners of Semi finals
        "WSF1": "",
        "WSF2": "",

        # Losers of Semi finals (for 3rd place)
        "LSF1": "",
        "LSF2": "",
    }

    TEAM_ALIAS = {}


# define current config
config = WKspel2026Config
