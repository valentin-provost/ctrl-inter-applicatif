from flask import Flask, request
from models_entities import DataLegoModel, metadata_obj
import base64
from flask.json import jsonify
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy import select
from sqlalchemy.orm import Session
import requests
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = b'models key'

engine = create_engine(os.getenv('MODELS_DB_URL'), echo=True)
metadata_obj.create_all(engine)

@app.post('/models')
def create_model():
    authorization_header = request.headers.get(key='Authorization', type=str, default=None)
    decoded_auth_header = None
    if authorization_header:
        decoded_auth_header = base64.b64decode(authorization_header.split(' ')[-1]).decode()
    if decoded_auth_header is None:
        return {}, 401
        
    if 'name' not in request.json:
        return {}, 415
        
    model = DataLegoModel(
        name=request.json['name']
    )
    with Session(engine) as session_db:
        session_db.add(model)
        session_db.commit()
        result = jsonify(model)
    return result

@app.post('/models/<int:model_id>/pieces/<int:piece_id>')
def add_piece_to_model(model_id, piece_id):
    authorization_header = request.headers.get(key='Authorization', type=str, default=None)
    decoded_auth_header = None
    if authorization_header:
        decoded_auth_header = base64.b64decode(authorization_header.split(' ')[-1]).decode()
    if decoded_auth_header is None:
        return {}, 401

    encoded_auth = base64.b64encode(b'inter_service_user').decode('utf-8')
    
    result = requests.post(
        url=f'http://localhost:5000/pieces/{piece_id}/assign',
        json={"model_id": model_id},
        headers={'Authorization': f'Bearer {encoded_auth}'}
    )
    
    return result.json(), result.status_code