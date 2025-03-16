from flask import Blueprint, jsonify
from racks.services import get_all_racks

racks_blueprint = Blueprint('racks', __name__)

@racks_blueprint.route('/<collection_name>/', methods=['GET'])
def get_racks(collection_name):
    racks = get_all_racks(collection_name=collection_name)
    return jsonify(racks), 200
