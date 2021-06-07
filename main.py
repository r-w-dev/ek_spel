from poule import PouleDatabase
from update import UpdatePuntenSpel, UpdateUserPoints
from upload import UploadTeams, UploadGames, UploadUsers
from ranking import TopUsers
from dump import Dump
from model import User

def initialize_data():
    UploadTeams(recreate=True).upload()
    UploadGames(recreate=True).upload()
    UploadUsers(recreate=True).upload()


if __name__ == '__main__':
    initialize_data()

    UpdatePuntenSpel().commit()

    PouleDatabase().add_all().print()

    UpdateUserPoints().commit()

    TopUsers().print()

    Dump(User).to_excel()
