from poule import Poule, PouleDatabase, POULES

# pdb = PouleDatabase()
#
# for p in POULES:
#     obj = Poule(p)
#     pdb.add(obj)
#
# pdb.print()

# from ranking import UserRanking
#
# UserRanking(1)
#
# 4 + 6 + 6

# from update import UpdatePuntenSpel
# from model import recreate_table, Team
#
# # recreate_table(Team)
# UpdatePuntenSpel()
from ranking import UserRanking

UserRanking(1).update_totaal()
