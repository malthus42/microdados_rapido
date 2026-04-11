import os
import duckdb
import pandas as pd

class MicrodadosRapido:
    def __init__(self, parquet_path, name="data"):
        self.parquet_path = parquet_path
        self.con = duckdb.connect()
        self.con.execute(f"""
            CREATE OR REPLACE VIEW {name} AS
            SELECT * FROM '{self.parquet_path}'
        """)

    def query(self, sql):  
        return self.con.execute(sql).df()

    def df(self):
        return self.con.execute(
            f"SELECT * FROM '{self.parquet_path}'"
        ).df()
    
    @staticmethod
    def read_csv(path, name="data"):
        parquet_path = path.replace(".csv", ".parquet")
        con = duckdb.connect()

        if not os.path.exists(parquet_path):
            con.execute(f"""
                COPY (
                    SELECT * FROM read_csv_auto(
                        '{path}',
                        delim=';',
                        header=True,
                        encoding='utf-8',
                        SAMPLE_SIZE=-1,
                        ignore_errors=true,
                        all_varchar=true
                    )
                )
                TO '{parquet_path}'
                (FORMAT PARQUET, COMPRESSION 'ZSTD');
            """)
        return MicrodadosRapido(parquet_path, name)
