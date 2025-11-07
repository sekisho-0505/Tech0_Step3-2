# Pricing Decision Support System

価格設定支援システム（Pricing Decision Support System）のMVP実装です。Next.js 14 + FastAPI + Supabase(PostgreSQL) を前提としたモノレポ構成になっています。

## リポジトリ構成

```
backend/   FastAPI アプリケーション（REST API, Excel 取込, 分岐点計算）
frontend/  Next.js 14 + TypeScript + MUI フロントエンド
```

## セットアップ

### 前提条件

- Python 3.11
- Node.js 20 以降
- Supabase プロジェクト（PostgreSQL 接続情報を取得）

### 共通環境変数

`.env`（プロジェクトルート）に以下を定義してください。

```
PRICING_DATABASE_URL=postgresql+psycopg://<user>:<password>@<host>:<port>/<database>
PRICING_ALLOWED_CORS_ORIGINS=["http://localhost:3000"]
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

> Supabase の接続文字列は `project.supabase.co` のホストと `service_role` ではなく **アプリ用のDBユーザー** を利用します。RLS を有効にした状態で API からアクセスすることを想定しています。

## バックエンド（FastAPI）

### 依存関係インストール

```
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### DB マイグレーション

`backend/sql/001_initial_schema.sql` を Supabase の SQL Editor で実行してテーブルを作成します。

初期固定費サンプル：

```
INSERT INTO public.fixed_costs (year_month, amount, category) VALUES
('2025-07-01', 34222000, '固定費'),
('2025-08-01', 38277000, '固定費'),
('2025-09-01', 43577000, '固定費');
```

### ローカル起動

```
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### テスト

```
pytest
```

### API ハイライト

- `POST /api/price-simulations/calculate`
  - 入力：`unit_cost_per_kg (円/kg)`、`target_margin_rate (率)`、`quantity_kg`
  - 出力：推奨単価、粗利益、パターン表、最低売価ガード
- `GET /api/break-even/current?year_month=YYYY-MM`
  - 固定費、売上、変動費率、分岐点売上、進捗率、危険度を返却
- `POST /api/import/excel`
  - Excel(C〜N列)取り込み。千円/kg → 円/kg 変換を適用、非数値は警告として返却

## フロントエンド（Next.js 14）

### 依存関係インストール

```
cd frontend
npm install
```

### ローカル起動

```
npm run dev
```

`NEXT_PUBLIC_API_BASE_URL` で FastAPI のエンドポイントを指定してください。UI では以下を提供します。

- 価格シミュレーションフォーム：最低売価未満の場合は保存ボタンを無効化し、警告表示
- 分岐点ダッシュボード：固定費・分岐点売上・進捗率を表示し、進捗率に応じて緑/黄/赤で表示
- Excel 取り込みモーダル：取り込み結果と警告一覧を表示

## サンプルデータ & E2E

`backend/tests/` に価格計算・分岐点・Excel 取込を1分以内で検証できる pytest が含まれています。

## ライセンス

このプロジェクトは社内利用を想定しています。
