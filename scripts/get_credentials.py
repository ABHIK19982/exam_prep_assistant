import json
import os
import configparser
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

def read_config(config_file = 'tokens.ini'):
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(__file__), '..','config', config_file)
    config.read(config_path)
    return config

def get_token(conf, token_path = 'config/token.json'):
    SCOPES = conf['GOOGLE']['SCOPES'].split(',')
    #print(SCOPES)
    client_config = {
        "installed": {
            "client_id": conf['GOOGLE']['CLIENT_ID'],
            "client_secret": conf['GOOGLE']['CLIENT_SECRET'],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "project_id": "monthly-report-444117",
            "redirect_uris": "http://localhost:6060/"
        }
    }
    try:
        with open(token_path , 'r') as f:
            gtoken = json.load(f)
            creds = Credentials.from_authorized_user_info(gtoken)
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())

    except FileNotFoundError as e :
        flow = InstalledAppFlow.from_client_config(
            client_config,
            SCOPES
        )
        creds = flow.run_local_server(
            port=6060,
            prompt='consent',
            access_type='offline'  # This enables refresh token
        )
        gtoken = {
            'token': creds.token,
            'refresh_token': creds.refresh_token,
            'token_uri': creds.token_uri,
            'client_id': creds.client_id,
            'client_secret': creds.client_secret,
            'scopes': creds.scopes
        }
        with open(token_path, 'w') as f:
            json.dump(gtoken, f)
    return creds