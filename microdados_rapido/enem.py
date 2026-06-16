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
    
    def balancear_grupos(
    self,
    df,
    group_mapping,
    coluna_origem="Q006",
    coluna_grupo="grupo_label",
    random_state=42
):
        df = df.copy()
        df[coluna_grupo] = df[coluna_origem].map(group_mapping)

        df = df.dropna(subset=[coluna_grupo])

        contagens = df[coluna_grupo].value_counts()

        if len(contagens) < 2:
            raise ValueError(
                "É necessário ter pelo menos dois grupos após o mapeamento."
            )

        tamanho_minimo = contagens.min()

        df_balanceado = (
            df.groupby(coluna_grupo, group_keys=False)
            .apply(
                lambda grupo: grupo.sample(
                    n=tamanho_minimo,
                    random_state=random_state,
                    replace=False
                )
            )
            .reset_index(drop=True)
        )

        return df_balanceado
    
    def matriz_respostas(
    self, 
    df, 
    area, 
    numero_inicial=0, 
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

        matriz_binaria["ESCORE_TOTAL"] = (
        matriz_binaria[item_cols]
        .sum(axis=1)
        )

        return matriz_binaria
    
    def preparar_dados_psicometricos(
    self,
    df,
    area,
    group_mapping,
    numero_inicial=0,
    n_itens=45,
    offset_resposta=0,
    offset_gabarito=0,
    coluna_origem_grupo="Q006",
    coluna_grupo="grupo_label",
    random_state=42
):
        df_balanceado = self.balancear_grupos(
            df=df,
            group_mapping=group_mapping,
            coluna_origem=coluna_origem_grupo,
            coluna_grupo=coluna_grupo,
            random_state=random_state
        )

        matriz = self.matriz_respostas(
            df=df_balanceado,
            area=area,
            numero_inicial=numero_inicial,
            n_itens=n_itens,
            offset_resposta=offset_resposta,
            offset_gabarito=offset_gabarito
        )

        df_balanceado = df_balanceado.reset_index(drop=True)
        matriz = matriz.reset_index(drop=True)

        df_final = pd.concat(
            [df_balanceado, matriz],
            axis=1
        )

        return df_final