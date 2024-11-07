from app.utils.queries import Queriable,Query
from duckdb import DuckDBPyConnection,connect

class TableManager():
    def __init__(self,connection:DuckDBPyConnection,entity:type) -> None:
        if not issubclass(entity,Queriable):
            raise TypeError
        self.prototype = entity
        self.table_name = entity.__name__
        self.schema = self.prototype().schema.copy()
        self.connection=connection
        self.table:DuckDBPyConnection=None
        with connection.cursor() as con:
            try:
                self.table=con.table(table_name=self.table_name)
            except Exception:
                table_generator=(f"{k} {v.SQLType()}" for k,v in self.schema.items())
                values = ",".join(table_generator)
                self.table=con.sql(f"CREATE TABLE {self.table_name} ({values});")
                
    def execute(self,query:Query|str)->list[Queriable]:
        with self.table.cursor() as cur:
            res=cur.sql(query=str(query))
            columns=res.columns
            values=res.fetchall()
        list_to_return=[self.prototype().setValues(dict([(columns[i],v) for i,v in enumerate(val)])) for val in values]
        return list_to_return
