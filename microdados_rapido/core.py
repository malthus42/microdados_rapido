import duckdb
import pandas as pd
from pathlib import Path

class MicrodadosRapido:
    def __init__(self, connection=None):
        self.con = connection if connection else duckdb.connect()

    def add_table(self, path, table_name):
        path = Path(path)
        
        if path.suffix.lower() != '.csv':
            raise ValueError(f"Formato inválido: '{path.suffix}'. Esta biblioteca aceita apenas arquivos .csv")
        
        parquet_path = self._csv_to_parquet(path)
        
        self.con.execute(f"""
            CREATE OR REPLACE VIEW {table_name} AS 
            SELECT * FROM '{parquet_path.as_posix()}'
        """)
        return self

    def _csv_to_parquet(self, csv_path):
        parquet_path = csv_path.with_suffix('.parquet')
        if not parquet_path.exists():
            self.con.execute(f"""
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
        return parquet_path

    def to_csv(self, sql, output_path):
        """Executa uma query e salva o resultado diretamente em um arquivo CSV."""
        path = Path(output_path).as_posix()
        self.con.execute(f"COPY ({sql}) TO '{path}' (HEADER, DELIMITER ';')")
        return self

    def query(self, sql):  
        return self.con.execute(sql).df()

    def list_tables(self):
        return self.con.execute("SHOW TABLES").df()