from pathlib import Path


class LoaderMixin:

    def load_table(self, path, table_name):
        path = Path(path).expanduser().resolve()

        if not path.exists():
            raise FileNotFoundError(
                f"Arquivo não encontrado: {path}"
            )

        if path.suffix.lower() != ".csv":
            raise ValueError(
                f"Formato inválido: '{path.suffix}'. "
                "Esta biblioteca aceita apenas arquivos CSV."
            )

        parquet_path = self._csv_to_parquet(path)

        self.con.execute(
            f"""
            CREATE OR REPLACE VIEW {table_name} AS
            SELECT *
            FROM read_parquet('{parquet_path.as_posix()}')
            """
        )

        return self

    def _csv_to_parquet(self, csv_path):
        parquet_path = csv_path.with_suffix(".parquet")

        if not parquet_path.exists():
            self.con.execute(
                f"""
                COPY (
                    SELECT *
                    FROM read_csv_auto(
                        '{csv_path.as_posix()}',
                        delim=';',
                        header=true,
                        encoding='utf-8',
                        sample_size=-1,
                        ignore_errors=true,
                        all_varchar=true
                    )
                )
                TO '{parquet_path.as_posix()}'
                (
                    FORMAT PARQUET,
                    COMPRESSION ZSTD
                )
                """
            )

        return parquet_path