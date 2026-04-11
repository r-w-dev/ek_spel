import warnings

import pandas as pd
from sqlalchemy import select

from wkspel.update import Sessie


class Dump(Sessie):

    _today = pd.Timestamp('today').strftime('%Y%m%d')

    def __init__(self, obj):
        self.obj = obj
        self.query = select(self.obj).order_by(self.obj.id)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            self.data = pd.read_sql(str(self.query), self.sessie.bind.raw_connection())

    def to_excel(self):
        filename = f'{self._today}_dump_{self.obj.__tablename__}.xlsx'
        self.data.to_excel(filename, engine='openpyxl', index=False)
        print(f'DUMP: {self.obj.__tablename__} to {filename}')

    def to_csv(self):
        filename = f'{self._today}_dump_{self.obj.__tablename__}.csv'
        self.data.to_csv(filename, index=False, sep=';')
        print(f'DUMP: {self.obj.__tablename__} to {filename}')
