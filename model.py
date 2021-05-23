from sqlalchemy import Integer, Column, String, Boolean, ForeignKey, DateTime, UniqueConstraint, \
    Table
from sqlalchemy import create_engine, event
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import declarative_base, relationship, validates


from config import DB_CONFIG, TYPES, FINALS_MAPPER

engine = create_engine(URL(**DB_CONFIG), echo=False)


@event.listens_for(engine, "connect")
def do_connect(dbapi_connection, connection_record):
    # disable pysqlite's emitting of the BEGIN statement entirely.
    # also stops it from emitting COMMIT before any DDL.
    dbapi_connection.isolation_level = None

    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
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
    table.__table__.drop(bind=engine)


def create_table(table):
    table.__table__.create(bind=engine)


def recreate_table(table):
    drop_table(table)
    create_table(table)


def validate_int(value, nullable=False, gt_zero=True, key=None):
    msg = f"Key '{key}' is not an integer: {value} ({type(value)})"
    is_digit_str = isinstance(value, str) and value.isdigit()
    is_int_float = isinstance(value, float) and value.is_integer()

    if nullable and value is None:
        return value
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

    def __tablename__(cls):
        pass

    @declared_attr
    def __table__(cls):
        return Table(cls.__tablename__, Base.metadata, autoload=True, autoload_with=engine)


class User(Base):

    __tablename__ = 'users'
    __table_args__ = {'sqlite_autoincrement': True}

    id = Column(Integer, primary_key=True, unique=True)
    naam = Column(String)
    team_naam = Column(String)
    leeftijd = Column(Integer)
    email = Column(String)
    topscoorder = Column(String)
    bonusvraag_gk = Column(Integer)
    bonusvraag_rk = Column(Integer)
    bonusvraag_goals = Column(Integer)
    betaald = Column(Boolean)

    def __repr__(self):
        return f"<User(name={self.naam}, teamnaam={self.team_naam})"

    @validates('id', 'leeftijd', 'bonusvraag_gk', 'bonusvraag_rk', 'bonusvraag_goals')
    def validate_int(self, key, value):
        return validate_int(value, key=key)

    @validates('email')
    def validate_email(self, key, value):
        if '@' not in value:
            raise ValueError
        return value


class Team(Base):

    __tablename__ = 'teams'
    __table_args__ = {'sqlite_autoincrement': True}

    id = Column(Integer, primary_key=True)
    team = Column(String, nullable=False, unique=True)
    punten = Column(Integer, default=0)

    def __repr__(self):
        return f"<Team(id={self.id}, teamnaam={self.team})"

    @validates('id')
    def validate_int(self, key, value):
        return validate_int(value, key=key)

    @validates('team')
    def validate_team(self, key, value):
        return self.clean(value)

    @classmethod
    def get_final_team(cls, value):
        return FINALS_MAPPER.get(value.upper()) or value

    @classmethod
    def clean(cls, value):
        return ''.join(s for s in value if s in {' ', '-'} or str.isalnum(s))


class Ranking(Base):
    """Een user geeft een lijst van landen een bepaalde waarde."""

    __tablename__ = 'ranking'

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey('users.id'))
    team_id = Column(Integer, ForeignKey('teams.id'))
    waarde = Column(Integer)

    user = relationship('User', back_populates='rankings')
    team = relationship('Team', back_populates='rankings', lazy='joined', innerjoin=True)

    def __repr__(self):
        return f"<Ranking(id={self.id}, user_id={self.user_id}, team_id={self.team_id}, waarde={self.waarde})"

    __table_args__ = (
        UniqueConstraint(user_id, team_id),
        {'sqlite_autoincrement': True}
    )

    @validates('id', 'user_id', 'team_id')
    def validate_int(self, key, value):
        return validate_int(value, key=key)


User.rankings = relationship('Ranking', order_by=Ranking.id, back_populates='user')
Team.rankings = relationship('Ranking', order_by=Ranking.id, back_populates='team')


class Games(Base):

    __tablename__ = 'games'

    id = Column(Integer, primary_key=True, nullable=False)
    date = Column(DateTime, nullable=False)
    type = Column(String, nullable=False)
    poule = Column(String, nullable=False)
    stage = Column(String, nullable=False)
    stadium = Column(String, nullable=False)

    team_id = Column(Integer, ForeignKey('teams.id'), primary_key=True, nullable=False)
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


Base.metadata.create_all(checkfirst=True)
Base.metadata.reflect()
