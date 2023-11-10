# google-drive_flask

This Flask application integrates with Google Drive to allow users to upload, view, and delete files from their Google Drive.

## Installation
Before running the application, ensure you have the following installed:
- Python 3.x
- Git
  
### Clone the Repository

### Create and Activate a Virtual Environment
python -m venv venv

### Install Dependencies
pip install -r requirements.txt

## Setup Google Drive API
1. Go to the https://console.cloud.google.com/
2. Create a new project
3. Enable the Google Drive API for your project.
4. Create credentials (OAuth client ID) and download the JSON file.
5. Save the JSON file as "credentials.json" in the root directory of your project.

### Run the Application
python app.py


## USAGE

1. Visit http://localhost:5000 in your browser.
2. Click the "Login" button to authorize the application with your Google Drive account.
3. Once authenticated, navigate to 'Google Drive Files' to upload, view, and delete files.
4. Click the "Logout" button to log out.


