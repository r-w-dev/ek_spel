from poule import PouleDatabase
from update import UpdatePuntenSpel
from upload import UploadTeams, UploadGames, UploadUsers
from ranking import UserRanking


def initialize_data():
    UploadTeams(recreate=True).upload()
    UploadGames(recreate=True).upload()
    UploadUsers(recreate=True).upload()


def get_scores():
    pass


if __name__ == '__main__':
    initialize_data()

    get_scores()

    # UpdateScore(game_id=1).update(0, 3)
    UpdatePuntenSpel().commit()
    PouleDatabase().add_all().print()
    UserRanking(user_id=1).totaal()
