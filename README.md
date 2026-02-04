f5vpn-login (Titech VPN 自動ログイン)
======================================

概要
----
Titech Portalにログインし、F5 BIG-IP APM VPNへ接続するための自動化スクリプトです。
`automate_f5vpn.py` でセッションを取得し、`f5vpn-login.py` を使ってVPNを開始します。

このリポジトリは https://github.com/zrhoffman/f5vpn-login を利用しています。
特に `f5vpn-login.py` は上記プロジェクトをベースにしています。

動作環境
--------
- macOS / Linux
- Python 3
- `sudo` 実行できる環境 (VPN接続時に必要)

依存関係
--------
- requests
- beautifulsoup4

インストール例:
```
python3 -m pip install requests beautifulsoup4
```

セットアップ
------------
1. `env.py` を作成して以下を設定します。
   - `username`: ポータルのユーザー名
   - `password`: ポータルのパスワード
   - `matrix_map`: マトリクス表の値

   `env.py` の例 (リポジトリ直下に作成):
   ```python
   # env.py
   # Titech Portal のログイン情報
   username = "YOUR_PORTAL_USERNAME"
   password = "YOUR_PORTAL_PASSWORD"

   # マトリクス表 (A〜J 列, 1〜7 行)
   # 下の表を自分のマトリクス表の値で埋めると、matrix_map (例: "a1") を自動生成します。
   matrix_table = [
      # A    B    C    D    E    F    G    H    I    J
      ["",  "",  "",  "",  "",  "",  "",  "",  "",  ""],  # 1
      ["",  "",  "",  "",  "",  "",  "",  "",  "",  ""],  # 2
      ["",  "",  "",  "",  "",  "",  "",  "",  "",  ""],  # 3
      ["",  "",  "",  "",  "",  "",  "",  "",  "",  ""],  # 4
      ["",  "",  "",  "",  "",  "",  "",  "",  "",  ""],  # 5
      ["",  "",  "",  "",  "",  "",  "",  "",  "",  ""],  # 6
      ["",  "",  "",  "",  "",  "",  "",  "",  "",  ""],  # 7
   ]

   matrix_map = {
      f"{chr(ord('a') + col)}{row + 1}": matrix_table[row][col]
      for row in range(7)
      for col in range(10)
   }
   ```

   `matrix_map` は `{"a1": "…", "b1": "…", ...}` のような辞書です。
   マトリクス認証が必要なため、基本的に空にはできません。

2. `f5vpn-login.py` が実行可能なことを確認します。
```
chmod +x f5vpn-login.py
```

使い方
------
```
python3 automate_f5vpn.py
```

成功するとMRHSessionが取得され、`sudo` で `f5vpn-login.py` が実行されます。

注意事項
--------
- `env.py` に機密情報が含まれるため、取り扱いに注意してください。
- VPN 接続に失敗する場合は、ポータル側の認証方式変更や VPN 側の仕様変更が原因の可能性があります。

ライセンス / クレジット
------------------------
- 元プロジェクト: https://github.com/zrhoffman/f5vpn-login
- 本リポジトリ内の `COPYING` を参照してください。
 - 変更点: `automate_f5vpn.py` と `titech_portal_kit/` を追加し、Titech Portalの自動ログインフローを実装しています。
