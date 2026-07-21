from pathlib import Path


class QueryMixin:

    def query(self, sql):
        return self.con.execute(sql).df()

    def query_into_csv(self, sql, output_path):
        path = Path(output_path).expanduser().resolve()

        path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self.con.execute(
            f"""
            COPY ({sql})
            TO '{path.as_posix()}'
            (
                HEADER,
                DELIMITER ';'
            )
            """
        )

        return self

    def list_tables(self):
        return self.con.execute("SHOW TABLES").df()