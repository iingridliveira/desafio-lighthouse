CREATE TABLE IF NOT EXISTS ingestion_runs (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  file_name VARCHAR(255) NOT NULL,
  source_table VARCHAR(100) NOT NULL,
  layer ENUM('raw','treated') NOT NULL,
  row_count INT NOT NULL,
  status VARCHAR(30) NOT NULL DEFAULT 'completed',
  details JSON NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS raw_csv_rows (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  ingestion_run_id BIGINT NOT NULL,
  source_table VARCHAR(100) NOT NULL,
  source_row_number INT NOT NULL,
  payload JSON NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (ingestion_run_id) REFERENCES ingestion_runs(id),
  INDEX idx_raw_source (source_table),
  INDEX idx_raw_run (ingestion_run_id)
);

CREATE TABLE IF NOT EXISTS treated_orders (
  id INT PRIMARY KEY, order_number VARCHAR(80), channel VARCHAR(80), customer_id INT,
  salesperson_id INT NULL, location_id INT, status VARCHAR(80), subtotal DECIMAL(18,2),
  discount_amount DECIMAL(18,2), total DECIMAL(18,2), placed_at DATETIME NULL,
  created_at DATETIME NULL, updated_at DATETIME NULL, source_run_id BIGINT NULL,
  INDEX idx_orders_date (created_at), INDEX idx_orders_customer (customer_id)
);
CREATE TABLE IF NOT EXISTS treated_order_items (
  id INT PRIMARY KEY, order_id INT, product_variant_id INT, quantity DECIMAL(18,4),
  unit_price DECIMAL(18,2), icms_rate DECIMAL(12,4), ipi_rate DECIMAL(12,4),
  line_total DECIMAL(18,2), source_run_id BIGINT NULL,
  INDEX idx_items_order (order_id), INDEX idx_items_variant (product_variant_id)
);
CREATE TABLE IF NOT EXISTS treated_products (
  id INT PRIMARY KEY, name VARCHAR(255), description TEXT, brand_id INT, category_id INT,
  ncm_code VARCHAR(80), unit_of_measure VARCHAR(30), is_active BOOLEAN, source_run_id BIGINT NULL
);
CREATE TABLE IF NOT EXISTS treated_product_variants (
  id INT PRIMARY KEY, product_id INT, sku VARCHAR(120), barcode_ean VARCHAR(120),
  sale_price DECIMAL(18,2), cost_price DECIMAL(18,2), weight_kg DECIMAL(18,4),
  icms_rate DECIMAL(12,4), ipi_rate DECIMAL(12,4), is_active BOOLEAN, source_run_id BIGINT NULL,
  INDEX idx_variants_product (product_id)
);
CREATE TABLE IF NOT EXISTS treated_customers (
  id INT PRIMARY KEY, person_type VARCHAR(4), legal_name VARCHAR(255), trade_name VARCHAR(255),
  tax_id VARCHAR(40), state_registration VARCHAR(80), email VARCHAR(320), phone VARCHAR(50),
  is_active BOOLEAN, created_at DATETIME NULL, updated_at DATETIME NULL, source_run_id BIGINT NULL
);
CREATE TABLE IF NOT EXISTS treated_addresses (
  id INT PRIMARY KEY, customer_id INT, address_type VARCHAR(50), city VARCHAR(150), state VARCHAR(80),
  country VARCHAR(100), is_primary BOOLEAN, source_run_id BIGINT NULL,
  INDEX idx_addresses_customer (customer_id)
);
CREATE TABLE IF NOT EXISTS treated_returns (
  id INT PRIMARY KEY, order_id INT, customer_id INT, status VARCHAR(80), reason VARCHAR(255),
  total_refund_amount DECIMAL(18,2), created_at DATETIME NULL, source_run_id BIGINT NULL
);
