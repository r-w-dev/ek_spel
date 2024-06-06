from wkspel.update import Sessie
import pandas as pd


class Dump(Sessie):

    _today = pd.Timestamp('today').strftime('%Y%m%d')

    def __init__(self, obj):
        self.obj = obj
        self.query = self.sessie.query(self.obj).order_by(self.obj.id).statement
        self.data = pd.read_sql(self.query, self.sessie.bind.engine)

    def to_excel(self):
        filename = f'{self._today}_dump_{self.obj.__tablename__}.xlsx'
        self.data.to_excel(filename, engine='openpyxl', index=False)
        print(f'DUMP: {self.obj.__tablename__} to {filename}')

    def to_csv(self):
        filename = f'{self._today}_dump_{self.obj.__tablename__}.csv'
        self.data.to_csv(filename, index=False, sep=';')
        print(f'DUMP: {self.obj.__tablename__} to {filename}')
