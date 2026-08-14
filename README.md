# LH Nautical Analytics Dashboard

Dashboard analítico em **Python + Streamlit**, com **MySQL em Docker**, baseado nos 24 CSVs reais fornecidos para o desafio.

## Execução

```bash
docker compose up --build
```

Acesse `http://localhost:8501`. O MySQL fica disponível em `localhost:3306` com banco `lh_nautical`, usuário `lighthouse` e senha `lighthouse`.

Para criar as tabelas e carregar os dados reais:

```bash
docker compose exec dashboard python /scripts/ingest.py
```

Em execução local fora do container:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r app/requirements.txt
export DATA_DIR=./dados
export DATABASE_URL=mysql+pymysql://lighthouse:lighthouse@localhost:3306/lh_nautical
python scripts/ingest.py
streamlit run app/app.py
```

## Camadas de dados

A camada **raw** preserva cada linha dos CSVs em `raw_csv_rows.payload`, sem limpeza, imputação ou remoção de outliers. Ela é a fonte exclusiva da seção EDA. A camada **treated** remove duplicidades exatas, converte datas e campos numéricos com coerção explícita e preserva nulos semanticamente válidos. Ela alimenta Vendas, Clientes, Previsão e Recomendações.

## Navegação

A barra lateral contém exatamente as seções **EDA**, **Tratamento**, **Vendas**, **Clientes**, **Previsão** e **Recomendações**.

| Seção | Conteúdo |
|---|---|
| EDA | Linhas, colunas, datas, estatísticas de `total`, nulos e outliers IQR na camada raw. |
| Tratamento | Nulos, duplicidades, decisões de limpeza e comparação raw/treated. |
| Vendas | Receita mensal, ticket, canais, produtos e Questão 4 — prejuízos por produto. |
| Clientes | Questão 5 — lucro acumulado, PF/PJ, recompra e geografia. |
| Previsão | Questão 6 relacionada à demanda diária e projeção de 30 dias por média móvel + tendência linear. |
| Recomendações | Coocorrência de produtos e sugestão de próxima compra por cliente. |

## Observações metodológicas

A margem de produto é estimada como `line_total - quantity * cost_price`. O ranking de prejuízos considera apenas produtos com margem agregada negativa. A taxa de recompra considera clientes com mais de um pedido. A previsão preenche dias sem pedidos com zero antes de calcular a média móvel, evitando superestimar a demanda.

Nenhuma recomendação é inventada: produtos e clientes são derivados dos CSVs reais. O método de recomendação é deliberadamente transparente, usando frequência de coocorrência no mesmo pedido e frequência histórica por cliente.
