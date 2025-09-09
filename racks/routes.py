from flask import Blueprint, jsonify, request
from utils.helpers import require_admin_token
from racks.services import get_all_racks, create_rack_service, update_rack_service, delete_rack_service
from bson import ObjectId

racks_blueprint = Blueprint('racks', __name__)

@racks_blueprint.route('/<collection_name>/', methods=['GET'])
def get_racks(collection_name):
    racks = get_all_racks(collection_name=collection_name)
    return jsonify(racks), 200

@racks_blueprint.route('/<collection_name>/', methods=['POST'])
@require_admin_token
def create_rack(collection_name):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing rack data"}), 400
    response, status = create_rack_service(collection_name, data)
    return jsonify(response), status

@racks_blueprint.route('/<collection_name>/<rack_id>/', methods=['PUT'])
@require_admin_token
def update_rack(collection_name, rack_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing rack data"}), 400
    response, status = update_rack_service(collection_name, rack_id, data)
    return jsonify(response), status

@racks_blueprint.route('/<collection_name>/<rack_id>/', methods=['DELETE'])
@require_admin_token
def delete_rack(collection_name, rack_id):
    response, status = delete_rack_service(collection_name, rack_id)
    return jsonify(response), status
