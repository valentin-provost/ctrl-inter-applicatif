from flask import Flask, request
from pieces_entities import DataLegoPiece, metadata_obj
import base64
from flask.json import jsonify
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy import select
from sqlalchemy.orm import Session
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = b'pieces key'

engine = create_engine(os.getenv('PIECES_DB_URL'), echo=True)
metadata_obj.create_all(engine)

@app.get('/pieces/available')
def list_available_pieces():
    session_db = Session(engine)
    statement = select(DataLegoPiece).filter_by(model_id=None)
    available_pieces = list(session_db.scalars(statement=statement))
    
    result = []
    for piece in available_pieces:
        result.append({
            'name': piece.name,
            'color': piece.color,
            'model_id': piece.model_id
        })
        
    return {'pieces': result}

@app.post('/pieces')
def create_piece():
    authorization_header = request.headers.get(key='Authorization', type=str, default=None)
    decoded_auth_header = None
    if authorization_header:
        decoded_auth_header = base64.b64decode(authorization_header.split(' ')[-1]).decode()
    if decoded_auth_header is None:
        return {}, 401
    
    if 'name' not in request.json or 'color' not in request.json:
        return {}, 415
        
    piece = DataLegoPiece(
        name=request.json['name'],
        color=request.json['color']
    )
    with Session(engine) as session_db:
        session_db.add(piece)
        session_db.commit()
        result = jsonify(piece)
    return result

@app.post('/pieces/<int:piece_id>/assign')
def assign_piece(piece_id):
    authorization_header = request.headers.get(key='Authorization', type=str, default=None)
    decoded_auth_header = None
    if authorization_header:
        decoded_auth_header = base64.b64decode(authorization_header.split(' ')[-1]).decode()
    if decoded_auth_header is None:
        return {}, 401
        
    if 'model_id' not in request.json:
        return {}, 415
        
    with Session(engine) as session_db:
        statement = select(DataLegoPiece).filter_by(id=piece_id)
        piece = session_db.scalars(statement=statement).first()
        if piece:
            piece.model_id = request.json['model_id']
            session_db.commit()
            return jsonify(piece)
    return {}, 404