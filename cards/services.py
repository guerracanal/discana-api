import io
from datetime import datetime
from PIL import Image
from cards.extra_card_refactor import make_extra_card
from cards.mongo_utils import get_album_by_spotify_id
from cards.card_generator import generator

def generate_extra_card(params):
    genres = params.get('genres', [])
    subgenres = params.get('subgenres', [])
    moods = params.get('moods', [])
    country = params.get('country')
    formats = params.get('formats', [])
    date_release = params.get('date_release')
    duration = params.get('duration')
    album_id = params.get('album')
    title = None
    artist = None

    if album_id:
        album = get_album_by_spotify_id(album_id)
        if not album:
            return None, {'error': 'Album not found'}, 404
        genres = album.get('genre', genres)
        subgenres = album.get('subgenres', subgenres)
        moods = album.get('mood', moods)
        country = album.get('country', country)
        formats = album.get('format', formats)
        date_release = album.get('date_release', date_release)
        duration = album.get('duration', duration)
        title = album.get('title', 'Unknown Album')
        artist = album.get('artist', 'Unknown Artist')

    card = make_extra_card(genres, subgenres, moods, country, formats, date_release, duration)
    card = Image.fromarray(card)
    card = card.resize((int(6.3/2.54*300), int(8.8/2.54*300)), resample=Image.LANCZOS)

    card_bytes = io.BytesIO()
    card.save(card_bytes, "png")
    card_bytes.seek(0)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if album_id:
        safe_title = title.replace(" ", "_") if title else "Unknown_Album"
        safe_artist = artist.replace(" ", "_") if artist else "Unknown_Artist"
        filename = f"{safe_artist}_{safe_title}_{timestamp}_extra_card.png"
    else:
        base = "_".join(filter(None, [
            (genres[0] if genres else None),
            country,
            duration
        ]))
        if not base:
            base = "extra_card"
        filename = f"{base}_{timestamp}.png"

    return card_bytes, filename, 200

def generate_card(params):
    album_link = params.get('link')
    icon = params.get('icon')
    album = params.get('album')
    album_input = params.get('album_input')
    title = params.get('title')
    subtitle = params.get('subtitle')
    image = params.get('image')
    details = params.get('details')
    jp = params.get('jp')

    if album:
        album_link = r'https://open.spotify.com/album/' + album
    elif album_input:
        album_link = album_input

    resolution = (5040, 3600, 3)
    card, album_name = generator(album_link, resolution, icon, title, subtitle, image, details, jp)
    card = Image.fromarray(card)
    card = card.resize((int(6.3/2.54*300), int(8.8/2.54*300)), resample=Image.LANCZOS)

    card_bytes = io.BytesIO()
    card.save(card_bytes, "png")
    card_bytes.seek(0)

    filename = f"{album_name}_card.jpg"
    return card_bytes, filename, 200
