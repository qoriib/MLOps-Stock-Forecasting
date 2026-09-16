-- Cloudflare D1 Migration: 0002_create_stock_models.sql
-- Migration number: 0002 	 2026-09-17T00:00:00.000Z

CREATE TABLE IF NOT EXISTS stock_models (
    ticker TEXT PRIMARY KEY,
    scaler_json TEXT NOT NULL,
    metrics_json TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
