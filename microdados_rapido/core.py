import os
import duckdb
import pandas as pd
from pathlib import Path

class MicrodadosRapido:
    def __init__(self, parquet_path, name="data"):
        self.parquet_path = Path(parquet_path)
        self.con = duckdb.connect()
        self.con.execute(f"""
            CREATE OR REPLACE VIEW {name} AS
            SELECT * FROM '{self.parquet_path.as_posix()}'
        """)

    def query(self, sql):  
        return self.con.execute(sql).df()

    def df(self):
        return self.con.execute(
            f"SELECT * FROM '{self.parquet_path.as_posix()}'"
        ).df()
    
    @staticmethod
    def read_csv(path, name="data"):
        csv_path = Path(path)
        parquet_path = csv_path.with_suffix('.parquet')

        con = duckdb.connect()

        if not parquet_path.exists():
            con.execute(f"""
                COPY (
                    SELECT * FROM read_csv_auto(
                        '{csv_path.as_posix()}',
                        delim=';',
                        header=True,
                        encoding='utf-8',
                        SAMPLE_SIZE=-1,
                        ignore_errors=true,
                        all_varchar=true
                    )
                )
                TO '{parquet_path.as_posix()}'
                (FORMAT PARQUET, COMPRESSION 'ZSTD');
            """)

        return MicrodadosRapido(parquet_path, name)