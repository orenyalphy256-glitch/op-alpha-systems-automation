"""
test_api.py - API integration tests
Run with: python -m pytest tests/test_api.py -v
"""
import pytest
import json
import os
import tempfile
from sqlalchemy import create_engine
from autom8.api import app
from autom8.models import init_db, get_session, Contact, Base

@pytest.fixture(scope='function')
def test_db():
    """Create a fresh test database for each test."""
    # Create temporary database file
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    db_url = f'sqlite:///{db_path}'
    
    # Create engine and tables
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    
    yield db_url
    
    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(test_db, monkeypatch):
    """Create test client with isolated database."""
    # Patch the database URL in models
    from autom8 import models
    
    # Create new engine with test database
    test_engine = create_engine(test_db)
    models.engine = test_engine
    models.SessionLocal.configure(bind=test_engine)
    
    # Configure Flask for testing
    app.config['TESTING'] = True
    app.config['DEBUG'] = False
    
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_contact(client):
    """Create a sample contact for tests that need one."""
    response = client.post('/api/v1/contacts',
                           data=json.dumps({
                               'name': 'Test User',
                               'phone': '0700000000',  # Unique phone
                               'email': 'test@example.com'
                           }),
                           content_type='application/json')
    
    # Verify creation succeeded
    assert response.status_code == 201, f"Setup failed: {response.get_json()}"
    
    return response.get_json()

# TESTS
def test_health_check(client):
    """Test health check endpoint."""
    response = client.get('/api/v1/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'


def test_root_endpoint(client):
    """Test API root returns documentation."""
    response = client.get('/')
    assert response.status_code == 200
    data = response.get_json()
    assert 'service' in data
    assert 'endpoints' in data


def test_list_contacts_empty(client):
    """Test listing contacts when database is empty."""
    response = client.get('/api/v1/contacts')
    assert response.status_code == 200
    data = response.get_json()
    assert data['count'] == 0
    assert data['contacts'] == []


def test_create_contact(client):
    """Test creating a new contact."""
    response = client.post('/api/v1/contacts',
                           data=json.dumps({
                               'name': 'Alphonce Liguori',
                               'phone': '0712345678',
                               'email': 'alphonce@example.com'
                           }),
                           content_type='application/json')
    
    assert response.status_code == 201
    data = response.get_json()
    assert data['name'] == 'Alphonce Liguori'
    assert data['phone'] == '0712345678'
    assert data['email'] == 'alphonce@example.com'
    assert 'id' in data
    assert 'created_at' in data


def test_create_contact_missing_fields(client):
    """Test creating contact with missing required fields."""
    response = client.post('/api/v1/contacts', 
                           data=json.dumps({'name': 'Test'}),
                           content_type='application/json')
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data


def test_create_contact_duplicate_phone(client, sample_contact):
    """Test creating contact with duplicate phone number."""
    response = client.post('/api/v1/contacts',
                           data=json.dumps({
                               'name': 'Different Name',
                               'phone': sample_contact['phone']
                           }),
                           content_type='application/json')
    
    assert response.status_code == 409
    data = response.get_json()
    assert 'already exists' in data['message'].lower()


def test_get_contact(client, sample_contact):
    """Test retrieving a single contact."""
    contact_id = sample_contact['id']
    response = client.get(f'/api/v1/contacts/{contact_id}')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['id'] == contact_id
    assert data['name'] == sample_contact['name']


def test_get_contact_not_found(client):
    """Test retrieving non-existent contact."""
    response = client.get('/api/v1/contacts/99999')
    
    assert response.status_code == 404
    data = response.get_json()
    assert 'not found' in data['message'].lower()


def test_update_contact(client, sample_contact):
    """Test updating a contact."""
    contact_id = sample_contact['id']
    response = client.put(f'/api/v1/contacts/{contact_id}',
                          data=json.dumps({
                              'name': 'Updated Name',
                              'email': 'updated@example.com'
                          }),
                          content_type='application/json')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'Updated Name'
    assert data['email'] == 'updated@example.com'
    assert data['phone'] == sample_contact['phone']


def test_update_contact_not_found(client):
    """Test updating non-existent contact."""
    response = client.put('/api/v1/contacts/99999',
                          data=json.dumps({'name': 'Test'}),
                          content_type='application/json')
    
    assert response.status_code == 404


def test_delete_contact(client, sample_contact):
    """Test deleting a contact."""
    contact_id = sample_contact['id']
    response = client.delete(f'/api/v1/contacts/{contact_id}')
    
    assert response.status_code == 204
    
    # Verify contact is deleted
    get_response = client.get(f'/api/v1/contacts/{contact_id}')
    assert get_response.status_code == 404


def test_delete_contact_not_found(client):
    """Test deleting non-existent contact."""
    response = client.delete('/api/v1/contacts/99999')
    
    assert response.status_code == 404


def test_list_contacts_with_pagination(client):
    """Test listing contacts with pagination."""
    # Create multiple contacts
    for i in range(5):
        client.post('/api/v1/contacts',
                   data=json.dumps({
                       'name': f'User {i}',
                       'phone': f'070000000{i}'
                   }),
                   content_type='application/json')
    
    # Test pagination
    response = client.get('/api/v1/contacts?limit=2&offset=0')
    assert response.status_code == 200
    data = response.get_json()
    assert data['count'] == 2
    assert data['limit'] == 2
    assert data['offset'] == 0


def test_search_contacts(client):
    """Test searching contacts by name."""
    # Create test contacts
    client.post('/api/v1/contacts',
               data=json.dumps({
                   'name': 'John Doe', 
                   'phone': '0701111111'
               }),
               content_type='application/json')
    client.post('/api/v1/contacts',
               data=json.dumps({
                   'name': 'Jane Smith', 
                   'phone': '0702222222'
               }),
               content_type='application/json')
    
    # Search for John
    response = client.get('/api/v1/contacts?search=john')
    assert response.status_code == 200
    data = response.get_json()
    assert data['count'] >= 1
    assert any('john' in contact['name'].lower() for contact in data['contacts'])


def test_invalid_json(client):
    """Test sending invalid JSON."""
    response = client.post('/api/v1/contacts',
                           data='invalid json',
                           content_type='application/json')
    
    assert response.status_code == 400


def test_validation_empty_name(client):
    """Test validation rejects empty name."""
    response = client.post('/api/v1/contacts',
                           data=json.dumps({
                               'name': '',
                               'phone': '0700000000'
                           }),
                           content_type='application/json')
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'name' in data['message'].lower()


def test_validation_invalid_email(client):
    """Test validation rejects invalid email."""
    response = client.post('/api/v1/contacts',
                           data=json.dumps({
                               'name': 'Test User',
                               'phone': '0700000000',
                               'email': 'invalid-email'
                           }),
                           content_type='application/json')
    
    assert response.status_code == 400
    data = response.get_json()
    assert '@' in data['message'].lower()