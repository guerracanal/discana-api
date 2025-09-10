from flask import Blueprint, request, send_file, render_template
from cards.services import generate_extra_card, generate_card

cards_blueprint = Blueprint('cards', __name__)

@cards_blueprint.route('/extra', methods=['GET'])
def card_extra():
    params = {
        'genres': request.args.getlist('genres'),
        'subgenres': request.args.getlist('subgenres'),
        'moods': request.args.getlist('moods'),
        'country': request.args.get('country'),
        'formats': request.args.getlist('formats'),
        'date_release': request.args.get('date_release'),
        'duration': request.args.get('duration'),
        'album': request.args.get('album')
    }
    card_bytes, filename, status = generate_extra_card(params)
    if card_bytes is None:
        return filename, status
    return send_file(
        card_bytes,
        mimetype='image/png',
        download_name=filename,
        as_attachment=True
    )

@cards_blueprint.route('/', methods=['GET'])
def index():
    return render_template('mainpage.html', PageTitle="Vinyl Card Generator")

@cards_blueprint.route('', methods=['POST', 'GET'])
def card_result():
    if request.method == 'GET':
        params = {
            'link': request.args.get('link'),
            'icon': request.args.get('icon'),
            'album': request.args.get('album'),
            'album_input': request.args.get('album_input'),
            'title': request.args.get('title'),
            'subtitle': request.args.get('subtitle'),
            'image': request.args.get('image'),
            'details': request.args.get('details'),
            'jp': request.args.get('jp')
        }
        card_bytes, filename, status = generate_card(params)
        return send_file(
            card_bytes,
            mimetype='image/png',
            download_name=filename,
            as_attachment=True
        )