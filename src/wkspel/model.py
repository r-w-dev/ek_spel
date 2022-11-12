import os

from sqlalchemy import Integer, Column, String, Boolean, ForeignKey, DateTime, UniqueConstraint, \
    Table
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import declarative_base, relationship, validates

from wkspel.config import config

engine = create_engine(os.environ["CONNECTION_STRING"], echo=False)


@event.listens_for(engine, "connect")
def do_connect(dbapi_connection, connection_record):
    # disable pysqlite's emitting of the BEGIN statement entirely.
    # also stops it from emitting COMMIT before any DDL.
    dbapi_connection.isolation_level = None

    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    # cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA locking_mode=EXCLUSIVE")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA busy_timeout=5000")
    cursor.close()


@event.listens_for(engine, "begin")
def do_begin(conn):
    # emit our own BEGIN
    conn.exec_driver_sql("BEGIN")


# define base
Base = declarative_base(bind=engine)


def has_table(table):
    return table.__table__.exists(bind=engine)


def drop_table(table):
    if has_table(table):
        print("Dropping table: ", str(table.__table__))
        table.__table__.drop(bind=engine)


def create_table(table):
    print("Creating table: ", str(table.__table__))
    table.__table__.create(bind=engine)


def recreate_table(table):
    drop_table(table)
    create_table(table)


def create_all(drop_first=False):
    if drop_first:
        drop_all()
    Base.metadata.create_all(checkfirst=True)


def drop_all():
    to_drop = [table for table in Base.metadata.sorted_tables if not str(table).startswith('sqlite_')]
    Base.metadata.drop_all(tables=to_drop, checkfirst=True)


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


class TableBase:

    @classmethod
    def __tablename__(cls):
        pass

    @declared_attr
    def __table__(cls):
        return Table(cls.__tablename__, Base.metadata, autoload=True, autoload_with=engine)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    naam = Column(String)
    team_naam = Column(String)
    leeftijd = Column(Integer)
    email = Column(String)
    topscoorder = Column(String)
    bonusvraag_gk = Column(Integer)
    bonusvraag_rk = Column(Integer)
    bonusvraag_goals = Column(Integer)
    betaald = Column(Boolean, default=False)
    punten = Column(Integer, default=0)

    __table_args__ = (
        UniqueConstraint(naam, team_naam),
        UniqueConstraint(topscoorder, bonusvraag_gk, bonusvraag_rk, bonusvraag_goals),
        {'sqlite_autoincrement': True}
    )

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


class Team(Base):
    __tablename__ = 'teams'
    __table_args__ = {'sqlite_autoincrement': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    team = Column(String, nullable=False, unique=True)
    team_finals = Column(String, nullable=False, unique=False)
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
        return config.FINALS_MAPPER.get(value.upper()) or value

    @classmethod
    def clean(cls, value):
        return ''.join(s for s in value if s in {' ', '-'} or str.isalnum(s)).strip()


class Ranking(Base):
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
        {'sqlite_autoincrement': True}
    )

    @validates('user_id', 'team_id')
    def validate_int(self, key, value):
        return validate_int(value, key=key, nullable=True)


User.rankings = relationship('Ranking', order_by=Ranking.id, back_populates='user')
Team.rankings = relationship('Ranking', order_by=Ranking.id, back_populates='team')


class Games(Base):
    __tablename__ = 'games'

    id = Column(Integer, primary_key=True, nullable=False)
    date = Column(DateTime, nullable=False)
    type = Column(String, nullable=False)
    poule = Column(String, nullable=False)
    stage = Column(String, nullable=False, primary_key=True)
    stadium = Column(String, nullable=False)

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
        for typ in config.TYPES:
            if group in config.TYPES[typ]:
                return typ
        else:
            raise ValueError


Team.games = relationship('Games', order_by=Games.id, back_populates='team_name')
