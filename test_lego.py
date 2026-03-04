import pytest
import base64
from pieces_service import app, engine
from pieces_entities import DataLegoPiece, metadata_obj
from sqlalchemy.orm import Session

@pytest.fixture()
def config_app():
    app.config.update({
        'TESTING': True
    })
    yield app

@pytest.fixture()
def client(config_app):
    return config_app.test_client()

@pytest.fixture()
def prepare_db():
    metadata_obj.drop_all(engine)
    metadata_obj.create_all(engine)
    
    piece1 = DataLegoPiece(name='brique 2x4', color='rouge')
    piece2 = DataLegoPiece(name='plaque 2x2', color='bleu')
    
    with Session(engine) as session:
        session.add(piece1)
        session.add(piece2)
        session.flush() 
        piece2.model_id = 1
        session.commit()
        
    yield metadata_obj
    metadata_obj.drop_all(engine)

def test_list_available_pieces(client, prepare_db):
    result = client.get('/pieces/available')
    json_result = result.json['pieces']
    
    assert len(json_result) == 1
    assert json_result[0]['name'] == 'brique 2x4'
    assert json_result[0]['model_id'] is None

def test_create_piece(client, prepare_db):
    encoded_auth = base64.b64encode(b'test_user').decode('utf-8')
    headers = {'Authorization': f'Bearer {encoded_auth}'}
    
    response = client.post('/pieces', json={'name': 'tuile 1x2', 'color': 'noir'}, headers=headers)
    
    piece_actual = response.json
    assert response.status_code == 200
    assert 'name' in piece_actual
    assert 'tuile 1x2' == piece_actual['name']
    assert 'color' in piece_actual
    assert 'noir' == piece_actual['color']

def test_assign_piece(client, prepare_db):
    encoded_auth = base64.b64encode(b'test_user').decode('utf-8')
    headers = {'Authorization': f'Bearer {encoded_auth}'}
    
    response = client.post('/pieces/1/assign', json={'model_id': 99}, headers=headers)
    
    piece_actual = response.json
    assert response.status_code == 200
    assert 'model_id' in piece_actual
    assert 99 == piece_actual['model_id']

def test_unauthorized_access(client, prepare_db):
    response = client.post('/pieces', json={'name': 'tuile 1x2', 'color': 'noir'})
    assert response.status_code == 401