import os
from datetime import date

import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

st.set_page_config(page_title="Lighthouse | EDA Orders", page_icon="📊", layout="wide")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@localhost:5432/lh_nautical_dw",
)

@st.cache_resource
def get_engine():
    return create_engine(DATABASE_URL, pool_pre_ping=True)

@st.cache_data(ttl=30)
def query_df(sql: str) -> pd.DataFrame:
    with get_engine().connect() as conn:
        return pd.read_sql(text(sql), conn)


def safe_query(sql: str) -> pd.DataFrame | None:
    try:
        return query_df(sql)
    except SQLAlchemyError as exc:
        st.error(f"Não foi possível consultar o banco: {exc}")
        return None

st.title("Dashboard de Qualidade — LH Nautical")
st.caption("Questão 1 · Análise exploratória bruta da tabela orders")

with st.sidebar:
    st.header("Filtros da visualização")
    st.write("As métricas principais seguem a premissa do desafio e usam toda a tabela `orders`, sem limpeza.")
    if st.button("Atualizar dados"):
        st.cache_data.clear()
        st.rerun()

try:
    health = safe_query("SELECT current_database() AS database, current_schema() AS schema")
except Exception:
    health = None

summary = safe_query("""
    SELECT total_rows, min_created_at, max_created_at, min_total, max_total,
           avg_total, null_total, negative_total
    FROM lh_nautical.v_orders_eda
""")

if summary is None:
    st.stop()

row = summary.iloc[0]
rows = int(row["total_rows"] or 0)

if rows == 0:
    st.warning("A tabela `orders` está vazia. Coloque os CSVs reais em `dados/` e execute o script de importação para habilitar as análises.")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Linhas em orders", f"{rows:,}".replace(",", "."))
m2.metric("Colunas", "17")
min_date = pd.to_datetime(row["min_created_at"]).strftime("%d/%m/%Y") if pd.notna(row["min_created_at"]) else "—"
max_date = pd.to_datetime(row["max_created_at"]).strftime("%d/%m/%Y") if pd.notna(row["max_created_at"]) else "—"
m3.metric("Data mínima", min_date)
m4.metric("Data máxima", max_date)

st.divider()

k1, k2, k3 = st.columns(3)
def money(value):
    return "—" if pd.isna(value) else f"R$ {float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
k1.metric("Total mínimo", money(row["min_total"]))
k2.metric("Total máximo", money(row["max_total"]))
k3.metric("Total médio", money(row["avg_total"]))

st.subheader("Diagnóstico de confiabilidade")
null_count = int(row["null_total"] or 0)
negative_count = int(row["negative_total"] or 0)
diagnosis = []
if rows == 0:
    diagnosis.append("A base ainda não contém registros; não é possível concluir sobre a confiabilidade até a carga dos CSVs.")
else:
    diagnosis.append(f"A tabela contém {rows:,} registros observáveis sem transformação aplicada.".replace(",", "."))
    if null_count:
        diagnosis.append(f"Foram encontrados {null_count:,} valores nulos em `total`; a base exige tratamento antes de análises financeiras.".replace(",", "."))
    else:
        diagnosis.append("Não foram encontrados valores nulos em `total`.")
    if negative_count:
        diagnosis.append(f"Há {negative_count:,} valores negativos em `total`, que devem ser investigados como possível inconsistência ou estorno.".replace(",", "."))
    else:
        diagnosis.append("Não foram encontrados valores negativos em `total`.")
    diagnosis.append("Valores extremos não são automaticamente erros; o painel os sinaliza para investigação por IQR, sem removê-los.")
for item in diagnosis:
    st.write(item)

st.subheader("Distribuição do valor total")
orders = safe_query("SELECT id, created_at, channel, status, total FROM lh_nautical.orders")
if orders is not None and not orders.empty:
    orders["total"] = pd.to_numeric(orders["total"], errors="coerce")
    q1 = orders["total"].quantile(0.25)
    q3 = orders["total"].quantile(0.75)
    iqr = q3 - q1
    lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    orders["outlier_iqr"] = (orders["total"] < lower) | (orders["total"] > upper)
    c1, c2 = st.columns([2, 1])
    with c1:
        fig = px.histogram(orders, x="total", nbins=40, title="Histograma de orders.total", labels={"total": "Valor total"})
        fig.update_layout(height=360, margin=dict(l=20, r=20, t=55, b=20))
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.metric("Registros sinalizados por IQR", f"{int(orders['outlier_iqr'].sum()):,}".replace(",", "."))
        st.caption(f"Limite inferior: {money(lower)} · Limite superior: {money(upper)}")
        st.dataframe(orders.loc[orders["outlier_iqr"], ["id", "created_at", "channel", "total"]].head(20), use_container_width=True, hide_index=True)
else:
    st.info("Sem dados para gerar a distribuição.")

left, right = st.columns(2)
monthly = safe_query("SELECT * FROM lh_nautical.v_orders_by_month")
channels = safe_query("SELECT * FROM lh_nautical.v_orders_by_channel")
with left:
    st.subheader("Evolução mensal")
    if monthly is not None and not monthly.empty:
        fig = px.line(monthly, x="month", y="total_sales", markers=True, labels={"month": "Mês", "total_sales": "Vendas"})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sem dados mensais.")
with right:
    st.subheader("Pedidos por canal")
    if channels is not None and not channels.empty:
        fig = px.bar(channels, x="channel", y="orders_count", color="channel", labels={"channel": "Canal", "orders_count": "Pedidos"})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sem dados por canal.")

st.subheader("Qualidade por coluna")
nulls = safe_query("SELECT column_name, null_count, total_rows, ROUND(100.0 * null_count / NULLIF(total_rows, 0), 2) AS null_pct FROM lh_nautical.v_orders_nulls ORDER BY null_pct DESC, column_name")
if nulls is not None:
    st.dataframe(nulls, use_container_width=True, hide_index=True)

with st.expander("SQL da Questão 1"):
    st.code("""SELECT COUNT(*) AS total_rows, MIN(created_at) AS min_created_at, MAX(created_at) AS max_created_at, MIN(total) AS min_total, MAX(total) AS max_total, AVG(total) AS avg_total FROM lh_nautical.orders;""", language="sql")

st.caption("O painel observa os dados brutos. Nenhuma limpeza, imputação ou remoção de outliers é aplicada automaticamente.")
