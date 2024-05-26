# MoniNasPy

LAN内のNAS等のファイルサーバーに保存されている複数のフォルダを監視し、変更・作成されれば
指定のメールアドレスに通知メールを送信するPythonスクリプトです。

Python3系（Python3.12にて動作確認）

## Installation

```bash
pip install -r requirements.txt
```

## How to Use

config.ini に、送信用メールサーバーの認証情報を指定します。
directories.jsonに、対象となるフォルダパス : 送信先メールアドレス を指定します。
複数指定可能です。
Windowsの場合、パスを以下のように入力します。

✗ \\FILE-SV\Target\path\to\1
◯ \\\\FILE-SV\\Target\\path\\to\\1


```bash
python moninas.py
```