import json
import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text

DATA_DIR = Path(os.getenv('DATA_DIR', Path(__file__).resolve().parents[1] / 'dados'))
DATABASE_URL = os.getenv('DATABASE_URL', 'mysql+pymysql://lighthouse:lighthouse@localhost:3306/lh_nautical')
engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)

TREATED_TABLES = {
    'orders': 'treated_orders', 'order_items': 'treated_order_items', 'products': 'treated_products',
    'product_variants': 'treated_product_variants', 'customers': 'treated_customers',
    'addresses': 'treated_addresses', 'returns': 'treated_returns'
}
DATE_COLUMNS = {'created_at', 'updated_at', 'placed_at', 'hire_date', 'termination_date', 'paid_at', 'issued_at', 'received_at'}
NUMERIC_COLUMNS = {'subtotal', 'discount_amount', 'total', 'quantity', 'unit_price', 'line_total', 'sale_price', 'cost_price', 'weight_kg', 'total_refund_amount'}


def clean_for_treated(df: pd.DataFrame, table: str) -> pd.DataFrame:
    out = df.copy()
    out = out.drop_duplicates().copy()
    for col in out.columns:
        if col in DATE_COLUMNS or col.endswith('_at') or col.endswith('_date'):
            out[col] = pd.to_datetime(out[col], errors='coerce')
        if col in NUMERIC_COLUMNS:
            out[col] = pd.to_numeric(out[col], errors='coerce')
    if table == 'customers':
        for col in ['tax_id', 'phone', 'email']:
            if col in out:
                out[col] = out[col].astype('string').str.strip()
    return out


def create_schema():
    schema_path = Path(__file__).resolve().parents[1] / 'database' / 'init.sql'
    statements = [s.strip() for s in schema_path.read_text().split(';') if s.strip()]
    with engine.begin() as conn:
        for statement in statements:
            conn.execute(text(statement))


def ingest_file(path: Path):
    table = path.stem
    df = pd.read_csv(path, low_memory=False)
    raw_run = pd.DataFrame([{'file_name': path.name, 'source_table': table, 'layer': 'raw', 'row_count': len(df), 'details': json.dumps({'columns': list(df.columns)})}])
    raw_run.to_sql('ingestion_runs', engine, if_exists='append', index=False)
    with engine.connect() as conn:
        run_id = conn.execute(text('SELECT LAST_INSERT_ID()')).scalar()
    raw = df.astype(object).where(pd.notna(df), None)
    raw_rows = pd.DataFrame({
        'ingestion_run_id': run_id,
        'source_table': table,
        'source_row_number': range(1, len(raw) + 1),
        'payload': raw.apply(lambda row: json.dumps(row.to_dict(), ensure_ascii=False, default=str), axis=1),
    })
    raw_rows.to_sql('raw_csv_rows', engine, if_exists='append', index=False, chunksize=2000, method='multi')
    if table in TREATED_TABLES:
        clean = clean_for_treated(df, table)
        treated_table = TREATED_TABLES[table]
        treated_run = pd.DataFrame([{'file_name': path.name, 'source_table': table, 'layer': 'treated', 'row_count': len(clean), 'details': json.dumps({'dropped_duplicate_rows': len(df) - len(clean), 'date_columns': sorted(set(clean.columns) & DATE_COLUMNS)})}])
        treated_run.to_sql('ingestion_runs', engine, if_exists='append', index=False)
        with engine.connect() as conn:
            treated_run_id = conn.execute(text('SELECT LAST_INSERT_ID()')).scalar()
        clean['source_run_id'] = treated_run_id
        clean.to_sql(treated_table, engine, if_exists='append', index=False, chunksize=2000, method='multi')
    print(f'Loaded {table}: {len(df)} raw rows')


def main():
    create_schema()
    with engine.begin() as conn:
        for table in ['raw_csv_rows', 'ingestion_runs', 'treated_orders', 'treated_order_items', 'treated_products', 'treated_product_variants', 'treated_customers', 'treated_addresses', 'treated_returns']:
            conn.execute(text(f'DELETE FROM {table}'))
    for path in sorted(DATA_DIR.glob('*.csv')):
        ingest_file(path)


if __name__ == '__main__':
    main()
