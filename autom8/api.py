"""
api.py - Flask REST API for Contact Management
Implements: RESTful endpoints using SQLAlchemy ORM
"""
from flask import Flask, request, jsonify, abort
from sqlalchemy.exc import IntegrityError
from autom8.models import (
    get_session,
    Contact,
    create_contact,
    get_contact_by_id,
    get_contact_by_phone,
    list_contacts,
    search_contacts,
    update_contact,
    delete_contact,
    init_db,
)
from autom8.core import log

# Flask Application Setup
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False # Preserve key order in JSON responses

# Initialize database on startup
init_db()
log.info("Flask API initialized - database ready")

# Error Handlers
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "error": "Bad Request",
        "message": str(error.description) if hasattr(error, 'description') else "Invalid request"
    }), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Not Found",
        "message": str(error.description) if hasattr(error, 'description') else "Resource not found"
    }), 404

@app.errorhandler(409)
def conflict(error):
    return jsonify({
        "error": "Conflict",
        "message": str(error.description) if hasattr(error, 'description') else "Resource already exists"
    }), 409

@app.errorhandler(500)
def internal_error(error):
    log.error(f"Internal server error: {error}")
    return jsonify({
        "error": "Internal Server Error",
        "message": "An unexpected error occurred"
    }), 500

# Helper Functions
def validate_contact_data(data, required_fields=None):
    """Validate contact data from request."""
    if not data:
        return False, "Request body must be JSON"
    
    if required_fields:
        missing = [field for field in required_fields if field not in data]
        if missing:
            return False, f"Missing required fields: {', '.join(missing)}"
        
    """Validate contact name from request."""
    if 'name' in data:
        if not isinstance(data['name'], str) or not data['name'].strip():
            return False, "Name must be a non-empty string"
        if len(data['name']) > 100:
            return False, "Name must be 100 characters or less"
        
    """Validate contact phone number."""
    if 'phone' in data:
        if not isinstance(data['phone'], str) or not data['phone'].strip():
            return False, "Phone must be a non-empty string"
        if len(data['phone']) > 20:
            return False, "Phone must be 20 characters or less"
        
    """Validate email (if provided)."""
    if 'email' in data and data['email']:
        if not isinstance(data['email'], str):
            return False, "Email must be a string"
        if len(data['email']) > 100:
            return False, "Email must be 100 characters or less"
        if '@' not in data['email']:
            return False, "Email must contain @ symbol"
    
    return True, None

# API Routes - Contacts
@app.route('/api/v1/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "autom8-api",
        "version": "1.0"
    }), 200

@app.route('/api/v1/contacts', methods=['GET'])
def get_contacts():
    session = get_session()

    try:
        # Get query parameters
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        search_query = request.args.get('search', None, type=str)

        # Validate pagination params
        if limit < 1 or limit > 1000:
            abort(400, description="Limit must be between 1 and 1000")
        if offset < 0:
            abort(400, description="Offset must be non-negative")
        
        # Execute query
        if search_query:
            contacts = search_contacts(session, search_query)
        else:
            contacts = list_contacts(session, limit=limit, offset=offset)
        
        # Serialize to dict
        result = [contact.to_dict() for contact in contacts]

        log.info(f"Listed {len(result)} contacts")

        return jsonify({
            "count": len(result),
            "limit": limit,
            "offset": offset,
            "contacts": result
        }), 200
    
    except Exception as e:
        log.error(f"Error listing contacts: {e}")
        abort(500)

    finally:
        session.close()

@app.route('/api/v1/contacts/<int:contact_id>', methods=['GET'])
def get_contact(contact_id):
    session = get_session()

    try:
        contact = get_contact_by_id(session, contact_id)

        if not contact:
            abort(404, description=f"Contact with ID {contact_id} not found")

        log.info(f"Retrieved contact ID {contact_id}")

        return jsonify(contact.to_dict()), 200
    
    finally:
        session.close()

@app.route('/api/v1/contacts', methods=['POST'])
def create_contact_endpoint():
    session = get_session()

    try:
        # Get JSON data
        data = request.get_json()

        # Validate the data
        is_valid, error_msg = validate_contact_data(data, required_fields=['name', 'phone'])
        if not is_valid:
            abort(400, description=error_msg)

        # Check if phone already exists
        existing = get_contact_by_phone(session, data['phone'])
        if existing:
            abort(409, description=f"Contact with phone {data['phone']} already exists")
        
        # Create contact
        contact = create_contact(
            session,
            name=data['name'],
            phone=data['phone'],
            email=data.get('email')
        )

        log.info(f"Created contact ID {contact.id}: {contact.name}")

        return jsonify(contact.to_dict()), 201
    
    except IntegrityError as e:
        session.rollback()
        log.error(f"Error creating contact: {e}")
        abort(500)

    finally:
        session.close()

@app.route('/api/v1/contacts/<int:contact_id>', methods=['PUT'])
def update_contact_endpoint(contact_id):
    session = get_session()
    
    try:
        existing = get_contact_by_id(session, contact_id)
        if not existing:
            abort(404, description=f"Contact with ID {contact_id} not found")
        
        data = request.get_json()
        
        is_valid, error_msg = validate_contact_data(data)
        if not is_valid:
            abort(400, description=error_msg)
        
        if 'phone' in data and data['phone'] != existing.phone:
            phone_conflict = get_contact_by_phone(session, data['phone'])
            if phone_conflict:
                abort(409, description=f"Contact with phone {data['phone']} already exists")
        
        updated = update_contact(session, contact_id, **data)
        
        log.info(f"Updated contact ID {contact_id}")
        
        return jsonify(updated.to_dict()), 200
        
    except IntegrityError as e:
        session.rollback()
        log.error(f"Integrity error updating contact: {e}")
        abort(409, description="Phone number already exists")
        
    finally:
        session.close()

@app.route('/api/v1/contacts/<int:contact_id>', methods=['DELETE'])
def delete_contact_endpoint(contact_id):
    session = get_session()
    
    try:
        existing = get_contact_by_id(session, contact_id)
        if not existing:
            abort(404, description=f"Contact with ID {contact_id} not found")
        
        deleted = delete_contact(session, contact_id)
        
        if deleted:
            log.info(f"Deleted contact ID {contact_id}")
            return '', 204
        else:
            abort(500)
            
    finally: 
        session.close()

# Root Endpoint
@app.route('/', methods=['GET'])
def index():
    """
    API root - shows available endpoints.
    """
    return jsonify({
        "service": "Autom8 API",
        "version": "1.0",
        "endpoints": {
            "health": "/api/v1/health",
            "contacts": {
                "list": "GET /api/v1/contacts",
                "get": "GET /api/v1/contacts/{id}",
                "create": "POST /api/v1/contacts",
                "update": "PUT /api/v1/contacts/{id}",
                "delete": "DELETE /api/v1/contacts/{id}"
            }
        },
        "documentation": "https://github.com/orenyalphy256-glitch/op-alpha-systems-automation"
    }), 200

# Module Exports
__all__ = ["app"]


