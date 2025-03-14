from flask import Blueprint, jsonify
from racks_types.services import get_all_racks_types

racks_types_blueprint = Blueprint('racks_ptypes', __name__)

@racks_types_blueprint.route("/", methods=['GET'])
def get_racks_ptes():
    racks = get_all_racks_types()
    return jsonify(racks), 200
