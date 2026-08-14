import os
from pathlib import Path
from itertools import combinations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title='LH Nautical | Analytics Blueprint', page_icon='◈', layout='wide', initial_sidebar_state='expanded')
DATA_DIR = Path(os.getenv('DATA_DIR', Path(__file__).resolve().parents[1] / 'dados'))

st.markdown('''
<style>
:root { --blueprint:#071a44; --blueprint-2:#0d2c68; --line:rgba(164,205,255,.28); --cyan:#65d9ff; --ink:#e7f3ff; --muted:#9db9dd; }
.stApp { background-color:var(--blueprint); background-image:linear-gradient(rgba(101,217,255,.055) 1px,transparent 1px),linear-gradient(90deg,rgba(101,217,255,.055) 1px,transparent 1px),linear-gradient(rgba(255,255,255,.035) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.035) 1px,transparent 1px); background-size:40px 40px,40px 40px,8px 8px,8px 8px; color:var(--ink); }
section[data-testid='stSidebar'] { background:#061536; border-right:1px solid var(--line); }
section[data-testid='stSidebar'] * { color:var(--ink)!important; }
.block-container { padding-top:2rem; max-width:1500px; }
.blueprint-title { border:1px solid var(--line); padding:22px 26px; position:relative; background:linear-gradient(135deg,rgba(13,44,104,.75),rgba(7,26,68,.55)); box-shadow:0 0 0 6px rgba(101,217,255,.025), inset 0 0 40px rgba(101,217,255,.04); }
.blueprint-title:before,.blueprint-title:after { content:''; position:absolute; width:28px; height:28px; border-color:var(--cyan); border-style:solid; }
.blueprint-title:before { top:-1px; left:-1px; border-width:2px 0 0 2px; }.blueprint-title:after { bottom:-1px; right:-1px; border-width:0 2px 2px 0; }
.blueprint-title h1 { font-size:2.2rem; letter-spacing:.08em; margin:0; color:#fff; }.eyebrow { font-size:.7rem; letter-spacing:.24em; color:var(--cyan); font-weight:700; text-transform:uppercase; }
.metric-card { border:1px solid var(--line); padding:16px; min-height:108px; background:rgba(13,44,104,.48); position:relative; }.metric-card:after { content:'+'; position:absolute; right:10px; top:7px; color:var(--cyan); opacity:.55; }.metric-label { color:var(--muted); font-size:.74rem; text-transform:uppercase; letter-spacing:.12em; }.metric-value { color:#fff; font-size:1.55rem; font-weight:800; margin-top:8px; }.section-label { color:var(--cyan); letter-spacing:.17em; text-transform:uppercase; font-size:.75rem; font-weight:800; border-bottom:1px solid var(--line); padding-bottom:10px; margin:24px 0 14px; }
[data-testid='stMetric'] { background:rgba(13,44,104,.48); border:1px solid var(--line); padding:10px; }.stDataFrame { border:1px solid var(--line); }.stTabs [data-baseweb='tab-list'] { gap:8px; }.stTabs [data-baseweb='tab'] { border:1px solid var(--line); background:rgba(13,44,104,.3); padding:8px 16px; }.stTabs [aria-selected='true'] { background:var(--blueprint-2); color:var(--cyan); }
</style>
''', unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def load_raw():
    return {p.stem: pd.read_csv(p, low_memory=False) for p in DATA_DIR.glob('*.csv')}

@st.cache_data(show_spinner=False)
def load_treated():
    raw = load_raw()
    treated = {k: v.drop_duplicates().copy() for k, v in raw.items()}
    for name, df in treated.items():
        for col in df.columns:
            if col.endswith('_at') or col.endswith('_date') or col in {'placed_at','paid_at','issued_at','received_at'}:
                df[col] = pd.to_datetime(df[col], errors='coerce')
            if col in {'subtotal','discount_amount','total','quantity','unit_price','line_total','sale_price','cost_price','weight_kg','total_refund_amount','amount'}:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        treated[name] = df
    return treated

raw = load_raw(); data = load_treated()
orders = data.get('orders', pd.DataFrame()); items = data.get('order_items', pd.DataFrame()); products = data.get('products', pd.DataFrame()); variants = data.get('product_variants', pd.DataFrame()); customers = data.get('customers', pd.DataFrame()); addresses = data.get('addresses', pd.DataFrame()); returns = data.get('returns', pd.DataFrame())

with st.sidebar:
    st.markdown('<div class="eyebrow">LH NAUTICAL / CONTROL ROOM</div>', unsafe_allow_html=True)
    st.markdown('## Navegação')
    page = st.radio('Seções', ['EDA','Tratamento','Vendas','Clientes','Previsão','Recomendações'], label_visibility='collapsed')
    st.divider(); st.caption(f'{len(raw)} CSVs carregados · {len(orders):,} pedidos'.replace(',', '.'))

st.markdown('<div class="blueprint-title"><div class="eyebrow">ANALYTICS BLUEPRINT · E-COMMERCE</div><h1>LH NAUTICAL / DATA COMMAND</h1><div style="color:#9db9dd;margin-top:8px">Painel técnico para diagnóstico, performance comercial e decisões de inventário.</div></div>', unsafe_allow_html=True)


def brl(v):
    if pd.isna(v): return '—'
    return f'R$ {float(v):,.2f}'.replace(',','X').replace('.',',').replace('X','.')

def metric(label, value, note=''):
    st.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div style="color:#9db9dd;font-size:.72rem;margin-top:5px">{note}</div></div>', unsafe_allow_html=True)

def chart_style(fig):
    fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(7,26,68,.35)', font_color='#e7f3ff', margin=dict(l=20,r=20,t=55,b=20), height=360)
    fig.update_xaxes(showgrid=True, gridcolor='rgba(164,205,255,.12)'); fig.update_yaxes(showgrid=True, gridcolor='rgba(164,205,255,.12)')
    return fig

def section(title, subtitle):
    st.markdown(f'<div class="section-label">{title}</div><div style="color:#9db9dd;margin-bottom:12px">{subtitle}</div>', unsafe_allow_html=True)

if page == 'EDA':
    section('01 / EDA BRUTA', 'A camada raw é observada sem correções, imputações ou remoção de outliers.')
    if orders.empty: st.error('orders.csv não encontrado ou vazio.')
    else:
        c=st.columns(5); [metric('Linhas',f'{len(orders):,}'.replace(',','.'), 'orders raw'), metric('Colunas',str(len(orders.columns)), 'contrato observado'), metric('Data mínima',orders.created_at.min().strftime('%d/%m/%Y'), 'created_at'), metric('Data máxima',orders.created_at.max().strftime('%d/%m/%Y'), 'created_at'), metric('Total médio',brl(orders.total.mean()), 'campo total')]
        section('ESTATÍSTICAS DE TOTAL','Amplitude, tendência central e regra IQR para sinalização exploratória.')
        st.dataframe(pd.DataFrame({'Métrica':['Mínimo','Máximo','Média','Mediana','Desvio padrão'], 'Valor':[brl(orders.total.min()),brl(orders.total.max()),brl(orders.total.mean()),brl(orders.total.median()),brl(orders.total.std())]}), use_container_width=True, hide_index=True)
        q1,q3=orders.total.quantile(.25),orders.total.quantile(.75); iqr=q3-q1; lower,upper=q1-1.5*iqr,q3+1.5*iqr; flagged=orders[(orders.total<lower)|(orders.total>upper)]
        a,b=st.columns([2,1]);
        with a: st.plotly_chart(chart_style(px.histogram(orders,x='total',nbins=50,title='Distribuição bruta de orders.total',labels={'total':'Valor do pedido'})), use_container_width=True)
        with b: metric('Sinalizados IQR',f'{len(flagged):,}'.replace(',','.'),f'limites {brl(lower)} / {brl(upper)}'); st.dataframe(flagged[['id','created_at','total']].head(20),use_container_width=True,hide_index=True)
        section('NULOS POR COLUNA','Valores ausentes na camada raw, sem interpretação automática.')
        nulls=orders.isna().sum().sort_values(ascending=False).reset_index(); nulls.columns=['coluna','nulos']; nulls['percentual']=nulls.nulos/len(orders)*100; st.dataframe(nulls,use_container_width=True,hide_index=True)

elif page == 'Tratamento':
    section('02 / TRATAMENTO','Comparação entre o arquivo raw e a camada treated usada nas análises.')
    rows=[]
    for name,df in raw.items():
        t=data[name]; rows.append({'tabela':name,'raw_linhas':len(df),'treated_linhas':len(t),'duplicados_removidos':len(df)-len(t),'nulos_raw':int(df.isna().sum().sum()),'nulos_treated':int(t.isna().sum().sum())})
    st.dataframe(pd.DataFrame(rows).sort_values('nulos_raw',ascending=False),use_container_width=True,hide_index=True)
    section('DECISÕES DE LIMPEZA','Regras aplicadas somente para a camada treated.')
    st.info('Datas são convertidas com errors=coerce; campos numéricos são convertidos para número; linhas duplicadas são removidas na camada treated; identificadores como CPF, CNPJ, EAN e telefone permanecem como texto; nulos semanticamente válidos são preservados.')
    a,b=st.columns(2)
    with a: st.plotly_chart(chart_style(px.bar(pd.DataFrame(rows).sort_values('nulos_raw',ascending=False).head(12),x='tabela',y='nulos_raw',title='Nulos por tabela raw')),use_container_width=True)
    with b: st.plotly_chart(chart_style(px.bar(pd.DataFrame(rows).sort_values('duplicados_removidos',ascending=False).head(12),x='tabela',y='duplicados_removidos',title='Duplicidades removidas na treated')),use_container_width=True)

elif page == 'Vendas':
    section('03 / VENDAS','Receita, ticket, canais, produtos e Questão 4 — prejuízos por produto.')
    revenue=orders.groupby(orders.created_at.dt.to_period('M').astype(str),dropna=False).agg(receita=('total','sum'),pedidos=('id','count'),ticket_medio=('total','mean')).reset_index().rename(columns={'created_at':'mes'})
    c=st.columns(4); [metric('Receita acumulada',brl(orders.total.sum())),metric('Pedidos',f'{len(orders):,}'.replace(',','.')),metric('Ticket médio',brl(orders.total.mean())),metric('Devoluções',f'{len(returns):,}'.replace(',','.'))]
    a,b=st.columns(2)
    with a: st.plotly_chart(chart_style(px.line(revenue,x='mes',y='receita',markers=True,title='Evolução mensal de receita',labels={'mes':'Mês','receita':'Receita'})),use_container_width=True)
    with b:
        ch=orders.groupby('channel',dropna=False).agg(receita=('total','sum'),pedidos=('id','count')).reset_index(); st.plotly_chart(chart_style(px.bar(ch,x='channel',y='receita',color='channel',title='Receita por canal')),use_container_width=True)
    section('PRODUTOS MAIS VENDIDOS','Ranking por quantidade e receita de itens.')
    prod=items.merge(variants[['id','product_id','cost_price']],left_on='product_variant_id',right_on='id',how='left',suffixes=('','_variant')).merge(products[['id','name']],left_on='product_id',right_on='id',how='left',suffixes=('','_product')); prod['profit']=prod['line_total']-(prod['quantity']*prod['cost_price']); ranked=prod.groupby('name',dropna=False).agg(unidades=('quantity','sum'),receita=('line_total','sum'),lucro=('profit','sum')).reset_index().sort_values('unidades',ascending=False)
    st.dataframe(ranked.head(20),use_container_width=True,hide_index=True)
    section('QUESTÃO 4 / PREJUÍZOS POR PRODUTO','Prejuízo agregado estimado quando custo dos itens supera a receita dos itens.')
    loss=ranked[ranked.lucro<0].sort_values('lucro'); st.plotly_chart(chart_style(px.bar(loss.head(20),x='lucro',y='name',orientation='h',title='Ranking de prejuízos por produto',labels={'lucro':'Prejuízo','name':'Produto'},color='lucro',color_continuous_scale='Blues')),use_container_width=True)

elif page == 'Clientes':
    section('04 / CLIENTES','Lucro acumulado, perfil PF/PJ, recompra e distribuição geográfica.')
    cust_orders=orders.groupby('customer_id').agg(pedidos=('id','count'),receita=('total','sum')).reset_index(); cust_orders['recompra']=cust_orders.pedidos>1; detail=cust_orders.merge(customers[['id','legal_name','person_type']],left_on='customer_id',right_on='id',how='left')
    c=st.columns(4); [metric('Clientes ativos em pedidos',f'{len(detail):,}'.replace(',','.')),metric('Taxa de recompra',f'{detail.recompra.mean()*100:.1f}%'),metric('Receita média/cliente',brl(detail.receita.mean())),metric('PF / PJ',f"{(customers.person_type=='PF').sum()} / {(customers.person_type=='PJ').sum()}")]
    section('QUESTÃO 5 / CLIENTES COM MAIOR LUCRO ACUMULADO','Lucro é atribuído pela margem dos itens comprados por cada cliente.')
    client_profit=orders[['id','customer_id']].merge(items[['order_id','product_variant_id','quantity','line_total']],left_on='id',right_on='order_id',how='left').merge(variants[['id','cost_price']],left_on='product_variant_id',right_on='id',how='left'); client_profit['lucro']=client_profit.line_total-(client_profit.quantity*client_profit.cost_price); cp=client_profit.groupby('customer_id',dropna=False).lucro.sum().reset_index().merge(customers[['id','legal_name','person_type']],left_on='customer_id',right_on='id',how='left').sort_values('lucro',ascending=False); st.plotly_chart(chart_style(px.bar(cp.head(20),x='lucro',y='legal_name',orientation='h',title='Top clientes por lucro acumulado',labels={'lucro':'Lucro acumulado','legal_name':'Cliente'})),use_container_width=True)
    a,b=st.columns(2)
    with a: st.plotly_chart(chart_style(px.pie(customers,names='person_type',title='Distribuição PF/PJ')),use_container_width=True)
    with b:
        geo=addresses.merge(customers[['id','person_type']],left_on='customer_id',right_on='id',how='left').groupby('state',dropna=False).size().reset_index(name='clientes'); st.plotly_chart(chart_style(px.bar(geo,x='state',y='clientes',title='Clientes por estado')),use_container_width=True)

elif page == 'Previsão':
    section('05 / PREVISÃO DE DEMANDA','Modelo transparente: média móvel de 7 dias + tendência linear sobre pedidos históricos.')
    daily=orders.assign(dia=orders.created_at.dt.floor('D')).groupby('dia').size().rename('pedidos').asfreq('D',fill_value=0).to_frame(); daily['media_movel_7d']=daily.pedidos.rolling(7,min_periods=1).mean(); y=daily.pedidos.values; x=np.arange(len(y)); slope,intercept=np.polyfit(x,y,1) if len(y)>1 else (0,float(y.mean()) if len(y) else 0); future_idx=np.arange(len(y),len(y)+30); future_dates=pd.date_range(daily.index.max()+pd.Timedelta(days=1),periods=30); forecast=np.maximum(0,(intercept+slope*future_idx + daily.pedidos.tail(7).mean())/2); fc=pd.DataFrame({'dia':future_dates,'pedidos_previstos':forecast})
    metric('Média prevista 30 dias',f'{fc.pedidos_previstos.mean():.1f}','pedidos/dia'); plot=pd.concat([daily.reset_index()[['dia','pedidos']].rename(columns={'pedidos':'valor'}).assign(tipo='Histórico'),fc.rename(columns={'pedidos_previstos':'valor'}).assign(tipo='Previsão')]); st.plotly_chart(chart_style(px.line(plot,x='dia',y='valor',color='tipo',title='Demanda histórica e projeção de 30 dias')),use_container_width=True); st.dataframe(fc,use_container_width=True,hide_index=True)

elif page == 'Recomendações':
    section('06 / RECOMENDAÇÕES','Regras simples e auditáveis, baseadas em coocorrência de produtos no mesmo pedido.')
    order_products=items.groupby('order_id').product_variant_id.apply(lambda s: sorted(set(s.dropna().astype(int)))).tolist(); pair_counts={}
    for basket in order_products:
        for a,b in combinations(basket,2): pair_counts[(a,b)]=pair_counts.get((a,b),0)+1
    pairs=pd.DataFrame([{'produto_a':a,'produto_b':b,'coocorrencias':n} for (a,b),n in pair_counts.items()]).sort_values('coocorrencias',ascending=False) if pair_counts else pd.DataFrame(columns=['produto_a','produto_b','coocorrencias'])
    if not pairs.empty:
        pairs=pairs.merge(variants[['id','product_id']],left_on='produto_a',right_on='id',how='left').merge(products[['id','name']],left_on='product_id',right_on='id',how='left').rename(columns={'name':'produto_a_nome'}).drop(columns=['id_x','product_id','id_y'],errors='ignore').merge(variants[['id','product_id']],left_on='produto_b',right_on='id',how='left').merge(products[['id','name']],left_on='product_id',right_on='id',how='left').rename(columns={'name':'produto_b_nome'}).drop(columns=['id_x','product_id','id_y'],errors='ignore')
    st.dataframe(pairs.head(30),use_container_width=True,hide_index=True); st.caption('Recomendação = produtos que aparecem juntos com maior frequência nos pedidos históricos. Não há dados sintéticos nem inferência de preferências fora do histórico.')
    section('PRÓXIMA COMPRA POR CLIENTE','Use o seletor para consultar o item mais frequente no histórico de cada cliente.')
    customer_id=st.selectbox('Cliente',sorted(orders.customer_id.dropna().unique().astype(int).tolist()) if not orders.empty else []); hist=orders[orders.customer_id==customer_id][['id']].merge(items[['order_id','product_variant_id','quantity']],left_on='id',right_on='order_id',how='left').groupby('product_variant_id').quantity.sum().reset_index().sort_values('quantity',ascending=False).head(10); hist=hist.merge(variants[['id','product_id']],left_on='product_variant_id',right_on='id',how='left').merge(products[['id','name']],left_on='product_id',right_on='id',how='left'); st.dataframe(hist[['name','quantity']].rename(columns={'name':'produto','quantity':'quantidade histórica'}),use_container_width=True,hide_index=True)

st.caption('Fonte: CSVs reais fornecidos pelo desafio LH Nautical. A camada raw permanece inalterada; regras de tratamento são aplicadas somente à camada treated.')
