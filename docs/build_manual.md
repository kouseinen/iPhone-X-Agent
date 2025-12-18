# X Bookmark Summarizer - ビルド＆デプロイマニュアル

このドキュメントでは、本プロジェクト（X Bookmark Summarizer）をAWS Lambdaへデプロイするためのビルド手順を体系的にまとめます。

## 前提条件

*   **Docker** がインストールされ、起動していること。
*   ターミナル（Mac/Linux）での操作が可能であること。
*   プロジェクトルートディレクトリにいること。

---

## 1. ビルドの仕組み（概要）

AWS Lambda（Pythonランタイム）では、使用する外部ライブラリ（`requirements.txt` に記載されたもの）をソースコードと一緒にZIPファイルに含めてアップロードする必要があります。

しかし、一部のライブラリ（`google-genai` や `discord.py` など）はOS依存のバイナリを含む場合があるため、MacOS上で単純に `pip install` したものをアップロードしても、Lambda（Linux環境）では動作しないことがあります。

そのため、**Dockerを使用してAmazon Linux互換の環境内でライブラリをインストールし、それをパッケージングする** 手法を採用しています。

---

## 2. ビルド手順（コマンド）

以下のコマンドブロックをターミナルにコピー＆ペーストして実行することで、自動的に最新のZIPファイルが生成されます。
※実行するたびにバージョン番号（ファイル名の末尾）を変えることを推奨します。

```bash
# === 設定: 出力ファイル名（必要に応じて変更してください） ===
OUTPUT_ZIP="deploy_package.zip"

# 1. 既存の一時フォルダを削除
rm -rf /tmp/xbookmark_build

# 2. 一時作業用ディレクトリを作成して移動
mkdir -p /tmp/xbookmark_build
cd /tmp/xbookmark_build

# 3. プロジェクトのソースコードと要件ファイルをコピー
# 注意: パスはご自身の環境に合わせて調整が必要な場合があります
PROJECT_ROOT="/Users/takakuwasouichirou/Library/Mobile Documents/iCloud~md~obsidian/Documents/X Bookmark"
cp -r "$PROJECT_ROOT/src" .
cp "$PROJECT_ROOT/requirements.txt" .

# 4. Dockerコンテナ内でライブラリをインストール
# AWS Lambda (Python 3.12) と同じ環境を使用
docker run --rm --entrypoint /bin/bash \
  -v "$PWD":/var/task \
  public.ecr.aws/lambda/python:3.12 \
  -c "pip install -r requirements.txt -t /var/task --upgrade --no-cache-dir"

# 5. 不要なファイル・フォルダの削除（軽量化）
rm -rf *.dist-info *.egg-info __pycache__ boto3* botocore* bin
find . -name "__pycache__" -type d -exec rm -rf {} +

# 6. Pythonパッケージとして認識させるための初期化ファイル作成
touch src/__init__.py

# 7. ZIPファイルを作成
zip -r "$OUTPUT_ZIP" .

# 8. 完成したZIPをプロジェクトルートに移動
mv "$OUTPUT_ZIP" "$PROJECT_ROOT/"

# 9. 元の場所に戻り、一時ファイルを削除
cd "$PROJECT_ROOT"
rm -rf /tmp/xbookmark_build

# 10. 完了メッセージ
echo "Build Complete: $OUTPUT_ZIP"
ls -lh "$OUTPUT_ZIP"
```

---

## 3. デプロイ手順（AWSコンソール）

ビルドで生成されたZIPファイルを、AWS Lambdaにアップロードします。

1.  **AWSマネジメントコンソール** にログインし、**Lambda** のサービス画面を開く。
2.  対象の関数（例: `XBookmarkSummarizer`）を選択する。
3.  **「コード (Code)」** タブを開く。
4.  画面右側の **「アップロード元 (Upload from)」** ボタンをクリックし、**「.zipファイル (.zip file)」** を選択。
5.  **「アップロード (Upload)」** ボタンを押し、先ほど作成したZIPファイル（例: `deploy_package.zip`）を選択する。
6.  **「保存 (Save)」** ボタンをクリックする。
    *   ※ アップロード完了まで数秒〜数十秒かかります。
    *   ※ 「環境変数のサイズが大きすぎます」等のエラーではなく、単に通信エラーが出る場合はブラウザをリロードして再試行してください。

---

## 4. トラブルシューティング

### Q1. "Failed to execute 'readAsArrayBuffer'..." というエラーでアップロードできない
**原因:** ブラウザでファイルを選択した後に、ローカルでファイルを上書き更新した場合、ブラウザが保持しているファイル参照が無効になるため発生します。
**対処:** ブラウザのタブをリロード（再読み込み）してから、再度アップロード手順を行ってください。

### Q2. デプロイ後に "ModuleNotFoundError" が出る
**原因:** 必要なライブラリがZIPに含まれていない、またはフォルダ構成が間違っている可能性があります。
**対処:** 
- `src` フォルダとライブラリ（`google` フォルダなど）がZIPのルート（一番上の階層）にあるか確認してください。
- `requirements.txt` に必要なライブラリがすべて記載されているか確認してください。

### Q3. "Permission denied" エラーが出る
**原因:** 実行権限の問題です。
**対処:** 
- Dockerを使用している場合、生成されたファイルの所有権がrootになっていることがあります。`chmod -R 755 .` 等で権限を修正するか、再度ビルドコマンドを実行し直してください。
