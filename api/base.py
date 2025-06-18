
from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from functools import wraps
import json
from datetime import datetime, timezone

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

def api_key_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({'error': 'API key required'}), 401
        
        # Validate API key against tenant settings
        if api_key != current_user.tenant.api_key:
            return jsonify({'error': 'Invalid API key'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

def json_response(data, status=200):
    """Standard JSON response format"""
    return jsonify({
        'status': 'success' if status < 400 else 'error',
        'data': data,
        'timestamp': datetime.now(timezone.utc).isoformat()
    }), status

@api_bp.route('/health')
def health_check():
    return json_response({'message': 'API is healthy'})

@api_bp.route('/customers', methods=['GET'])
@login_required
@api_key_required
def api_customers():
    from models import Customer
    customers = Customer.query.filter_by(tenant_id=current_user.tenant_id).all()
    return json_response([{
        'id': c.id,
        'name': c.name,
        'email': c.email,
        'phone': c.phone,
        'city': c.city
    } for c in customers])
