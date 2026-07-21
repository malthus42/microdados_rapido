import duckdb
from .loader import LoaderMixin
from .query import QueryMixin


class MicrodadosRapido(
    LoaderMixin,
    QueryMixin
):

    def __init__(self, connection=None):
        self.con = (
            connection
            if connection is not None
            else duckdb.connect()
        )

    def close(self):
        self.con.close()
        