# Microdados Rápido

`microdados_rapido` é um pacote Python para carregar e consultar arquivos grandes, com foco nos microdados do ENEM.

O pacote utiliza DuckDB para converter arquivos CSV em Parquet e permite executar consultas SQL sem carregar todo o conjunto de dados diretamente na memória.

## Instalação

Instale diretamente pelo GitHub:

```bash
python3 -m pip install git+https://github.com/malthus42/microdados_rapido.git
```

Para atualizar o pacote:

```bash
python3 -m pip install --upgrade git+https://github.com/malthus42/microdados_rapido.git
```

Também é possível instalar localmente:

```bash
git clone https://github.com/malthus42/microdados_rapido.git
cd microdados_rapido
python3 -m pip install .
```

## Importação

```python
from microdados_rapido import MicrodadosRapido
```

## Carregando os microdados do ENEM

Faça o download dos microdados no portal do INEP e informe o caminho do arquivo CSV:

```python
from microdados_rapido import MicrodadosRapido

enem = MicrodadosRapido()

enem.load_table(
    path="MICRODADOS_ENEM_2023.csv",
    table_name="enem_2023"
)
```

Na primeira execução, o arquivo CSV será convertido automaticamente para Parquet:

```text
MICRODADOS_ENEM_2023.csv
MICRODADOS_ENEM_2023.parquet
```

Nas próximas execuções, o arquivo Parquet existente será reutilizado.

## Consultando uma prova do ENEM

Exemplo de consulta para selecionar participantes de uma determinada prova e área:

```python
area = "MT"
codigo_prova = 1211
nota_minima = 0
redacao_minima = 0
table_name = "enem_2023"

sql = f"""
    SELECT
        NU_INSCRICAO,
        Q006,
        TX_GABARITO_{area},
        TX_RESPOSTAS_{area},
        TRY_CAST(NU_NOTA_{area} AS DOUBLE) AS NU_NOTA_{area}
    FROM {table_name}
    WHERE
        TRY_CAST(CO_PROVA_{area} AS INTEGER) = {codigo_prova}
        AND TRY_CAST(NU_NOTA_{area} AS DOUBLE) > {nota_minima}
        AND TRY_CAST(NU_NOTA_REDACAO AS DOUBLE) > {redacao_minima}
"""

df = enem.query(sql)

print(df.head())
```

Nesse exemplo:

* `area` indica a área da prova;
* `codigo_prova` identifica o caderno;
* `nota_minima` define a nota mínima na área;
* `redacao_minima` define a nota mínima na redação.

Áreas utilizadas nos microdados:

```text
LC - Linguagens e Códigos
CH - Ciências Humanas
CN - Ciências da Natureza
MT - Matemática
```

## Exportando o resultado

O resultado de uma consulta pode ser salvo diretamente em CSV:

```python
enem.query_into_csv(
    sql=sql,
    output_path="dados_processados/enem_2023_mt_1211.csv"
)
```

O diretório será criado caso ainda não exista.

O arquivo gerado utiliza `;` como separador.

## Listando tabelas carregadas

```python
print(enem.list_tables())
```

## Exemplo completo

```python
from microdados_rapido import MicrodadosRapido

enem = MicrodadosRapido()

enem.load_table(
    "MICRODADOS_ENEM_2023.csv",
    "enem_2023"
)

area = "LC"
codigo_prova = 1201

sql = f"""
    SELECT
        NU_INSCRICAO,
        Q006,
        TX_GABARITO_{area},
        TX_RESPOSTAS_{area},
        TRY_CAST(NU_NOTA_{area} AS DOUBLE) AS NU_NOTA_{area}
    FROM enem_2023
    WHERE
        TRY_CAST(CO_PROVA_{area} AS INTEGER) = {codigo_prova}
        AND TRY_CAST(NU_NOTA_{area} AS DOUBLE) > 0
        AND TRY_CAST(NU_NOTA_REDACAO AS DOUBLE) > 0
"""

df = enem.query(sql)

print(df.head())
print(f"Quantidade de participantes: {len(df)}")

enem.query_into_csv(
    sql,
    "dados_processados/enem_2023_lc_1201.csv"
)

enem.close()
```

## Estrutura do projeto

```text
.
├── README.md
├── microdados_rapido
│   ├── __init__.py
│   ├── core.py
│   ├── loader.py
│   └── query.py
├── poetry.lock
└── pyproject.toml
```

## Métodos principais

### `load_table(path, table_name)`

Carrega um arquivo CSV, converte para Parquet quando necessário e cria uma view no DuckDB.

### `query(sql)`

Executa uma consulta SQL e retorna um `DataFrame` do pandas.

### `query_into_csv(sql, output_path)`

Executa uma consulta e salva o resultado diretamente em um arquivo CSV.

### `list_tables()`

Lista as tabelas e views disponíveis.

### `close()`

Encerra a conexão com o DuckDB.

## Observação

Caso o arquivo CSV original seja alterado depois da conversão, exclua o arquivo Parquet antigo para que ele seja gerado novamente:

```bash
rm MICRODADOS_ENEM_2023.parquet
```

## Autor

Desenvolvido por Matheus Silva Lopes da Costa.
