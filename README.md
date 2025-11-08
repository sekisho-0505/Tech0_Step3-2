# Pricing Decision Support System

価格設定支援システム（Pricing Decision Support System）のMVP実装です。Next.js 14 + FastAPI + Supabase(PostgreSQL) を前提としたモノレポ構成になっています。

## リポジトリ構成

```
backend/   FastAPI アプリケーション（REST API, Excel 取込, 分岐点計算）
frontend/  Next.js 14 + TypeScript + MUI フロントエンド
```

### ディレクトリとコードの詳解

以下は、各ディレクトリ内の主なファイルと役割を初心者向けに説明したものです。迷ったときの地図として活用してください。

#### backend/

- `app/`
  - `main.py`：FastAPI のエントリーポイントです。価格シミュレーション・分岐点計算・Excel 取込の各エンドポイントを定義し、共通の丸め処理や CORS 設定もここで行います。
  - `config.py`：環境変数から API の設定値（例：CORS 許可リスト、データベース接続 URL）を読み込みます。設定の一元管理を行うファイルです。
  - `database.py`：SQLAlchemy を使って PostgreSQL へ接続するための共通処理（エンジン生成、セッション提供）をまとめています。
  - `models.py`：SQLAlchemy の ORM モデル定義です。Supabase に作成するテーブル（`products` や `sales_data` など）のカラムと型をクラスで表現しています。
  - `schemas.py`：Pydantic による入出力の型定義です。API が受け取る JSON と返す JSON の「形」をコードで保証し、バリデーションも兼ねます。
  - `crud.py`：DB からの集計や保存処理を関数として分離しています。`get_fixed_cost_total` や `get_sales_summary` など、アプリ固有のデータアクセスがまとまっています。
  - `utils.py`：金額の四捨五入や粗利パターンの生成など、複数のエンドポイントから使われる小さな便利関数を置いています。
- `requirements.txt`
  - バックエンドで利用する Python ライブラリの一覧です。仮想環境を作成した後、このファイルを `pip install -r requirements.txt` で読み込むと必要な依存関係がそろいます。
- `sql/`
  - `001_initial_schema.sql`：Supabase で最初に実行する SQL スクリプトです。必要なテーブルをまとめて作成します。README のサンプル INSERT と合わせて初期データを投入できます。
- `tests/`
  - `conftest.py`：pytest の共通セットアップです。テスト用のアプリケーションインスタンスやダミーデータを定義しています。
  - `test_price_simulation.py`：価格計算 API が仕様通りの値を返すかを確認する自動テストです。分岐点計算・Excel 取込のチェックも含まれています。

#### frontend/

- `app/`
  - `page.tsx`：トップページのコンポーネントです。価格シミュレーションフォーム、分岐点ダッシュボード、Excel 取込 UI を表示します。ユーザー操作に応じて API から取得したデータを画面に反映する中心的なファイルです。
  - `layout.tsx`：Next.js のレイアウトコンポーネントです。全ページ共通で適用する `<html>` 構造やヘッダー要素を定義しています。
  - `globals.css`：全体に適用するスタイル定義です。背景色や基本フォントなど、UI の共通デザインを整えます。
- `components/`
  - `ThemeRegistry.tsx`：MUI のテーマ設定（色・フォント）と SSR 対応をまとめたコンポーネントです。`app/layout.tsx` から読み込まれ、全コンポーネントに同じテーマを行き渡らせます。
- `lib/`
  - `api.ts`：フロントエンドから FastAPI にアクセスするための関数を集めたファイルです。`fetchPriceSimulation` や `fetchBreakEven` など、HTTP リクエストを送る処理を共通化しています。
- `package.json`
  - フロントエンドで使う npm パッケージとスクリプトの定義です。`npm run dev` や `npm run build` といったコマンドはここで管理されています。
- `tsconfig.json`
  - TypeScript のコンパイル設定です。`paths` や `strict` モードを通じて、型チェックと開発体験を調整しています。


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
