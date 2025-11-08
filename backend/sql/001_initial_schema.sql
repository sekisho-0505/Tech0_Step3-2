CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS public.products (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  product_code VARCHAR(50) UNIQUE NOT NULL,
  product_name VARCHAR(200) NOT NULL,
  category VARCHAR(100),
  unit_cost_per_kg NUMERIC(14,3),
  unit_price_per_kg NUMERIC(14,3),
  target_margin_rate NUMERIC(6,4),
  min_margin_rate NUMERIC(6,4),
  unit TEXT NOT NULL DEFAULT 'JPY/kg',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.price_simulations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  product_id UUID REFERENCES public.products(id),
  simulation_at TIMESTAMP NOT NULL DEFAULT NOW(),
  input_cost_per_kg NUMERIC(14,3) NOT NULL,
  target_margin_rate NUMERIC(6,4) NOT NULL,
  calculated_price_per_kg NUMERIC(14,3) NOT NULL,
  selected_price_per_kg NUMERIC(14,3),
  quantity_kg NUMERIC(14,3),
  gross_profit_total NUMERIC(16,2),
  parameters JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.fixed_costs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  year_month DATE NOT NULL,
  amount NUMERIC(14,2) NOT NULL,
  category VARCHAR(100) NOT NULL DEFAULT '固定費',
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.sales_data (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  product_id UUID REFERENCES public.products(id),
  sale_date DATE NOT NULL,
  quantity_kg NUMERIC(14,3),
  unit_price_per_kg NUMERIC(14,3),
  unit_cost_per_kg NUMERIC(14,3),
  created_at TIMESTAMP DEFAULT NOW()
);
