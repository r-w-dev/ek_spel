import pandas as pd
from sqlalchemy import desc, func

from model import Team, Ranking, User
from session import Session


class UserRanking:

    PLAATS = 'Plaats'
    TEAM = 'Team'
    WAARDE = 'Waarde'
    TOTAAL = 'Totaal'

    def get_ranking_query(self, session):
        return (
            session
            .query(User.naam, User.team_naam, Team.team, Ranking.waarde, Team.punten,
                   (Ranking.waarde * Team.punten).label('totaal'))
            .join(Ranking, User.id == Ranking.user_id)
            .join(Team)
            .filter(Ranking.user_id == self.user_id)
            .order_by(User.naam, desc(Ranking.waarde))
        )


    def __init__(self, user_id):
        self.user_id = user_id
        self.data = {}

        with Session() as session:
            result = self.get_ranking_query(session).all()

        print(pd.DataFrame(map(dict, result)).to_markdown())

    def totaal(self):
        with Session() as session:
            subqry = self.get_ranking_query(session).subquery()
            totaal = session.query(func.sum(subqry.c.totaal)).group_by(subqry.c.naam).scalar()

        print(f"User {self.user_id}: {totaal}")
