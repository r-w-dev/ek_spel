import os
import argparse
import sys
from importlib import import_module
from pathlib import Path

from sqlalchemy.engine import make_url


def create_handler(args: argparse.Namespace):
    print("CREATE")
    from wkspel.model import create_all

    if args.recreate:
        if input("Recreating tables, are you sure? (type IAMSURE)") != "IAMSURE":
            print("Not sure, exiting")
            sys.exit(0)

    create_all(drop_first=args.recreate)
    print("Finished: creating")


def load_handler(args: argparse.Namespace):
    print("LOAD")

    if not (args.source_file or args.source_forms):
        print("No load parameters passed. See 'load --help'")

    from wkspel.upload import UploadTeams, UploadGames, UploadUsers

    if args.source_file:
        print(f"Processing source_file: {args.source_file}")
        filename = args.source_file

        if args.scores_only:
            print("Processing scores")
            UploadGames().read(filename).upload_scores()
        else:
            UploadTeams(args.recreate).read(filename).upload()
            UploadGames(args.recreate).read(filename).upload()

    if args.source_forms:
        UploadUsers(args.recreate).read(args.source_forms).upload()


def update_handler(args: argparse.Namespace):
    print("UPDATE")

    from wkspel.update import UpdatePuntenSpel, UpdateUserPoints
    from wkspel.upload import UploadGames, UploadTeams

    if args.source_file:
        print("Uploading scores")
        UploadTeams().read(args.source_file).upload()
        UploadGames().read(args.source_file).upload_scores()

    if not args.teams and not args.users:
        UpdatePuntenSpel().commit()
        UpdateUserPoints().commit()
    elif args.teams:
        UpdatePuntenSpel().commit()
    elif args.users:
        UpdateUserPoints().commit()


def print_handler(args: argparse.Namespace):
    print("PRINT")

    if args.top:
        from wkspel.ranking import TopUsers
        TopUsers(top_n=args.top).print()

    if args.poule:
        from wkspel.poule import PouleDatabase
        PouleDatabase().add_all().print()


def dump_handler(args: argparse.Namespace):
    print("DUMP")

    from wkspel.dump import Dump

    def dump_table(tablename: str):
        model = import_module("model")
        Dump(getattr(model, tablename)).to_excel()

    if args.table:
        dump_table(args.table)

    else:
        for table in args.table.choices:
            dump_table(table)


def init_arg_parser():
    arg_parser = argparse.ArgumentParser(
        description="WKspel 2002 application",
        epilog="Have fun!"
    )
    subparsers = arg_parser.add_subparsers()

    create = subparsers.add_parser("create", help="Migrate tables into the database")
    create.add_argument("--recreate", help="Clear current database first *DANGEROUS*", action="store_true")
    create.set_defaults(func=create_handler)

    load = subparsers.add_parser("load", help="Initial load of all data")
    load.add_argument("--source_file", help="Path to source (excel) file")
    load.add_argument("--source_forms", help="Folder with forms submitted by contestants")
    load.add_argument("--scores_only", help="Only update scores from source file", action="store_true")
    load.add_argument("--recreate", help="Clear current database first *DANGEROUS*", action="store_true")
    load.set_defaults(func=load_handler)

    update = subparsers.add_parser("update", help="Update operations on tables")
    update.add_argument("--teams", action="store_true")
    update.add_argument("--users", action="store_true")
    update.add_argument("--source_file", help="Path to source (excel) file")
    update.set_defaults(func=update_handler)

    print_ = subparsers.add_parser("print", help="print statistics")
    print_.add_argument("--top", type=int, action="store")
    print_.add_argument("--poule", action="store", default="all")
    print_.set_defaults(func=print_handler)

    dump = subparsers.add_parser("dump", help="Dump to file")
    dump.add_argument("--table", action="store", choices=["User", "Team", "Ranking", "Games"])

    return arg_parser


def validate_connection_string():
    conn_string = os.environ.get("CONNECTION_STRING")

    if not conn_string:
        raise ConnectionError("No connection defined in environment variable 'CONNECTION_STRING'")

    url = make_url(conn_string)

    if url.database.endswith(".db") and Path(url.database).exists():
        print("Database exists: ", url.database)


def main():
    # windows default encoding is not utf-8
    sys.stdout.reconfigure(encoding='utf-8')

    parser = init_arg_parser()
    args = parser.parse_args()

    validate_connection_string()

    try:
        args.func(args)  # call relevant handler
    except AttributeError:
        print("handler not known or passed, exiting..")
        sys.exit(1)


if __name__ == '__main__':
    main()
