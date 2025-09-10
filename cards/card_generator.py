from io import BytesIO
import io
import tempfile
import requests
import re
from cards.utils import custom_data, dominant_colors, rounded_rectangle, spotify_data_pull


def generator(album = None, resolution = None, icon = None, title = None, subtitle = None, image = None, details = None, jp = None):
    # Los imports pesados (numpy, cv2, PIL, skimage) solo dentro de las funciones que los usan
    import numpy as np
    import cv2
    from PIL import Image, ImageFont, ImageDraw
    global card  # declare card as a global variable

    if album is None:
        data = custom_data(image, title, subtitle)
    else:
        data = spotify_data_pull(album)
        
    print(data)
    
    # spacing: Píxeles de separación entre los diferentes elementos que se van a colocar en la carta
    spacing = 100
    # y_position: La posición vertical actual en la que estamos situando los diferentes elementos en el cartel
    y_position = 2*spacing

    # crea una matriz con la resolución indicada
    card = np.ones(resolution, np.uint8)
    card = card*255

    # define el color de fondo en función del valor de data['album_type']
    if data['album_type'] == 'single':
        color = (254, 238, 218)  #daeefe
    elif data['album_type'] == 'compilation':
        color = (225, 252, 252) #fcfce1
    else:
        color = (250, 250, 255)  #snow
        
    # asigna el color de fondo a la matriz
    #card = cv2.cvtColor(card, cv2.COLOR_GRAY2BGR)
    card[:] = color

    print(icon)
    if icon is not None:
        icon_image = add_icon_png(icon, resolution, spacing)
    else:
        icon_image = None
    
    # Crear y posicionar el arte del album
    print("Art: " + data['album_art'])
    
    album_art = pil_process_album_art(data['album_art'], resolution, spacing)
    add_album_art_to_card(album_art, resolution, spacing)
    
    # update y position for next element
    y_position += album_art.shape[0] + 3*spacing
        
    text_box_position = 4000
    add_horizontal_line(album_art.shape[0] + 100, text_box_position - 4*spacing, album_art)
    #add_horizontal_black_lines(album_art.shape[0] + 100, text_box_position - 4*spacing)

    y_position = text_box_position

    if jp is None:
        font_path = jp
    else:
        font_path = r'static/font/NotoSansJP-Regular.ttf'
        y_position += 100
    
    album_name = process_text(data['album_name'], font_path) if title is None else title
    add_title_to_card(album_name, resolution, y_position, spacing, font_path)
        
    # update y position for next element
    y_position += 3 * spacing
        
    text = process_text(data['album_artist'], font_path) if subtitle is None else subtitle
    add_subtitle_to_card(text, resolution, y_position, spacing, font_path)

    if jp is not None:
        y_position -= 100
        
    # update y position for next element
    y_position += 2*spacing
    
    text =  data['release_date'] + ' - ' +  data['playtime'] + ' (' + str(data['total_tracks']) + ')' if details is None else details
    add_details_to_card(text, resolution, y_position + 10, spacing)
    
    # update y position for next element
    y_position += 4*spacing

    #add_populaty_to_card(data['popularity'], resolution, y_position + 10, spacing)
    
    #logo = add_spotify_logo(card, resolution, spacing)
    if album is not None:
        add_spotify_code(album, data['album_type'], resolution, spacing)

    # add border to card with colors of album art
    add_border_to_card(album_art)
    add_black_border_to_card(False)
    
    # update y position for next element
    y_position += 1*spacing

    #add_popularity(data['popularity'], resolution, y_position, spacing)
    
    #add_tracks_album_to_card(card, resolution, y_position, spacing)
        
    #add_label(data['record'] + ' - ' + data['album_type'] + ' ', (spacing, resolution[0]-163))
    #add_label(data['release_date'] + ' (' + data['copyright'] + ')' , (spacing, resolution[0]-spacing))
    
    card = cv2.cvtColor(card, cv2.COLOR_BGR2RGB)

    return(card, album_name)

def pil_process_album_art(album, resolution, spacing):
    # Los imports pesados (numpy, cv2, PIL, skimage) solo dentro de las funciones que los usan
    import numpy as np
    import cv2
    from PIL import Image
    global card  # declare card as a global variable
    
    # Download the image directly to memory using BytesIO
    response = requests.get(album)
    image = Image.open(BytesIO(response.content))

    # Convert to OpenCV format
    album_art = np.array(image.convert('RGB'))
    album_art = cv2.cvtColor(album_art, cv2.COLOR_RGB2BGR)

    scale_factor = 5.4  # reduce image size by 50%
    album_art = cv2.resize(album_art, (0,0), fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_AREA)

    mask = np.zeros((album_art.shape[0], album_art.shape[1]), np.uint8)
    mask = rounded_rectangle(mask, (0,0), (album_art.shape[0], album_art.shape[1]), 0, color=(255,255,255), thickness=-1)

    art_inv = cv2.bitwise_not(album_art)
    album_art = cv2.bitwise_not(cv2.bitwise_and(art_inv, art_inv, mask=mask))

    return album_art

def process_album_art(data, resolution, spacing):
    # Los imports pesados (numpy, cv2, PIL, skimage) solo dentro de las funciones que los usan
    import numpy as np
    import cv2
    from skimage import io as skio
    import os
    global card  # declare card as a global variable

    with tempfile.NamedTemporaryFile(delete=False) as f:
        response = requests.get(data['album_art'])
        f.write(response.content)
        temp_file_name = f.name

    f = open(temp_file_name, 'wb')
    f.write(response.content)
    f.close()

    # Cambiar el nombre del archivo temporal
    os.rename(temp_file_name, temp_file_name + '.png')

    album_art = io.imread(temp_file_name + '.png')

    scale_factor = 5.4  # reduce image size by 50%
    album_art = cv2.resize(album_art, (0,0), fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_AREA)
    album_art = cv2.cvtColor(album_art, cv2.COLOR_RGB2BGR)

    mask = np.zeros((album_art.shape[0], album_art.shape[1]), np.uint8)
    mask = rounded_rectangle(mask, (0,0), (album_art.shape[0], album_art.shape[1]), 0, color=(255,255,255), thickness=-1)

    art_inv = cv2.bitwise_not(album_art)
    album_art = cv2.bitwise_not(cv2.bitwise_and(art_inv, art_inv, mask=mask))


    # Eliminar archivo temporal
    os.unlink(temp_file_name + '.png')

    # Cerrar archivo
    f.close()

    return album_art

def add_album_art_to_card(album_art, resolution, spacing):
    global card  # declare card as a global variable

    # calculate x offset to center image horizontally
    x_offset = int((resolution[1] - album_art.shape[1]) / 2)
    y_offset = spacing
    # set image in card
    card[y_offset:y_offset+album_art.shape[0], x_offset:x_offset+album_art.shape[1]] = album_art

def get_font_scale(text, resolution, spacing, font_scale_factor, thickness, margin, font_path=None):
    import cv2
    from PIL import ImageFont, ImageDraw, Image
    global card
    if font_path is None:
        for i in range(2 * spacing, 50, -5):
            i = i / margin
            textsize = cv2.getTextSize(text, cv2.FONT_HERSHEY_COMPLEX, i * font_scale_factor, thickness)
            if textsize[0][0] <= (resolution[1] - 2 * spacing):
                font_scale = i * font_scale_factor
                return (font_scale, textsize)
    else:
        for i in range(2 * spacing, 50, -5):
            i = i / margin
            font = ImageFont.truetype(font_path, int(i * font_scale_factor))
            draw = ImageDraw.Draw(Image.fromarray(card))
            # Reemplazar textsize con textbbox
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            if text_width <= (resolution[0] - 2 * spacing):
                font_scale = i * font_scale_factor
                text_height = text_bbox[3] - text_bbox[1]
                return (font_scale, ((text_width, text_height), 0))
    return (0, ((0, 0), 0))


def add_title_to_card(text, resolution, y_position, spacing, font_path=None):
    import cv2
    from PIL import ImageFont, ImageDraw, Image
    global card
    font_scale = 0
    font_scale_factor = 5
    thickness = 15

    if font_path is None:
        font_scale, textsize = get_font_scale(text, resolution, spacing, font_scale_factor, thickness, 110)
        text_width, text_height = textsize[0]
        x_position = int((resolution[1] - text_width) / 2)
        cv2.putText(card, text, (x_position, y_position), cv2.FONT_HERSHEY_COMPLEX, font_scale, (0,0,0), thickness)
    else:
        print('text jp:' + text)
        font_scale_factor = 140
        font_scale, textsize = get_font_scale(text, resolution, spacing, font_scale_factor, thickness, 110, font_path)
        text_width, text_height = textsize[0]
        x_position = int((resolution[1] - text_width) / 2)
        font = ImageFont.truetype(font_path, int(font_scale))
        img_pil = Image.fromarray(card)
        draw = ImageDraw.Draw(img_pil)
        draw.text((x_position, y_position - 400), text, font = font, fill = (0,0,0))
        card = np.array(img_pil)

    print('title:' + str(font_scale))    

def add_subtitle_to_card(text, resolution, y_position, spacing, font_path=None):
    import cv2
    from PIL import ImageFont, ImageDraw, Image
    global card
    font_scale = 0
    font_scale_factor = 4
    thickness = 10

    if font_path is None:
        font_scale, textsize = get_font_scale(text, resolution, spacing, font_scale_factor, thickness, 110)
        text_width, text_height = textsize[0]  # Obtener el ancho y alto del texto
        x_position = int((resolution[1] - text_width) / 2)  # Calcular la posición x para centrar el texto horizontalmente
        cv2.putText(card, text, (x_position, y_position), cv2.FONT_HERSHEY_COMPLEX, font_scale, (0,0,0), thickness)
    else:
        print('text jp:' + text)
        font_scale_factor = 120
        font_scale, textsize = get_font_scale(text, resolution, spacing, font_scale_factor, thickness, 110, font_path)
        text_width, text_height = textsize[0]  # Obtener el ancho y alto del texto
        x_position = int((resolution[1] - text_width) / 2)  # Calcular la posición x para centrar el texto horizontalmente
        font = ImageFont.truetype(font_path, int(font_scale))
        img_pil = Image.fromarray(card)
        draw = ImageDraw.Draw(img_pil)
        draw.text((x_position, y_position - 400), text, font = font, fill = (0,0,0))
        card = np.array(img_pil)


    print('subtitle:' + str(font_scale)) 


    
def add_details_to_card(text, resolution, y_position, spacing):
    import cv2
    global card  # declare card as a global variable
    font_scale = 0
    font_scale_factor = 5
    thickness = 2

    font_scale, textsize = get_font_scale(text, resolution, spacing, font_scale_factor, thickness, 200)

    print('details:' + str(font_scale))

    text_width = textsize[0][0]
    x_position = int((resolution[1] - text_width) / 2)  # calculate x position to center text horizontally

    cv2.putText(card, text, (x_position, y_position), cv2.FONT_HERSHEY_COMPLEX, font_scale, (0,0,0), thickness)

def add_populaty_to_card(popularity, resolution, y_position, spacing):
    import cv2
    global card  # asegurarse de que estás usando la variable global

    #text = get_popularity_level(popularity)

    font_scale_factor = 5
    thickness = 2

    font_scale, textsize = get_font_scale(popularity, resolution, spacing, font_scale_factor, thickness, 200)

    print('popularity:' + popularity)

    text_width = textsize[0][0]
    x_position = spacing  # establecer el valor de x_position al margen izquierdo de la imagen

    cv2.putText(card, popularity, (x_position, y_position), cv2.FONT_HERSHEY_COMPLEX, font_scale, (0, 0, 0), thickness)

def add_horizontal_line(y_start, y_end, album_art):
    import numpy as np
    import cv2
    global card
    
    palette = dominant_colors(album_art)
    num_colors = len(palette)
    # add horizontal line to card
    line_height = y_end - y_start
    horizontal_line = np.zeros((line_height, card.shape[1], 3), np.uint8)
    #cv2.rectangle(horizontal_line, (0, 0), (card.shape[1], thickness), color, -1)
    for i in range(num_colors):

        section_width = int(card.shape[1] / num_colors)
        x_start = section_width * i
        x_end = x_start + section_width
        cv2.rectangle(horizontal_line, (x_start, 0), (x_end, line_height), palette[i], -1)
    
    alpha = 0.5  # define alpha value between 0 (fully transparent) and 1 (fully opaque)
    beta = 1 - alpha  # calculate beta value

    # modify opacity of the rectangle
    horizontal_line = cv2.addWeighted(horizontal_line, alpha, np.ones(horizontal_line.shape, dtype=np.uint8) * 255, beta, 0, horizontal_line)

    card[y_start:y_end, :] = horizontal_line

def add_horizontal_black_lines(y_start, y_end):
    import numpy as np
    import cv2
    global card

    # add black lines above and below the colored line
    black_line_height = 5
    black_line_top = y_start - black_line_height
    black_line_bottom = y_end #+ black_line_height
    black_line = np.zeros((black_line_height, card.shape[1], 3), np.uint8)
    black_line[:] = (0, 0, 0)
    card[black_line_top:black_line_top+black_line_height, :] = black_line
    card[black_line_bottom:black_line_bottom+black_line_height, :] = black_line


def add_border_to_card(album_art):
    import numpy as np
    import cv2
    global card
    palette = dominant_colors(album_art)

    num_colors = len(palette)
    color_palette = np.ones((5, num_colors*100, 3), np.uint8)
    for i in range(num_colors):
        section = 100*(i+1)
        cv2.rectangle(color_palette, (section-100,0), (section, 100), palette[i], -1)

    # add color border to card
    border_width = 100
    border_height = card.shape[0] - 2 * border_width

    # left border
    left_border = np.zeros((border_height, border_width, 3), np.uint8)
    for i in range(num_colors):
        section = int(border_height / num_colors) * i
        cv2.rectangle(left_border, (0, section), (border_width, section + int(border_height / num_colors)), palette[i], -1)

    # right border
    right_border = np.zeros((border_height, border_width, 3), np.uint8)
    for i in range(num_colors):
        section = int(border_height / num_colors) * i
        cv2.rectangle(right_border, (0, section), (border_width, section + int(border_height / num_colors)), palette[i], -1)

    # top border
    top_border = np.zeros((border_width, card.shape[1], 3), np.uint8)
    for i in range(num_colors):
        section = int(card.shape[1] / num_colors) * i
        cv2.rectangle(top_border, (section, 0), (section + int(card.shape[1] / num_colors), border_width), palette[i], -1)

    # bottom border
    bottom_border = np.zeros((border_width, card.shape[1], 3), np.uint8)
    for i in range(num_colors):
        section = int(card.shape[1] / num_colors) * i
        cv2.rectangle(bottom_border, (section, 0), (section + int(card.shape[1] / num_colors), border_width), palette[i], -1)

    # add borders to card
    card[border_width:card.shape[0]-border_width, 0:border_width] = left_border
    card[border_width:card.shape[0]-border_width, card.shape[1]-border_width:card.shape[1]] = right_border
    card[0:border_width, :] = top_border
    card[card.shape[0]-border_width:card.shape[0], :] = bottom_border

def add_black_border_to_card(round_corners=False):
    import cv2
    import numpy as np
    global card

    border_width = 100
    thickness = 20

    # add black border inside existing border
    inner_border_width = border_width // 2
    inner_border_height = card.shape[0] - 2 * inner_border_width
    
    inner_border = np.zeros((inner_border_height, card.shape[1] - 2 * inner_border_width, 3), np.uint8)
    inner_border[:] = (0, 0, 0)
    
    if round_corners:
        # Set the corner radius
        corner_radius = 50

        # Draw the rectangle with rounded corners
        rectangle_color = (0, 0, 0)
        
        # corners
        top_left = (border_width, border_width)
        bottom_left = (border_width, card.shape[0] - border_width)
        top_right = (card.shape[1] - border_width, border_width)
        bottom_right = (card.shape[1] - border_width, card.shape[0] - border_width)

        cv2.rectangle(card, (border_width, border_width), (card.shape[1] - border_width, card.shape[0] - border_width), (0, 0, 0), thickness)
        
        cv2.ellipse(card, (top_left[0] + corner_radius, top_left[1] + corner_radius), (corner_radius, corner_radius), 0, 180, 270, rectangle_color, thickness)
        #cv2.ellipse(card, (top_left[0] + corner_radius - 20 , top_left[1] + corner_radius - 20), (corner_radius - 20, corner_radius - 20), 0, 180, 270, rectangle_color, thickness)

        cv2.ellipse(card, (top_right[0] - corner_radius, top_right[1] + corner_radius), (corner_radius, corner_radius), 270, 0, 90, rectangle_color, thickness)
        
        cv2.ellipse(card, (bottom_left[0] + corner_radius, bottom_left[1] - corner_radius), (corner_radius, corner_radius), 0, 90, 180, rectangle_color, thickness)
        
        cv2.ellipse(card, (bottom_right[0] - corner_radius, bottom_right[1] - corner_radius), (corner_radius, corner_radius), 0, 0, 90, rectangle_color, thickness)

    else:
        cv2.rectangle(card, (border_width, border_width), (card.shape[1] - border_width, card.shape[0] - border_width), (0, 0, 0), thickness)

def add_spotify_code(album, type, resolution, spacing):
    import numpy as np
    import cv2
    global card

    album_url_base = r'https://open.spotify.com/album/'
    if "?" in album:
        album = album[:album.find('?')]
    id = album[album.find(album_url_base)+len(album_url_base):]

    if type == "album":
        color = "fffafa"
    elif type == "single":
        color = "daeefe"
    elif type == "compilation":
        color = "fcfce1"
    else:
        return None

    # https://scannables.scdn.co/uri/plain/[format]/[background-color-in-hex]/[code-color-in-text]/[size]/[spotify-URI]
    url = 'https://scannables.scdn.co/uri/plain/png/'+ color + '/black/640/spotify:album:' + id

    response = requests.get(url)
    img_array = np.array(bytearray(response.content), dtype=np.uint8)

    creditslogo = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    height, width, channels = creditslogo.shape
    scale = 2.5
    new_width = int(width * scale)
    new_height = int(height * scale)

    creditslogo = cv2.resize(creditslogo, (new_width, new_height), fx=scale, fy=scale)
    logo_x = resolution[1] - spacing - creditslogo.shape[1] - int((resolution[1] - 2*spacing - creditslogo.shape[1])/2) # center position

    card[resolution[0]-spacing-creditslogo.shape[0]:resolution[0]-spacing, logo_x:logo_x+creditslogo.shape[1]] = creditslogo
        
def add_icon(image_file, right_logo, resolution, spacing):
    import cv2
    global card

    image = cv2.imread(image_file)
    image = cv2.resize(image, (200, 200))  # replace with desired size
    image_x = right_logo - spacing - image.shape[1]
    card[resolution[0]-spacing-image.shape[0]:resolution[0]-spacing, image_x:image_x+image.shape[1]] = image
    
    return image_x

def add_icon_key(image_file, resolution, spacing):
    import cv2
    global card

    image = cv2.imread("static/images/icons/" + image_file)
    image = cv2.resize(image, (400, 400))  # replace with desired size
    
    image_x = resolution[1] - spacing - image.shape[1]
    image_y = resolution[0] - spacing - image.shape[0]

    # add the image to the bottom right corner of the card
    card[image_y:image_y+image.shape[0], image_x:image_x+image.shape[1]] = image
    
    return image_x

def add_icon_png(image_file, resolution, spacing):
    import cv2
    global card

    image = cv2.imread("static/images/icons/" + image_file, cv2.IMREAD_UNCHANGED)
    image = cv2.resize(image, (300, 300))  # replace with desired size
    
    image_x = resolution[1] - spacing - image.shape[1]
    image_y = resolution[0] - spacing - image.shape[0]

    if image.shape[2] == 4:  # check if image has alpha channel
        alpha = image[:,:,3]
        # blend image with transparency onto card
        for c in range(0, 3):
            card[image_y:image_y+image.shape[0], image_x:image_x+image.shape[1], c] = (
                alpha/255.0 * image[:,:,c] + (1 - alpha/255.0) * card[
                    image_y:image_y+image.shape[0], image_x:image_x+image.shape[1], c])
    else:  # image does not have alpha channel
        card[image_y:image_y+image.shape[0], image_x:image_x+image.shape[1]] = image[:,:,0:3]
    
    return image_x
    

def add_label(text, position):
    import cv2
    global card

    cv2.putText(card, text, position, cv2.FONT_HERSHEY_PLAIN, 3.5, (0,0,0), 5)

def read_from_file(file_path):
    with open(file_path, 'r') as f:
        return [line.strip() for line in f.readlines() if line.strip()]


def remove_additions(text):
    additions = read_from_file('cards/remove_additions.txt')

    # Crear una única expresión regular para todas las adiciones
    regex = re.compile(r'\s*(?:\(\d{4}\)\s*|\d{4}\s+\w+\s*)?(?:' + '|'.join(additions) + r')\s*', re.IGNORECASE)
    
    # Aplicar la expresión regular para eliminar las adiciones del texto
    text = regex.sub('', text)
    
    return text


def remove_special_characters(text):
    replacements = (
        ("á", "a"),
        ("é", "e"),
        ("í", "i"),
        ("ó", "o"),
        ("ú", "u"),
        ("Á", "A"),
        ("É", "E"),
        ("Í", "I"),
        ("Ó", "O"),
        ("Ú", "U"),
        ("ñ", "n"),
        ("Ñ", "N"),
        ("¿", "")
    )
    for a, b in replacements:
        text = text.replace(a, b)
        
    # Eliminar caracteres especiales con expresiones regulares
    text = re.sub(r'[^\w\s:/\?\.,-]', '', text)  # Mantener letras, números, espacios y algunos signos de puntuación
    return text


def process_text(text, font_path=None):
    if font_path is None:
        text = remove_special_characters(text)    
        # Convertir a bytes y luego a ASCII para eliminar caracteres no-ASCII
        text = text.encode('ascii', 'ignore').decode('ascii')
        text = text.encode('unicode_escape').decode('utf-8')
        text = remove_additions(text)
        if len(text) > 42:
            return text[:42] + "..."
    else:
        if len(text) > 20:
            return text[:20] + "..."
    return text


def add_popularity(popularity, resolution, y_position, spacing):
    from PIL import ImageDraw, ImageFont, Image
    global card
    
    # crear un objeto de dibujo para la imagen
    draw = ImageDraw.Draw(Image.fromarray(card))
    
    # cargar la fuente y el tamaño del texto
    font = ImageFont.truetype('arial.ttf', 24)
    
    # convertir la popularidad a una cadena de texto
    text = str(popularity)
    
    # determinar el ancho y la altura del texto
    text_width, text_height = draw.textsize(text, font=font)
    
    # calcular la posición del texto
    x_position = spacing
    y_position -= text_height + spacing
    
    # dibujar un rectángulo negro detrás del texto
    draw.rectangle((x_position, y_position + text_height, x_position + text_width, y_position), fill=(0, 0, 0))
    
    # escribir el texto en el rectángulo
    draw.text((x_position, y_position), text, font=font, fill=(255, 255, 255))

if __name__ == '__main__':
    import cv2
    from PIL import Image
    album = input("Enter Spotify Album link: ")
    if album == '':
        album = 'https://open.spotify.com/album/6D9urpsOWWKtYvF6PaorGE?si=-vOP9zWNQK6Mfq55f3o4kw'
    if album.find('https://open.spotify.com/album/') == -1:
        print("Enter valid Spotify album link.")
        exit(1)

    resolution = ''
    #resolution = input("Enter height, width in pixels: ")
    if resolution == '':
        # resolution = (5100, 3300, 3)
        resolution = (5040, 3600, 3)
    else:
        resolution = list(map(int, resolution.strip().split(',')))
        resolution.append(3)

    card, album_name = generator(album, resolution, None)

    album_name = remove_special_characters(album_name)

    card = cv2.cvtColor(card, cv2.COLOR_RGB2BGR)

    cv2.imwrite("{}_card.jpg".format(album_name), card)

    Image.open("{}_card.jpg".format(album_name)).show()
