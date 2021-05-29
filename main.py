from upload import UploadTeams, UploadGames, UploadUsers
from update import UpdateScore
from poule import PouleDatabase


if __name__ == '__main__':
    UploadTeams(recreate=True).upload().commit()
    UploadGames(recreate=True).upload().commit()
    UploadUsers(recreate=True).upload().commit()

    UpdateScore(game_id=1).update(0, 3)

    PouleDatabase().add_all().print()
