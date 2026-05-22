from pathlib import Path

class ENEMMixin:

    def carregar_enem(self, ano, path=None):
        tabela = f"enem_{ano}"

        if path is None:
            path = f"../microdados/{ano}/DADOS/MICRODADOS_ENEM_{ano}.csv"

        self.add_table(path, tabela)

        return tabela

    def respostas_prova(
        self,
        ano,
        area,
        codigo_prova,
        tabela=None,
        nota_minima=0,
        redacao_minima=0
    ):

        if tabela is None:
            tabela = f"enem_{ano}"

        query = f"""
        SELECT
            NU_INSCRICAO,
            Q006,
            TX_GABARITO_{area},
            TX_RESPOSTAS_{area},
            NU_NOTA_{area}
        FROM
            {tabela}
        WHERE
            CO_PROVA_{area} = '{codigo_prova}'
            AND NU_NOTA_{area}::FLOAT > {nota_minima}
            AND NU_NOTA_REDACAO::FLOAT > {redacao_minima}
        """

        return self.query(query)