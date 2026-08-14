# Questão 1 — Análise exploratória da tabela `orders`

## Escopo

A análise deve usar exclusivamente a tabela `orders`, sem limpeza, imputação, remoção de duplicidades ou tratamento de outliers. O dashboard implementado reproduz essa premissa e apresenta as métricas diretamente do PostgreSQL.

## Métricas solicitadas

| Item | Consulta |
|---|---|
| Quantidade total de linhas | `COUNT(*)` |
| Quantidade total de colunas | Catálogo `information_schema.columns` |
| Intervalo de datas | `MIN(created_at)` e `MAX(created_at)` |
| Total mínimo | `MIN(total)` |
| Total máximo | `MAX(total)` |
| Total médio | `AVG(total)` |

A consulta auditável está em `sql/questao_1.sql`. A quantidade de colunas prevista pelo DDL do relatório técnico é **17**.

## Diagnóstico

Como os CSVs não estavam presentes no arquivo enviado, não é possível emitir um diagnóstico factual sobre volume, outliers ou nulos da base real sem inventar dados. O dashboard, portanto, inicia com estado vazio e informa essa limitação ao usuário.

Após a carga dos CSVs, o diagnóstico deve considerar três aspectos. Primeiro, valores nulos em `total` ou `created_at` reduzem a confiabilidade das métricas e exigem tratamento documentado. Segundo, valores negativos ou muito extremos em `total` devem ser investigados como possíveis estornos, erros de origem ou eventos válidos de negócio. Terceiro, a presença de valores sinalizados pelo intervalo interquartil não significa, isoladamente, que os registros sejam inválidos.

A recomendação é considerar a tabela **não pronta para análises decisórias** enquanto os nulos, inconsistências de domínio, duplicidades e outliers não forem revisados com as áreas responsáveis. A etapa de EDA, entretanto, pode ser executada sobre os dados brutos justamente para localizar esses problemas.
