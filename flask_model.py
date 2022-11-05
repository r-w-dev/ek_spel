from sqlalchemy import Integer, Column, String, Boolean, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship, validates

from config import TYPES, FINALS_MAPPER
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

_STR_SIZE = 256


def validate_int(value, nullable=False, gt_zero=True, key=None):
    msg = f"Key '{key}' is not an integer: {value} ({type(value)})"
    is_digit_str = isinstance(value, str) and value.isdigit()
    is_int_float = isinstance(value, float) and value.is_integer()
    is_nan = value != value

    if nullable and (value is None or is_nan):
        return None
    elif isinstance(value, int):
        pass
    elif is_digit_str or is_int_float:
        value = int(value)
    else:
        raise ValueError(msg)

    if gt_zero and value < 0:
        raise ValueError(msg)

    return value


class User(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    naam = Column(String(_STR_SIZE))
    team_naam = Column(String(_STR_SIZE))
    leeftijd = Column(Integer)
    email = Column(String(_STR_SIZE))
    topscoorder = Column(String(_STR_SIZE))
    bonusvraag_gk = Column(Integer)
    bonusvraag_rk = Column(Integer)
    bonusvraag_goals = Column(Integer)
    betaald = Column(Boolean, default=False)
    punten = Column(Integer, default=0)

    def __repr__(self):
        return f"<User(id={self.id}, name={self.naam}, teamnaam={self.team_naam})"

    @validates('leeftijd', 'bonusvraag_gk', 'bonusvraag_rk', 'bonusvraag_goals')
    def validate_int(self, key, value):
        return validate_int(value, key=key)

    @validates('email')
    def validate_email(self, key, value):
        if '@' not in value:
            raise ValueError
        return value

    @validates('betaald')
    def validate_betaald(self, key, value):
        test = value.upper() if isinstance(value, str) else value
        return test in {'1', 'J', 'TRUE', True, 1}


class Team(db.Model):
    __tablename__ = 'teams'

    id = Column(Integer, primary_key=True, autoincrement=True)
    team = Column(String(_STR_SIZE), nullable=False, unique=True)
    team_finals = Column(String(_STR_SIZE), nullable=False, unique=False)
    punten = Column(Integer, default=0)

    def __repr__(self):
        return f"<Team(id={self.id}, teamnaam={self.team})"

    @validates('punten')
    def validate_int(self, key, value):
        return validate_int(value, key=key)

    @validates('team', 'team_finals')
    def validate_team(self, key, value):
        return self.clean(value)

    @classmethod
    def get_final_team(cls, value):
        return FINALS_MAPPER.get(value.upper()) or value

    @classmethod
    def clean(cls, value):
        return ''.join(s for s in value if s in {' ', '-'} or str.isalnum(s)).strip()


class Ranking(db.Model):
    """Een user geeft een lijst van landen een bepaalde waarde."""

    __tablename__ = 'ranking'

    id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(Integer, ForeignKey('users.id'))
    team_id = Column(Integer, ForeignKey('teams.id'))
    waarde = Column(Integer)

    user = relationship('User', back_populates='rankings')
    team = relationship('Team', back_populates='rankings')

    def __repr__(self):
        return f"<Ranking(id={self.id}, user_id={self.user_id}, team_id={self.team_id}, waarde={self.waarde})"

    __table_args__ = (
        UniqueConstraint(user_id, team_id),
    )

    @validates('user_id', 'team_id')
    def validate_int(self, key, value):
        return validate_int(value, key=key, nullable=True)


User.rankings = relationship('Ranking', order_by=Ranking.id, back_populates='user')
Team.rankings = relationship('Ranking', order_by=Ranking.id, back_populates='team')


class Games(db.Model):
    __tablename__ = 'games'

    id = Column(Integer, primary_key=True, nullable=False)
    date = Column(DateTime, nullable=False)
    type = Column(String(_STR_SIZE), nullable=False)
    poule = Column(String(_STR_SIZE), nullable=False)
    stage = Column(String(_STR_SIZE), nullable=False, primary_key=True)
    stadium = Column(String(_STR_SIZE), nullable=False)

    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    goals = Column(Integer, default=None)

    team_name = relationship('Team', back_populates='games')

    def __repr__(self):
        return f"<Games(id={self.id}, type={self.type}, poule={self.poule}, team_id={self.team_id}, goals={self.goals})"

    __table_args__ = (
        UniqueConstraint(date, stage, stadium),
    )

    @validates('id', 'team_id')
    def validate_int(self, key, value):
        return validate_int(value, key=key)

    @validates('goals')
    def validate_goals(self, key, value):
        return validate_int(value, gt_zero=False, nullable=True, key=key)

    @validates('setting')
    def validate_setting(self, key, value):
        if value not in {'home', 'away'}:
            raise ValueError(f"'{key}' has invalid value: {value}")
        return value

    @classmethod
    def get_type(cls, group):
        for typ in TYPES:
            if group in TYPES[typ]:
                return typ
        else:
            raise ValueError


Team.games = relationship('Games', order_by=Games.id, back_populates='team_name')
