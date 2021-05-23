from typing import Iterator
from sqlalchemy.orm import sessionmaker
from model import engine

Sessionmaker = sessionmaker(bind=engine)


class Session:

    session = None

    def __getattr__(self, item):
        if hasattr(self, item):
            return getattr(self, item)
        else:
            return getattr(self.session, item)

    def __enter__(self):
        if self.session is None:
            self.session = Sessionmaker()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_tb is not None:
            self.session.rollback()
        else:
            self.session.commit()
        self.session.close()

    def add(self, obj):
        if isinstance(obj, (list, tuple, Iterator)):
            self.session.add_all(obj)
        else:
            self.session.add(obj)

    def truncate(self, obj):
        self.session.query(obj).delete()

    def query(self, *entities, **kwargs):
        return self.session.query(*entities, **kwargs)

    def merge(self, obj):
        if isinstance(obj, (list, tuple, Iterator)):
            for o in obj:
                self.session.merge(o)
        else:
            self.session.merge(obj)
