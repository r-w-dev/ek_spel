import pandas as pd
from sqlalchemy import desc, func

from model import Team, Ranking, User
from update import get_session


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
        self.session = get_session()
        self.user_id = user_id
        self.data = {}

        result = self.get_ranking_query(self.session).all()

        print(pd.DataFrame(map(dict, result)).to_markdown())

    def totaal(self):
        subqry = self.get_ranking_query(self.session).subquery()
        totaal = self.session.query(func.sum(subqry.c.totaal)).group_by(subqry.c.naam).scalar()

        print(f"User {self.user_id}: {totaal}")
