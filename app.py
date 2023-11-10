import os.path
from flask import Flask, render_template, redirect, url_for, session, request
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
from werkzeug.utils import secure_filename
import tempfile
import google.auth
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'batman'


@app.route('/')
def index():
    authenticated = is_authenticated()
    return render_template('index.html', authenticated=authenticated)

def is_authenticated():
    token_file_path = "token.json"
    return os.path.exists(token_file_path)


SCOPES = ["https://www.googleapis.com/auth/drive"]

@app.route('/login')
def login():
  creds = None
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)

    with open("token.json", "w") as token:
      token.write(creds.to_json())
    return redirect('/google_drive_api')

@app.route('/logout')
def logout():
    session.clear()

    token_file_path = "token.json"
    if os.path.exists(token_file_path):
        os.remove(token_file_path)

    return redirect(url_for('index'))


def save_image(file_name, mime_type, file_data):
    drive_api = get_drive_service()

    media_body = MediaIoBaseUpload(BytesIO(file_data.read()),
                                    mimetype=mime_type,
                                    resumable=True)

    body = {
        'name': file_name,
        'mimeType': mime_type,
    }

    file = drive_api.files().create(body=body, media_body=media_body, fields='id').execute()
    file_id = file.get('id')

    file_data.close()

    return file_id

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect('/')

    file = request.files['file']
    if not file:
        return redirect('/google_drive_api')

    filename = secure_filename(file.filename)

    with tempfile.TemporaryFile() as fp:
        ch = file.read()
        fp.write(ch)
        fp.seek(0)

        mime_type = request.headers['Content-Type']
        save_image(filename, mime_type, fp)

    return redirect('/google_drive_api')
    
@app.route('/google_drive_api')
def google_drive_api():
    drive_service = get_drive_service()
    if not drive_service:
        return redirect(url_for('login'))

    files = fetch_files(drive_service)
    return render_template('google_drive_api.html', files=files)

def get_drive_service():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    
    return build("drive", "v3", credentials=creds)

def fetch_files(service):
    try:
        results = (
            service.files()
            .list(pageSize=200, fields="nextPageToken, files(id, name, webViewLink, thumbnailLink)")
            .execute()
        )
    
        items = results.get("files", [])

        if not items:
            return []

        files = []
        for item in items:
            file_id = item["id"]
            file_name = item["name"]
            file_link = item.get("webViewLink", "#") 
            file_thumbnail = item.get("thumbnailLink", None)
            files.append({"id": file_id, "name": file_name, "link": file_link, "thumbnail": file_thumbnail})

        return files
    except HttpError as error:
        print(f"An error occurred: {error}")
        return []
    

@app.route('/delete/<file_id>')
def delete(file_id):
    drive_service = get_drive_service()
    delete_file(drive_service, file_id)
    return redirect(url_for('google_drive_api'))

def delete_file(drive_service, file_id):
    drive_service.files().delete(fileId=file_id).execute()

    
if __name__ == '__main__':
    app.run(debug=True)
