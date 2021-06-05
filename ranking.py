import pandas as pd
from sqlalchemy import desc, func
from sqlalchemy.orm import aliased
from sqlalchemy.sql import label

from model import Team, Ranking, User
from update import Sessie


class UserRanking(Sessie):

    TEAM = 'Team'
    WAARDE = 'Waarde'
    TOTAAL = 'Totaal'
    NAAM_USER = 'User - naam'
    TEAMNAAM_USER = 'User - teamnaam'
    PUNTEN_TEAM = 'Punten team'

    def get_ranking_query(self):
        FinalTeam = aliased(Team)

        # Calculate sum of all points (including finals) per team
        team_all_points = (
            self.sessie
            .query(
                FinalTeam.id,
                Team.team_finals,
                func.sum(Team.punten).label(self.PUNTEN_TEAM)
            )
            .group_by(Team.team_finals)
            .join(FinalTeam, Team.team_finals == FinalTeam.team)
            .subquery()
        )
        punten_per_land = getattr(team_all_points.c, self.PUNTEN_TEAM)

        return (
            self.sessie
            .query(
                label(self.NAAM_USER, User.naam),
                label(self.TEAMNAAM_USER, User.team_naam),
                label(self.TEAM, team_all_points.c.team_finals),
                label(self.PUNTEN_TEAM, punten_per_land),
                label(self.WAARDE, Ranking.waarde),
                label(self.TOTAAL, Ranking.waarde * punten_per_land)
            )
            .join(Ranking, User.id == Ranking.user_id)
            .join(team_all_points, team_all_points.c.id == Ranking.team_id)
            .filter(Ranking.user_id == self.user_id)
            .order_by(User.naam, desc(Ranking.waarde))
        )

    def __init__(self, user_id):
        self.user_id = user_id

        result = self.get_ranking_query().all()
        df = pd.DataFrame(map(dict, result), index=range(1, len(result)+1))

        print(df.to_markdown())

    def totaal(self):
        subqry = self.get_ranking_query().subquery()
        col_totaal = getattr(subqry.c, self.TOTAAL)
        col_naam = getattr(subqry.c, self.NAAM_USER)

        totaal = self.sessie.query(func.sum(col_totaal)).group_by(col_naam).scalar()
        print(f"\nUser {self.user_id}: {totaal} punt(en)")
