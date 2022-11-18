import pandas as pd
from sqlalchemy import desc, func
from sqlalchemy.orm import aliased
from sqlalchemy.sql import label

from wkspel.model import Team, Ranking, User
from wkspel.update import Sessie


def to_dataframe(query):
    return pd.DataFrame(map(dict, query), index=range(1, len(query) + 1))


class UserRanking(Sessie):

    TEAM = 'Team'
    WAARDE = 'Waarde'
    TOTAAL = 'Totaal'
    NAAM_USER = 'User - naam'
    TEAMNAAM_USER = 'User - teamnaam'
    PUNTEN_TEAM = 'Punten team'

    def __init__(self, user: User):
        self.user = user

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
            .filter(Ranking.user_id == self.user.id)
            .order_by(User.naam, desc(Ranking.waarde))
        )

    def update_totaal(self):
        subqry = self.get_ranking_query().subquery()
        col_totaal = getattr(subqry.c, self.TOTAAL)
        col_naam = getattr(subqry.c, self.NAAM_USER)

        points_update = self.sessie.query(func.sum(col_totaal)).group_by(col_naam).scalar()

        if self.user.punten != points_update:
            print(f"Updating '{self.user.naam}' to '{points_update}' points ({points_update-self.user.punten:+})")
            self.sessie.merge(User(id=self.user.id, punten=points_update))


class TopUsers(Sessie):

    def __init__(self, top_n=10):
        self.data = to_dataframe(
            self.sessie.query(
                User.id,
                User.naam,
                User.team_naam,
                User.topscoorder,
                User.bonusvraag_gk,
                User.bonusvraag_rk,
                User.bonusvraag_goals,
                User.punten
            ).order_by(desc(User.punten))
            .limit(top_n)
            .all()
        ).to_markdown(index=False)

    def print(self):
        print(self.data)
