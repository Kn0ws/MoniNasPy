import os
import json
import datetime
import configparser
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


# 監視するフォルダと通知先のメールアドレスの設定
config_ini = configparser.ConfigParser()

# Windows上の読み込みを考慮。UTF-8_sigに設定。
config_ini.read('config.ini', encoding='utf-8_sig') 

SMTP_SERVER = config_ini['MAIL']['SMTP_SERVER']
SMTP_PORT = config_ini['MAIL']['SMTP_PORT']
EMAIL_ADDRESS = config_ini['MAIL']['EMAIL_ADDRESS']
EMAIL_PASSWORD = config_ini['MAIL']['EMAIL_PASSWORD']

# Windows上の読み込みを考慮。UTF-8_sigに設定。
json_open = open("directories.json", 'r',  encoding='utf-8_sig')
watch_directories = json.load(json_open)

# メール送信関数
def send_email(subject, body, to_email, attachment_path=None):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'html'))

    if attachment_path:
        filename = os.path.basename(attachment_path)
        with open(attachment_path, 'rb') as attachment:
            attach = MIMEApplication(attachment.read())
        
        attach.add_header('Content-Disposition', 'attachment', filename=filename)
        msg.attach(attach)

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())

# イベントハンドラ
class MonitorHandler(FileSystemEventHandler):

    # 作成時のみ。
    # 更新時: on_modified
    # 削除時: on_deleted
    def on_created(self, event):
        now = datetime.datetime.now()
        fmt_now = now.strftime('%Y/%m/%d %H:%M:%S')
        if not event.is_directory and event.src_path.endswith('.pdf'):
            for path, email in watch_directories.items():
                if event.src_path.startswith(path):

                    _path = event.src_path
                    subject = f'【自動】{os.path.basename(path)}にPDFが作成されました。: '
                    body = f"""
                    <html>
                    <body>
                    <p>以下のフォルダにPDFが作成されました。ご確認をお願い致します。<br>
                    <b>{_path}</b><br>
                    添付ファイルでもご確認いただけますが、PC版Outlook以外のメールソフトの場合、正常に認識されない場合があります。<br>
                    現在改善に向けて検証を行っていますが、可能な限りPC版Outlookでのご確認をお願い致します。<br>
                    添付ファイルが存在しない場合、ファイルの取得にエラーが発生しています。<br>
                    そのため、添付ファイル無しで送信されている場合があります。
                    </p>
                    </body>
                    </html>
                    """
                    try:
                        send_email(subject, body, email, event.src_path)
                        print(f'{fmt_now} > 送信完了: {_path} => {email} ')
                    except PermissionError:
                        send_email(subject, body, email)
                        print(f'{fmt_now} > PermissionErrorが発生しました。Permission Error:{event.src_path}\n添付ファイル無しで送信完了')

# メイン関数
if __name__ == "__main__":
    monitor_handler = MonitorHandler()
    print("監視を開始しました")
    observer = Observer()

    for path in watch_directories.keys():
        observer.schedule(monitor_handler, path, recursive=True)

    observer.start()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        observer.stop()

    observer.join()