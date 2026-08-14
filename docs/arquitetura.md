# Arquitetura e decisões técnicas

## Visão geral

A solução usa PostgreSQL como camada persistente e Streamlit como camada de apresentação. O banco mantém o schema `lh_nautical`, enquanto o dashboard consulta views analíticas para reduzir duplicação de lógica e tornar as métricas reproduzíveis.

| Camada | Tecnologia | Responsabilidade |
|---|---|---|
| Persistência | PostgreSQL 16 | Tabelas relacionais, constraints e índices. |
| Inicialização | Docker Compose | Rede, volume persistente, healthcheck e montagem dos scripts. |
| Análise | SQL + pandas | Agregações, nulos e sinalização exploratória de outliers. |
| Apresentação | Streamlit + Plotly | KPIs, gráficos e tabela de qualidade. |

## Princípio de não tratamento

O enunciado exige que a Questão 1 use somente `orders` e não faça limpeza. A aplicação segue essa regra: não preenche nulos, não converte valores para corrigir inconsistências e não remove outliers. A regra IQR serve somente para sinalização visual e deve ser interpretada como hipótese de investigação.

## Dados não fornecidos

O arquivo recebido continha o PDF do desafio e um relatório técnico, mas não continha a pasta `lh_nautical_csv/` nem os 24 CSVs mencionados no enunciado. O banco inicia vazio de propósito. Assim que os arquivos reais forem adicionados, a carga deve ser executada e o painel passará a apresentar os resultados observados.

## Segurança e operação

As credenciais padrão existem apenas para desenvolvimento local. Em ambiente real, devem ser substituídas por secrets e não versionadas. O volume `postgres_data` mantém a base entre reinicializações; para uma carga limpa, use `docker compose down -v`.
