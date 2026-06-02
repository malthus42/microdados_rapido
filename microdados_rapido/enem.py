from pathlib import Path
import numpy as np
import pandas as pd

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
    
    def matriz_respostas(
    self, 
    df, 
    area, 
    numero_inicial, 
    n_itens=45, 
    offset_resposta=0, 
    offset_gabarito=0
    ):

        respostas_col = f"TX_RESPOSTAS_{area}"
        gabarito_col = f"TX_GABARITO_{area}"

        if df.empty:
            raise ValueError("DataFrame vazio.")

        gabarito_base = df[gabarito_col].iloc[0]

        respostas_base = df[respostas_col].astype(str)

        matriz_binaria = pd.DataFrame(index=df.index)

        item_cols = []

        for i in range(n_itens):

            numero_questao = numero_inicial + i

            item_id = f"{area}_Item_{numero_questao}"

            item_cols.append(item_id)

            coluna_resposta = respostas_base.str[i + offset_resposta]

            gabarito_char = gabarito_base[i + offset_gabarito]

            is_correct = coluna_resposta == gabarito_char

            is_valid = coluna_resposta.isin(
                ['A', 'B', 'C', 'D', 'E']
            )

            matriz_binaria[item_id] = np.where(
                is_valid,
                is_correct.astype(int),
                np.nan
            )

        return matriz_binaria