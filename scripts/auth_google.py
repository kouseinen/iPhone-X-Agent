import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# スコープ設定（Google Drive の読み書き権限）
SCOPES = ['https://www.googleapis.com/auth/drive']

def main():
    """
    ユーザー認証を行い、リフレッシュトークンを取得して表示・保存するスクリプト
    """
    creds = None
    
    # client_secret.json の存在確認
    if not os.path.exists('client_secret.json'):
        print("エラー: 'client_secret.json' が見つかりません。")
        print("GCPコンソールから 'OAuth 2.0 Client ID' (Desktop App) のJSONをダウンロードし、")
        print("このスクリプトと同じフォルダに 'client_secret.json' という名前で保存してください。")
        return

    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            'client_secret.json', SCOPES)
        creds = flow.run_local_server(port=0)
    except Exception as e:
        print(f"認証フロー中にエラーが発生しました: {e}")
        return

    print("\n" + "="*50)
    print("認証成功！以下の情報を Lambda の環境変数に設定してください。")
    print("="*50)
    
    # client_secret.json から読み込み
    with open('client_secret.json', 'r') as f:
        client_data = json.load(f)
        # web か installed か判定
        key = 'installed' if 'installed' in client_data else 'web'
        client_id = client_data[key]['client_id']
        client_secret = client_data[key]['client_secret']

    print(f"\nGOOGLE_CLIENT_ID: {client_id}")
    print(f"GOOGLE_CLIENT_SECRET: {client_secret}")
    print(f"GOOGLE_REFRESH_TOKEN: {creds.refresh_token}")
    print("\n" + "="*50)
    
    # .env ファイルへの追記（ローカル開発用）
    save_env = input("この情報を .env ファイルに追記しますか？ (y/n): ")
    if save_env.lower() == 'y':
        with open('.env', 'a') as f:
            f.write(f"\nGOOGLE_CLIENT_ID={client_id}")
            f.write(f"\nGOOGLE_CLIENT_SECRET={client_secret}")
            f.write(f"\nGOOGLE_REFRESH_TOKEN={creds.refresh_token}")
        print(".env に追記しました。")

if __name__ == '__main__':
    main()

