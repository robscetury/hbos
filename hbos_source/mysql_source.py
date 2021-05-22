import decimal
import typing
from typing import Dict, List

import mysql.connector.connection
from pandas import DataFrame

from hbos_server.connection_manager import get_manager
from hbos_server.sourcebase import SourceBase


class MySQLSource(SourceBase):
    def create(self, objs_to_create: List[Dict[str, typing.Any]],*args, **kwargs) -> DataFrame:
        pass

    def retrieve(self, *args, **kwargs) -> DataFrame:
        manager = get_manager()
        options = self.options
        conn : mysql.connector.connection.MySQLConnection = manager[options["connection"]]
        cursor = conn.cursor()
        cursor.execute( self.__do_subs(options["retrieve_sql"], *args, **kwargs)  )  
        data = self._cleandata(cursor)
        df = DataFrame(data)
        #df.append([row for row in cursor])
        df.columns = list(cursor.column_names)

        for c in df.columns:
            if type(df[c][0]) is decimal.Decimal:
                df[c] = df[c].astype(float)
        return df

    def _cleandata(self, cursor):
        v = cursor.fetchall()
        if [ type(x) == bytearray for x in v[0]]:
            output = []
            for row in v:
                newRow = []
                for col in row:
                    if type(col) is bytearray:
                        newRow.append(col.decode())
                    else:
                        newRow.append(col)
                output.append(newRow)
            return output
        else:
            return v

    def update(self, update_values: List[Dict[str, typing.Any]],
               original_values: List[Dict[str, typing.Any]] = None,*args,**kwargs) -> DataFrame:
        pass

    def delete(self, to_delete: List,*args,**kwargs) -> bool:
        pass

    def __do_subs(self, sql, *args, **kwargs):
       return sql

class MySQLTableSource(SourceBase):
    def create(self, objs_to_create: List[Dict[str, typing.Any]],*args, **kwargs) -> DataFrame:
        pass

    def retrieve(self, *args, **kwargs) -> List[Dict[str, typing.Any]]:
        pass

    def update(self, update_values: List[Dict[str, typing.Any]],
               original_values: List[Dict[str, typing.Any]] = None,*args,**kwargs) -> DataFrame:
        pass

    def delete(self, to_delete: List,*args,**kwargs) -> bool:
        pass
