# EstateLens (エステート・レンズ) 🏠🔍

賃貸物件のスクレイピング、データクリーニング、および多次元的な市場分析を行うデータパイプラインプロジェクトです。

## 🚀 プロジェクト概要
特定の不動産情報サイトから物件データを自動収集し、築年数、面積、駅徒歩分数などの要素と家賃の相関を分析可能な形式に整形します。
「市場の相場から乖離したお値打ち物件（市場の歪み）」をデータから発見することを目的としています。

## 🛠 技術スタック
### Backend
- **Python 3.10+**
- **FastAPI**: 高速なAPIサーバー構築と自動ドキュメント生成。
- **Playwright**: JavaScript駆動の動的コンテンツを正確にスクレイピング。
- **Pandas**: 正規表現を用いた高度なデータクリーニングと整形。
- **SQLAlchemy / PostgreSQL**: 収集データの永続化と時系列管理。

### Infrastructure
- **Docker / Docker Compose**: 環境の分離とVPSへのスムーズなデプロイ。
- **Ubuntu 24.04 (VPS)**: 24時間稼働のデータ収集基盤。

## 🏗 アーキテクチャ
1. **Scraper**: Playwrightを使用し、物件カセット内の親子構造（物件・部屋）を二重ループで抽出。
2. **Processor**: Pandasを使用し、「10.5万円」や「築15年」などの文字列を、分析可能な数値データへ変換。
3. **API**: FastAPIを介してスクレイピングの実行指示やデータ取得を制御。
4. **Database**: PostgreSQLにより、重複を除いたユニークな物件情報を管理。

## 🚦 セットアップ
```bash
# リポジトリのクローン
git clone [https://github.com/hisao5232/EstateLens.git](https://github.com/hisao5232/EstateLens.git)
cd EstateLens

# 環境変数の設定
cp .env.example .env  # テンプレートから作成

# 起動
docker compose up -d --build

## 📝 今後の展望
- Next.js + Cloudflare Pages による分析ダッシュボードの公開

- GitHub Actions を利用した週次スクレイピングの自動化

- 機械学習を用いた家賃予測モデルの実装
