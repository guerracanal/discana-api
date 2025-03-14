from flask import Blueprint, jsonify
from racks_pendientes.services import get_all_racks_ptes

racks_ptes_blueprint = Blueprint('racks_ptes', __name__)

@racks_ptes_blueprint.route("/", methods=['GET'])
def get_racks_ptes():
    racks = get_all_racks_ptes()
    return jsonify(racks), 200
