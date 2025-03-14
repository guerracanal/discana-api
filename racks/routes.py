from flask import Blueprint, jsonify
from racks.services import get_all_racks

racks_blueprint = Blueprint('racks', __name__)

@racks_blueprint.route("/", methods=['GET'])
def get_racks():
    racks = get_all_racks()
    return jsonify(racks), 200
