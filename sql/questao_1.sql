-- Questão 1.1 — EDA da tabela orders, sem limpeza ou tratamento.
SET search_path TO lh_nautical, public;

SELECT
    COUNT(*) AS total_linhas,
    (SELECT COUNT(*)
     FROM information_schema.columns
     WHERE table_schema = 'lh_nautical' AND table_name = 'orders') AS total_colunas,
    MIN(created_at) AS data_minima_created_at,
    MAX(created_at) AS data_maxima_created_at,
    MIN(total) AS valor_minimo,
    MAX(total) AS valor_maximo,
    AVG(total) AS valor_medio
FROM orders;

-- Qualidade observável, sem alterar a tabela.
SELECT
    COUNT(*) FILTER (WHERE total IS NULL) AS nulos_total,
    COUNT(*) FILTER (WHERE total < 0) AS negativos_total,
    COUNT(*) FILTER (WHERE created_at IS NULL) AS nulos_created_at,
    COUNT(*) FILTER (WHERE total <> total) AS valores_nao_finitos_total
FROM orders;

-- Sinalização descritiva de outliers por IQR.
WITH quartis AS (
    SELECT
        percentile_cont(0.25) WITHIN GROUP (ORDER BY total) AS q1,
        percentile_cont(0.75) WITHIN GROUP (ORDER BY total) AS q3
    FROM orders
    WHERE total IS NOT NULL
), limites AS (
    SELECT q1, q3, q1 - 1.5 * (q3 - q1) AS limite_inferior, q3 + 1.5 * (q3 - q1) AS limite_superior
    FROM quartis
)
SELECT COUNT(*) AS quantidade_sinalizada, MIN(limite_inferior) AS limite_inferior, MAX(limite_superior) AS limite_superior
FROM orders CROSS JOIN limites
WHERE orders.total < limites.limite_inferior OR orders.total > limites.limite_superior;
