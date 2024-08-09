# Chroma QA Chat

Chroma QA Chatは、PDFドキュメントをインデックス化し、質問に対して関連する情報を提供するチャットアプリケーションです。このプロジェクトは、LangChain、Chainlit、Chromaなどのライブラリを使用して構築されています。また、このプロジェクトは [chroma-qa-chat](https://github.com/Chainlit/cookbook/tree/main/chroma-qa-chat) のリポジトリを参考にしています。


## 必要条件

- Python 3.11
- Poetry

## インストール

1. リポジトリをクローンします。

    ```sh
    git clone <リポジトリのURL>
    cd chroma-qa-chat
    ```

2. Poetryを使用して依存関係をインストールします。

    ```sh
    poetry install
    ```

3. 必要に応じて、`.env` ファイルを設定します。

## 使用方法

1. PDFファイルを `pdfs/` ディレクトリに配置します。

2. アプリケーションを起動します。

    ```sh
    poetry run chainlit run app.py --port 8000
    ```

3. ブラウザで http://localhost:8000 にアクセスして、チャットインターフェースを使用します。

## 主な機能

- PDFドキュメントのインデックス化
- 質問に対する関連情報の提供
- チャットインターフェース

## コードの概要

### app.py

- `process_pdfs(pdf_storage_path: str)` : PDFファイルを読み込み、ドキュメントをインデックス化します。
- `on_chat_start()` : チャットセッションの開始時に呼び出される非同期関数です。
- `on_message(message: cl.Message)` : メッセージを処理する非同期関数です。

### Dockerfile

- アプリケーションのDockerイメージをビルドするための設定ファイルです。

### pyproject.toml

- プロジェクトの依存関係とメタデータを定義するファイルです。

## ライセンス

このプロジェクトはMITライセンスの下でライセンスされています。詳細については、LICENSEファイルを参照してください。

## 貢献

貢献を歓迎します！バグ報告、機能リクエスト、プルリクエストをお待ちしています。

## 作者

- Koichiro Mori <f2forest@gmail.com>
