class Parameters:
    ARTIST = 'artist'
    TITLE = 'title'
    FORMAT = 'format'
    GENRES = 'genres'
    MOODS = 'moods'
    COMPILATIONS = 'compilations'
    COUNTRY = 'country'
    YEAR = 'year'
    START_YEAR = 'start_year'
    END_YEAR = 'end_year'
    YEARS = 'years'
    DECADE = 'decade'
    DAYS = 'days'
    TYPE = 'type'
    COLLECTION = 'collection_name'
    ANNIVERSARY = 'anniversary'
    RELEASE = 'release'
    RELEASES = 'releases'
    ALBUM = 'album'
    ALBUMS = 'albums'
    TRACK = 'track'
    SONG = 'song'
    PLAYLIST = 'playlist'
    ME = 'me'
    NEW = 'new'
    TOP = 'top'
    LOGIN = 'login'
    CALLBACK = 'callback'
    LOGOUT = 'logout'
    ALL = 'all'
    

class ParametersValues:
    PATH = 'path:'
    INT = 'int:'
    ARTIST = f'<{Parameters.ARTIST}>'
    TITLE = f'<{Parameters.TITLE}>'
    FORMAT = f'<{Parameters.FORMAT}>'
    GENRES = f'<{PATH}{Parameters.GENRES}>'
    MOODS = f'<{PATH}{Parameters.MOODS}>'
    COMPILATIONS = f'<{PATH}{Parameters.COMPILATIONS}>'
    COUNTRY = f'<{Parameters.COUNTRY}>'
    YEAR = f'<{Parameters.YEAR}>'
    START_YEAR = f'<{Parameters.START_YEAR}>'
    END_YEAR = f'<{Parameters.END_YEAR}>'
    DECADE = f'<{INT}{Parameters.DECADE}>'
    DAYS = f'<{INT}{Parameters.DAYS}>'
    TYPE = f'<{Parameters.TYPE}>'
    COLLECTION = f'<{Parameters.COLLECTION}>'
    ANNIVERSARY = f'<{Parameters.ANNIVERSARY}>'         
    RELEASE = f'<{Parameters.RELEASE}>'
    RELEASES = f'<{Parameters.RELEASES}>'
    ALBUM = f'<{Parameters.ALBUM}>'
    TRACK = f'<{Parameters.TRACK}>'
    SONG = f'<{Parameters.SONG}>'
    PLAYLIST = f'<{Parameters.PLAYLIST}>'
    

class Routes:
    ARTIST = f'{Parameters.ARTIST}/{ParametersValues.ARTIST}'
    TITLE = f'{Parameters.TITLE}/{ParametersValues.TITLE}'
    FORMAT = f'{Parameters.FORMAT}/{ParametersValues.FORMAT}'
    GENRES = f'{Parameters.GENRES}/{ParametersValues.GENRES}'
    MOODS = f'{Parameters.MOODS}/{ParametersValues.MOODS}'
    COMPILATIONS = f'{Parameters.COMPILATIONS}/{ParametersValues.COMPILATIONS}'
    COUNTRY = f'{Parameters.COUNTRY}/{ParametersValues.COUNTRY}'
    YEAR = f'{Parameters.YEAR}/{ParametersValues.YEAR}'
    YEARS = f'{Parameters.YEARS}/{ParametersValues.START_YEAR}/{ParametersValues.END_YEAR}'
    DECADE = f'{Parameters.DECADE}/{ParametersValues.DECADE}'
    DAYS = f'{Parameters.DAYS}/{ParametersValues.DAYS}'
    TYPE = f'{Parameters.TYPE}/{ParametersValues.TYPE}'
    COLLECTION = f'{Parameters.COLLECTION}/{ParametersValues.COLLECTION}'
    ANNIVERSARY = f'{Parameters.ANNIVERSARY}/{ParametersValues.DAYS}'
    RELEASE = f'{Parameters.RELEASES}/{ParametersValues.DAYS}'
    ALBUM = f'{Parameters.ALBUM}/{ParametersValues.ALBUM}'
    TRACK = f'{Parameters.TRACK}/{ParametersValues.TRACK}'
    SONG = f'{Parameters.SONG}/{ParametersValues.SONG}'
    PLAYLIST = f'{Parameters.PLAYLIST}/{ParametersValues.PLAYLIST}'
    

class Collections:
    SPOTIFY = 'spotify'
    LASTFM = 'lastfm'
    DISCOGS = 'discogs'