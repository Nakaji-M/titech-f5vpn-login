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
- keyring

インストール例:
```
python3 -m pip install requests beautifulsoup4 keyring
```

セットアップ
------------
1. keyring にログイン情報を保存します。
```
python3 automate_f5vpn.py --set-key
```

   `matrix_map` は `{"a1": "…", "b1": "…", ...}` のような辞書です。
   JSON を貼り付けるか、`--matrix-map-file` で JSON ファイルを指定できます。

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
- VPN 接続に失敗する場合は、ポータル側の認証方式変更や VPN 側の仕様変更が原因の可能性があります。

ライセンス / クレジット
------------------------
- 元プロジェクト: https://github.com/zrhoffman/f5vpn-login
- 本リポジトリ内の `COPYING` を参照してください。
 - 変更点: `automate_f5vpn.py` と `titech_portal_kit/` を追加し、Titech Portalの自動ログインフローを実装しています。
