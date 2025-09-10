class MusicGenres:
    def __init__(self):
        # Diccionario principal con géneros padres como keys y listas de subgéneros como values
        self.genres = {
            'Rock': [
                'Rock & Roll', 'Rockabilly', 'Blues Rock', 'Garage Rock', 'Psych Rock',
                'Pop Rock', 'Rock Experimental', 'Folk Rock', 'Jazz Rock', 'Heavy Psych',
                'Blues Psych', 'Garage Psych', 'Surf Rock', 'Acid Rock', 'Merseybeat',
                'Nederbeat', 'Hard Rock', 'Prog', 'Progressive Rock', 'Prog Rock', 
                'Symphonic Prog', 'Sureño', 'Art Rock',
                'Glam Rock', 'Power Pop', 'Space Rock', 'New Wave', 'Funk Rock', 'AOR',
                'Hard Blues Rock', 'Art Prog', 'Avant Prog', 'Krautrock', 'Heartland Rock',
                'Roots Rock', 'Piano', 'Soft Rock', 'Country Rock', 'Zeuhl', 'Canterbury Scene',
                'Rock In Opposition', 'Swamp Rock', 'Pub Rock', 'British Folk Rock', 'Boogie Rock',
                'Yacht Rock', 'Latin Rock', 'Deutschrock', 'Andean Rock', 'Raga Rock',
                'Anatolian Rock', 'Afro Rock', 'Andalusian Rock', 'Alternative Rock',
                'Noise Rock', 'Goth Rock', 'Neo Prog', 'Heavy Rock', 'Celtic Rock', 'Dim Wave',
                'Zolo', 'Rock Urbano Español', 'Paisley Underground', 'Indie Rock',
                'Rock Industrial', 'Slowcore', 'Post Rock', 'Slacker Rock', 'Math Rock',
                'Neo Psychedelia', 'Midwest Emo', 'Shoegaze', 'Stoner Rock', 'Britpop',
                'Grunge', 'Noise Pop', 'Raw Indie Rock', 'Space Rock Revival', 'Latin Alternative',
                'Post-Grunge', 'Emo Pop', 'Post-Punk Revival', 'Garage Rock Revival',
                'Harsh Indie Rock', 'Popgaze', 'Technical Post Rock', 'J-Rock',
                'Alternative Art Rock', 'Melodic Math Rock', 'Heavy Alternative', 'Red Dirt',
                'Experimental Post Rock', 'Emotional Math Rock', 'Pigfuck', 'Geek Rock',
                
            ],
            'Metal': [
                'Heavy Metal', 'Thrash Metal', 'Death Metal', 'Trad Doom', 'Speed Metal',
                'Tech Thrash', 'Crossover', 'Glam Metal', 'US Power', 'NWOBHM',
                'Blackened Thrash', 'Neoclassical Metal', 'Black Metal', 'Prog Metal',
                'Alt Metal', 'Power Metal', 'Grindcore', 'Metalcore', 'Doom Metal',
                'Tech Death', 'Sludge Metal', 'Groove Metal', 'Stoner Metal', 'Melodic Death',
                'Industrial Metal', 'Atmospheric Black', 'Melodic Black', 'Brutal Death',
                'Nu Metal', 'Death Doom', 'Deathgrind', 'Symphonic Black', 'Goth Metal',
                'Folk Metal', 'Funk Metal', 'Rap Metal', 'NDH', 'Epic Doom', 'Viking Metal',
                'Death & Roll', 'Pagan Black', 'Symphonic Metal', 'Avant Metal', 'Prog Death',
                'Atmospheric Sludge', 'Deathcore', 'Mathcore', 'Post-Metal', 'Blackened Death',
                'Melodic Metalcore', 'Symphonic Power', 'Depressive Black', 'Funeral Doom',
                'Prog Metalcore', 'Drone Metal', 'Brutal Tech Death', 'Goregrind', 'Slam Death',
                'Prog Power', 'War Metal', 'Cybergrind', 'Celtic Metal', 'Prog Black',
                'Cyber Metal', 'Black & Roll', 'Beatdown Metalcore', 'Djent', 'Blackgaze',
                'Avant Death', 'Avant Black', 'Doomgaze', 'Tech Deathcore', 'Trance Metal'
            ],
            'Punk': [
                'Punk Rock', 'Post-Punk', 'Art Punk', 'Hardcore Punk', 'Crust Punk',
                'Garage Punk', 'Synth Punk', 'Psychobilly', 'Dance-Punk', 'Oi!',
                'Coldwave', 'Thrashcore', 'New York Hardcore', 'Deathrock', 'Emocore',
                'No Wave', 'Anarcho Punk', 'UK82', 'Blues Punk', 'Glam Punk',
                'Cowpunk', 'Post-Hardcore', 'Pop Punk', 'Melodic Hardcore', 'Powerviolence',
                'Screamo', 'Folk Punk', 'Ska Punk', 'D-Beat', 'Horror Punk',
                'Headcore', 'Muff Punk', 'Skate Punk', 'Riot Grrrl', 'Celtic Punk',
                'Surf Punk', 'Burning Spirits', 'Emoviolence', 'Digital Hardcore',
                'Emo-Pop Punk', 'Swancore', 'Neocrust', 'Sasscore', 'Post-Hardpop',
                'Skacore', 'Nintendocore', 'Hard Oi!', 'Gypsypunk', 'Blackened Crust',
                'Easycore', 'Indie Pop Punk', 'Eggpunk', 'Trancecore', 'Dance-Punk Revival'
            ],
            'Pop': [
                'Traditional Pop', 'Schlager', 'Space Age Pop', 'Exotica', 'Psychedelic Pop',
                'Baroque Pop', 'Canción melódica', 'Sunshine Pop', 'French Pop', 'Italo Pop',
                'Yé-yé', 'Progressive Pop', 'Adult Contemporary', 'Jazz Pop', 'Europop',
                'City Pop', 'Idol kayō', 'Turkish Pop', 'New Music', 'Euro-Disco', 'Synthpop',
                'Dance-Pop', 'Art Pop', 'Sophisti-Pop', 'Jangle Pop', 'Alternative Dance',
                'Ethereal Wave', 'Dance-R&B', 'New Romantic', 'Mandopop', 'Cantopop',
                'Korean Ballad', 'Nederpop', 'Techno kayō', 'Dream Pop', 'Ambient Pop',
                'Indie Pop', 'Chamber Pop', 'Twee Pop', 'Dreamgaze', 'Baggy', 'Shibuya-kei',
                'Eurodance', 'Bubblegum Dance', 'Electropop', 'Electro Dance-Pop', 'K-Pop',
                'Indietronica', 'Ethereal Indie Pop', 'Glitch Pop', 'Bitpop', 'K-R&B',
                'New Rave', 'Crunkcore', 'Alt-Pop', 'Hypnagogic Pop', 'Bedroom Pop',
                'Chillwave', 'Soulful Art Pop', 'Neo-Psych Pop', 'Millenial Pop', 'Hyperpop',
                'Flamenco Pop', 'Enka', 'Easy Listening', 'J-Pop', 'K-Pop'
            ],
            'Hip Hop': [
                'Disco Rap', 'Miami Bass', 'Boom Bap', 'West Coast Hip Hop', 'Hardcore Hip Hop',
                'Southern Hip Hop', 'Jazz Rap', 'Pop Rap', 'Conscious Hip Hop', 'Instrumental Hip Hop',
                'G-Funk', 'Horrorcore', 'Dirty South', 'Memphis Rap', 'U.K. Hip Hop',
                'French Hip Hop', 'Mobb Music', 'Rap Boricua', 'Japanese Hip Hop', 'Chopped And Screwed',
                'Chicano Rap', 'Bounce', 'Turntablism', 'Trap', 'Abstract Hip Hop', 'Experimental Hip Hop',
                'Industrial Hip Hop', 'Grime', 'Ritmo y Poesía', 'Club Rap', 'Crunk', 'Hyphy',
                'Nerdcore Hip Hop', 'Drumless', 'Grimey Sound', 'Cloud Rap', 'Pop Trap', 'Plugg',
                'Chicago Drill', 'U.K. Drill', 'Emo Rap', 'Phonk', 'Trap Metal', 'Lo-Fi Hip Hop',
                'Country Rap', 'Sweg', 'Detroit Trap', 'Sample Drill', 'Rage', 'Sigilkore'
            ],
            'Afroamericana': [
                'Gospel', 'Delta Blues', 'Vaudeville Blues', 'Acoustic Texas Blues', 'Piedmont Blues',
                'Jug Band', 'Boogie Woogie', 'Acoustic Chicago Blues', 'Rhythm & Blues', 'Jump Blues',
                'Chicago Blues', 'New Orleans R&B', 'Doo-Wop', 'Southern Soul', 'Funk', 'Psych Soul',
                'Pop Soul', 'Motown', 'Texas Blues', 'British R&B', 'Disco', 'Smooth Soul', 'P-Funk',
                'Latin Funk', 'Euro-Disco', 'Philly Soul', 'Chicago Soul', 'Contemporary R&B', 'Synth Funk',
                'New Jack Swing', 'Boogie', 'Britfunk', 'Neo-Soul', 'Hill Country Blues', 'Nu-Disco',
                'Alt R&B', 'Funktronica', 'Trap Soul', 'Highlife'
            ],
            'Folk': [
                'Contemporary Folk', 'Psychedelic Folk', 'Folk Pop', 'American Primitivism', 'Chamber Folk',
                'Progressive Folk', 'Avant-Folk', 'Britfolk', 'Neofolk', 'Indie Folk', 'Anti-Folk',
                'Freak Folk', 'Dark Folk', 'Folktronica', 'Free Folk', 'Convenience Folk', 'Drone Folk',
                'Industrial Folk (Martial Folk)', 'Ensemble Folk', 'Slowfolk', 'Slacker Folk',
                'Rumba flamenca', 'Rumba catalana', 'Flamenco', 'Flamenco nuevo', 'Celtic Folk Music',
                'Asturian Folk Music', 'Galician Folk Music', 'Irish Folk Music', 'Breton Celtic Folk',
                'Celtic New Age', 'Mariachi', 'Folk Fusion', 'Country'
            ],
            'Jamaica': [
                'Ska', 'Rocksteady', 'Reggae', 'Dub', 'Pop Reggae', 'Lovers Rock', 'Deejay', 'Dancehall',
                '2 Tone', 'Digital Dancehall', 'Third Wave Ska', 'Ragga'
            ],
            'Jazz': [
                'Dixieland', 'Stride', 'Swing', 'British Dance Band', 'Vocal Swing', 'Jazz manouche',
                'Bebop', 'Vocal Jazz', 'Progressive Big Band', 'Hard Bop', 'Cool Jazz', 'Latin Jazz',
                'Samba-jazz', 'Afro-Cuban Jazz', 'Post-Bop', 'Jazz Fusion', 'Avant-Garde Jazz',
                'Third Stream', 'Spiritual Jazz', 'Free Jazz', 'Soul Jazz', 'Jazzpel', 'Chamber Jazz',
                'Afro-Jazz', 'Jazz-Funk', 'ECM Style Jazz', 'Smooth Jazz', 'Experimental Big Band',
                'Cape Jazz', 'European Free Jazz', 'Flamenco Jazz', 'New Age', 'Swing Revival', 'Yass',
                'Dark Jazz', 'Neo Soul Jazz', 'Space Jazz', 'Beat Jazz'
            ],
            'Electronica': [
                'Ambient', 'Dark Ambient', 'Experimental Ambient', 'IDM', 'Electro', 'Electroclash', 'Breakbeat',
                'Big Beat', 'Downtempo', 'Trip Hop', 'Glitch', 'Drum & Bass', 'Jungle', 'Liquid Funk', 'Neurofunk',
                'Dubstep', 'Brostep', 'Future Garage', 'UK Garage', '2-Step', 'Speed Garage', 'Bassline',
                'Footwork', 'Juke', 'Hardcore Techno', 'Happy Hardcore', 'Gabber', 'Breakcore',
                'Digital Hardcore', 'Acid House', 'Chicago House', 'Deep House', 'Progressive House',
                'Tech House', 'Electro House', 'French House', 'Minimal Techno', 'Detroit Techno',
                'Berlin Techno', 'Acid Techno', 'Trance', 'Goa Trance', 'Psytrance', 'Uplifting Trance',
                'Progressive Trance', 'Eurodance', 'Hands Up', 'Synthwave', 'Retrowave', 'Vaporwave',
                'Chiptune', 'Bitpop', 'Electro Swing', 'Future Bass', 'Trap EDM', 'Moombahton',
                'Complextro', 'Witch House', 'Darkwave', 'New Beat', 'Industrial', 'EBM', 'Aggrotech',
                'Electropunk', 'Electroacoustic', 'Experimental Electronica', 'Microhouse', 'Lo-Fi House',
                'Lo-Fi Beats', 'Braindance', 'Sequencer & Tracker', 'Celtic Electronica', 'Ethereal Wave',
                'Electronic'
            ],
            'Clásica': [
                'Música Medieval', 'Música Renacentista', 'Música Barroca', 'Música Clásica (Período)',
                'Música Romántica', 'Música Impresionista', 'Música Nacionalista', 'Música Moderna',
                'Música Contemporánea', 'Música Serial', 'Música Dodecafónica', 'Música Aleatoria',
                'Música Minimalista', 'Música Electroacústica', 'Música Coral', 'Música de Cámara',
                'Música Sinfónica', 'Música Concertante', 'Música Sacra', 'Música Litúrgica',
                'Música para Piano', 'Música para Órgano', 'Música para Guitarra Clásica',
                'Música para Cuerda', 'Música para Viento', 'Música para Percusión', 'Música Vocal',
                'Ópera', 'Opereta', 'Oratorio', 'Cantata', 'Música Ballet', 'Música para Cine',
                'Música para Banda', 'Música para Ensamble', 'Música Experimental Clásica',
                'Música Neoclásica', 'Música Postminimalista', 'Música Microtonal', 'Música Espacial',
                'Música Programática', 'Música Absoluta', 'Avant-Garde Music', 'Ballet', 'Band Music',
                'Chamber Music', 'Choral', 'Classical Crossover', 'Concerto', 'Electronic/Computer Music',
                'Fight Songs', 'Film Score', 'Keyboard', 'Marches', 'Military', 'Miscellaneous (Classical)',
                'Opera', 'Orchestral', 'Show/Musical', 'Symphony', 'Vocal Music', "Film Soundtrack", "Orchestral Music", 
                'Cinematic Classical', 'Television Music', 'Impressionism', 'Modern Classical', 'Romanticism', 'Film Score',
                'Spaghetti Western', 'Post-Minimalism'
            ],
            "Otros": [
                'Video Game Music', 'Poetry', 'Compilation', 'Spoken Word', 'Big Music', 'Sound Effects', 'Singer-Songwriter'
            ]
        }

        # Diccionario inverso para búsquedas rápidas de padre por subgénero
        self.parent_map = {}
        for parent, children in self.genres.items():
            for child in children:
                self.parent_map[child] = parent

    def get_parent(self, subgenre):
        return self.parent_map.get(subgenre)

    def get_children(self, genre):
        return self.genres.get(genre, [])

    def add_genre(self, parent, subgenres):
        if parent not in self.genres:
            self.genres[parent] = []
        self.genres[parent].extend(subgenres)
        for subgenre in subgenres:
            self.parent_map[subgenre] = parent

    def is_subgenre(self, genre):
        return genre in self.parent_map

    def is_main_genre(self, genre):
        return genre in self.genres

    def search_genre(self, query):
        results = []
        for genre in self.parent_map:
            if query.lower() in genre.lower():
                results.append((genre, self.parent_map[genre]))
        return results

    def get_all_main_genres(self):
        return list(self.genres.keys())

    def get_all_subgenres(self):
        return list(self.parent_map.keys())


if __name__ == "__main__":
    music = MusicGenres()
    print("Géneros principales disponibles:", music.get_all_main_genres())
    print("Padre de 'Dubstep':", music.get_parent("Dubstep"))
    print("Padre de 'K-Pop':", music.get_parent("K-Pop"))
    print("Subgéneros de 'Jazz':", len(music.get_children("Jazz")))
    rock_genres = music.search_genre("rock")
    print(f"Géneros con 'rock' en el nombre: {len(rock_genres)} encontrados")
