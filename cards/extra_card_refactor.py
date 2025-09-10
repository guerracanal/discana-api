# extra_card_refactor.py
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Iterable, Sequence, Tuple, Dict, Any, List, Optional
import logging
import os
import re

import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

from cards.music_genres import MusicGenres
from cards.mongo_utils import get_mood_descriptors

# ───────────────────────────────────────── LOGGING
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

# ───────────────────────────────────────── FONDO MOODS
N_MOOD_LINES: int = 20
WORDS_PER_LINE: int = 10
LINE_SPACING_FACTOR: float = 0.30
MOOD_BG_MAX_FONT: int = 300
MOOD_BG_MIN_FONT: int = 250
MOOD_BG_COLOR: Tuple[int, int, int, int] = (220, 220, 220, 80)
EXTEND_FACTOR: float = 3.5
ANGLE_MOOD_BG: int = 45
MOOD_WORD_SPACING: int = 60

# ───────────────────────────────────────── ICONOS / CÍRCULOS
ICON_SIZE: int = 600
CIRCLE_RADIUS: int = ICON_SIZE // 2
CIRCLE_GAP: int = 150
ICON_GAP: int = 150

# Paleta por década (fondo) y color de texto asociado
DECADE_COLORS: List[Tuple[int, int, Tuple[int, int, int]]] = [
    (0,    1960, (214, 162, 162)),   # <60s rojizo suave
    (1960, 1970, (240, 180, 120)),   # 60s naranja
    (1970, 1980, (245, 210, 110)),   # 70s amarillo cálido
    (1980, 1990, (170, 210, 130)),   # 80s verde fresco
    (1990, 2000, (120, 200, 160)),   # 90s verde agua
    (2000, 2010, (110, 175, 220)),   # 00s azul cielo
    (2010, 2020, (150, 130, 210)),   # 10s violeta
    (2020, 2100, (210, 140, 210)),   # 20s lila
]
DECADE_TEXT_COLORS: List[Tuple[int, int, Tuple[int, int, int]]] = [
    (0,    1960, (40,  40,  40)),
    (1960, 1970, (40,  30,  10)),
    (1970, 1980, (40,  40,  10)),
    (1980, 1990, (30,  50,  30)),
    (1990, 2000, (30,  50,  40)),
    (2000, 2010, (255, 255, 255)),
    (2010, 2020, (255, 255, 255)),
    (2020, 2100, (255, 255, 255)),
]

# Paleta por duración (fondo) y color de texto asociado
DURATION_COLORS: List[Tuple[int, int, Tuple[int, int, int]]] = [
    (0,   31,  (200, 230, 250)),   # ≤30  azul muy claro
    (31,  46,  (150, 200, 240)),   # 31–45 azul claro
    (46,  61,  (220, 220, 220)),   # 46–60 gris claro
    (61,  76,  (250, 200, 150)),   # 61–75 naranja claro
    (76,  10000, (250, 150, 150)), # ≥76   rojo claro
]
DURATION_TEXT_COLORS: List[Tuple[int, int, Tuple[int, int, int]]] = [
    (0,   31,  (35,  45,  70)),    # azul muy claro → texto azul marino/gris frío
    (31,  46,  (255, 255, 255)),   # azul claro → blanco
    (46,  61,  (50,  50,  50)),    # gris claro → gris oscuro
    (61,  76,  (70,  40,  10)),    # naranja claro → marrón oscuro
    (76,  10000, (255, 255, 255)), # rojo claro → blanco (mejor legibilidad)
]

# Colores de géneros (para los títulos)
GENRE_COLORS: Dict[str, Tuple[int, int, int]] = {
    'Rock':        (220, 90, 90),
    'Metal':       (80, 80, 80),
    'Punk':        (240, 140, 60),
    'Pop':         (255, 120, 180),
    'Afroamericana': (60, 150, 210),
    'Jazz':        (240, 200, 60),
    'Folk':        (180, 140, 60),
    'Jamaica':     (0, 150, 70),
    'Hip Hop':     (150, 60, 180),
    'Country':     (200, 150, 90),
    'Electronica': (0, 200, 180),
    'Clasica':     (140, 120, 200),
    'Otros':       (160, 160, 160),
}
SUBGENRE_COLOR: Tuple[int, int, int] = (60, 60, 60)

GENRE_BORDER_WIDTH: int = 0

# ───────────────────────────────────────── TIPOGRAFÍA
FONT_BOLD_SIZE: int = 400
FONT_SUBGENRE_SIZE: int = 200
FONT_CIRCLE_SIZE: int = 300

# ───────────────────────────────────────── POSICIONES / MARCOS
Y_FORMAT_ROW: int = -400
Y_INFO_ROW: int = 200
GENRE_LINE_SPACING: int = 100
SUBGENRE_LINE_SPACING: int = 80
BORDER_WIDTH: int = 0
BORDER_THICKNESS: int = 0

# ───────────────────────────────────────── RUTAS
DEFAULT_RESOLUTION: Tuple[int, int, int] = (5040, 3600, 3)
DEFAULT_FONT_PATH: str = r"cards/font/BebasNeue-Regular.ttf"
DEFAULT_ICON_DIR: str = r"cards/images/icons"
DEFAULT_FLAG_DIR: str = r"cards/flags/round"

VALID_FORMATS: Dict[str, str] = {
    'vinilo': 'vinyl.png',
    'cd': 'cd.png',
    'cassette': 'cassette.png',
    'card': 'card.png',
}

MAX_SUBGENRES_PER_LINE = 3

# ───────────────────────────────────────── UTILIDADES DE COLOR
def darken_rgb(rgb: Tuple[int, int, int], factor: float = 0.75) -> Tuple[int, int, int]:
    """Oscurece un color multiplicando por `factor` (0..1)."""
    r, g, b = rgb
    return (int(r * factor), int(g * factor), int(b * factor))

def hex_to_rgba(hex_color: str, alpha: int = 80) -> Tuple[int, int, int, int]:
    s = hex_color.strip().lstrip('#')
    if len(s) == 3:
        s = ''.join(ch * 2 for ch in s)
    if not re.fullmatch(r"[0-9a-fA-F]{6}", s or ""):
        r, g, b, a = MOOD_BG_COLOR
        return (r, g, b, alpha if alpha is not None else a)
    r = int(s[0:2], 16); g = int(s[2:4], 16); b = int(s[4:6], 16)
    return (r, g, b, alpha)

# ───────────────────────────────────────── TEXTO / FUENTES
def _text_size(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> Tuple[int, int]:
    l, t, r, b = draw.textbbox((0, 0), text, font=font)
    return r - l, b - t

@lru_cache(maxsize=64)
def _load_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)

def _resolve_font_paths(font_path: str) -> Tuple[str, str]:
    regular = font_path
    bold = font_path.replace('Regular', 'Bold') if 'Regular' in font_path else font_path
    if not os.path.exists(bold):
        bold = regular
    return bold, regular

@lru_cache(maxsize=128)
def _load_icon(path: str, size: int) -> Image.Image:
    img = Image.open(path).convert('RGBA')
    return img.resize((size, size), Image.LANCZOS)

# ───────────────────────────────────────── MAPEOS (fondo y color de texto)
def _scan_palette(value: int, table: List[Tuple[int, int, Tuple[int, int, int]]]) -> Tuple[int, int, int]:
    for start, end, color in table:
        if start <= value < end:
            return color
    return table[-1][2]

def _get_decade_color(year_str: str) -> Tuple[int, int, int]:
    try:
        y = int(year_str)
    except Exception:
        return (120, 180, 255)
    return _scan_palette(y, DECADE_COLORS)

def _get_decade_text_color(year_str: str) -> Tuple[int, int, int]:
    try:
        y = int(year_str)
    except Exception:
        return (40, 40, 40)
    return _scan_palette(y, DECADE_TEXT_COLORS)

def _get_duration_color(mins: int | str | None) -> Tuple[int, int, int]:
    try:
        m = int(mins)
    except Exception:
        return (140, 230, 180)
    return _scan_palette(m, DURATION_COLORS)

def _get_duration_text_color(mins: int | str | None) -> Tuple[int, int, int]:
    try:
        m = int(mins)
    except Exception:
        return (50, 50, 50)
    return _scan_palette(m, DURATION_TEXT_COLORS)

# ───────────────────────────────────────── OTRAS UTILIDADES
def _safe_year_from_date(date_release: Any) -> Optional[str]:
    if date_release is None:
        return None
    if isinstance(date_release, int):
        return str(date_release)[:4]
    s = str(date_release)
    m = re.search(r"(19\d{2}|20\d{2})", s)
    return m.group(1) if m else None

def _as_list(x: Any) -> List[str]:
    if x is None:
        return []
    if isinstance(x, str):
        return [x] if x.strip() else []
    if isinstance(x, Iterable):
        return [str(v) for v in x if str(v).strip()]
    return []

# ───────────────────────────────────────── RENDER CONFIG
@dataclass(frozen=True)
class RenderConfig:
    resolution: Tuple[int, int, int] = DEFAULT_RESOLUTION
    font_path: str = DEFAULT_FONT_PATH
    icon_dir: str = DEFAULT_ICON_DIR
    flag_dir: str = DEFAULT_FLAG_DIR
    text_box_position: int = 4000

music_genres = MusicGenres()

# ───────────────────────────────────────── RELOJ DE DURACIÓN
def draw_duration_clock(draw: ImageDraw.ImageDraw, cx: int, cy: int, radius: int,
                        minutes: int, base_color: Tuple[int, int, int]) -> None:
    """
    Dibuja un reloj estilo 'relleno progresivo':
      - el círculo se pinta con `base_color`
      - el sector (progreso) se pinta con un tono más oscuro de `base_color`
      - minutos se limita a [0, 60]
    """
    minutes = max(0, min(int(minutes), 60))
    bbox = [cx - radius, cy - radius, cx + radius, cy + radius]

    # Fondo del reloj (color de rango)
    draw.ellipse(bbox, fill=base_color)

    # Sector de progreso (oscurecido)
    if minutes > 0:
        extent = int(360 * minutes / 60)
        sector_color = darken_rgb(base_color, 0.75)
        draw.pieslice(bbox, start=-90, end=-90 + extent, fill=sector_color)

# ───────────────────────────────────────── BORDE DE ESQUINAS
def draw_corner_border(img_pil, genre_colors, border_width=50, triangle_size=80, base_color=(50, 50, 50)):
    card = np.array(img_pil).copy()
    h, w = card.shape[:2]

    x1, y1 = border_width, border_width
    x2, y2 = w - border_width, h - border_width

    mask = np.zeros_like(card)
    cv2.rectangle(mask, (0, 0), (w, h), base_color, thickness=-1)
    cv2.rectangle(mask, (x1, y1), (x2, y2), (0, 0, 0), thickness=-1)

    colors = genre_colors[:4]
    cc = {"tl": base_color, "tr": base_color, "bl": base_color, "br": base_color}
    if len(colors) == 1:
        cc = {k: colors[0] for k in cc}
    elif len(colors) == 2:
        cc["tl"] = cc["br"] = colors[0]; cc["tr"] = cc["bl"] = colors[1]
    elif len(colors) == 3:
        cc["tl"] = cc["br"] = colors[0]; cc["tr"] = colors[1]; cc["bl"] = colors[2]
    elif len(colors) == 4:
        cc["tl"], cc["tr"], cc["bl"], cc["br"] = colors

    off = border_width
    pts = np.array([[off, off], [off+triangle_size, off], [off, off+triangle_size]], np.int32)
    cv2.fillConvexPoly(mask, pts, cc["tl"])
    pts = np.array([[w-off, off], [w-off-triangle_size, off], [w-off, off+triangle_size]], np.int32)
    cv2.fillConvexPoly(mask, pts, cc["tr"])
    pts = np.array([[off, h-off], [off+triangle_size, h-off], [off, h-off-triangle_size]], np.int32)
    cv2.fillConvexPoly(mask, pts, cc["bl"])
    pts = np.array([[w-off, h-off], [w-off-triangle_size, h-off], [w-off, h-off-triangle_size]], np.int32)
    cv2.fillConvexPoly(mask, pts, cc["br"])

    mask_bool = np.any(mask != 0, axis=2)
    card[mask_bool] = mask[mask_bool]
    return card

# ───────────────────────────────────────── RENDER PRINCIPAL
def make_extra_card(
    genres: Sequence[str] | None,
    subgenres: Sequence[str] | None,
    moods: Sequence[str] | None,
    country: Optional[str] = None,
    format: str | Sequence[str] | None = None,
    date_release: Any = None,
    duration: Any = None,
    resolution: Tuple[int, int, int] = DEFAULT_RESOLUTION,
    text_box_position: int = 4000,
    font_path: str = DEFAULT_FONT_PATH,
    *,
    config: Optional[RenderConfig] = None,
) -> np.ndarray:

    cfg = config or RenderConfig(resolution=resolution, font_path=font_path, text_box_position=text_box_position)
    H, W, _ = cfg.resolution
    card = np.ones(cfg.resolution, np.uint8) * 255
    img_pil = Image.fromarray(card)

    # ── Fondo de moods
    mood_descriptors: List[Dict[str, Any]] = get_mood_descriptors(moods or [])
    if mood_descriptors:
        bold_path, regular_path = _resolve_font_paths(cfg.font_path)
        mood_fonts: List[ImageFont.FreeTypeFont] = []
        total = max(1, len(mood_descriptors) - 1)
        for i in range(len(mood_descriptors)):
            size = int(MOOD_BG_MAX_FONT - (MOOD_BG_MAX_FONT - MOOD_BG_MIN_FONT) * (i / total))
            try:
                font = _load_font(bold_path, size)
            except Exception:
                font = _load_font(regular_path, size)
            mood_fonts.append(font)

        ext_w = int(W * EXTEND_FACTOR); ext_h = int(H * EXTEND_FACTOR)
        bg_img = Image.new('RGBA', (ext_w, ext_h), (255, 255, 255, 0))
        bg_draw = ImageDraw.Draw(bg_img)

        line_spacing = (ext_h / (N_MOOD_LINES - 1)) * LINE_SPACING_FACTOR if N_MOOD_LINES > 1 else ext_h * LINE_SPACING_FACTOR
        def alt_index(n: int) -> int: return (n // 2) if n % 2 == 0 else -(n // 2 + 1)

        used_indices: List[int] = []; seq_n = 0
        for line in range(N_MOOD_LINES):
            if len(mood_descriptors) == 0: break
            idx_candidate = alt_index(seq_n) % len(mood_descriptors)
            if used_indices and idx_candidate == used_indices[-1]:
                seq_n = 0; idx_candidate = alt_index(seq_n) % len(mood_descriptors)
            used_indices.append(idx_candidate); seq_n += 1
            start_idx = idx_candidate

            line_words: List[Tuple[str, ImageFont.FreeTypeFont, int, Tuple[int, int, int, int]]] = []
            line_width = 0
            for i in range(WORDS_PER_LINE):
                idx = (start_idx + i) % len(mood_descriptors)
                word = str(mood_descriptors[idx].get('es') or mood_descriptors[idx].get('en') or '').upper()
                if not word: continue
                font = mood_fonts[idx]
                color_hex = str(mood_descriptors[idx].get('color') or '#000000')
                color = hex_to_rgba(color_hex, alpha=MOOD_BG_COLOR[3])
                tw, _ = _text_size(bg_draw, word, font)
                line_words.append((word, font, tw, color))
                line_width += tw + (MOOD_WORD_SPACING if i < WORDS_PER_LINE - 1 else 0)

            if not line_words: continue
            x = (ext_w - line_width) // 2
            y = int(line * line_spacing + (ext_h - (line_spacing * (N_MOOD_LINES - 1))) // 2)
            for word, font, tw, color in line_words:
                bg_draw.text((x, y), word, font=font, fill=color)
                x += tw + MOOD_WORD_SPACING

        bg_img = bg_img.rotate(ANGLE_MOOD_BG, resample=Image.BICUBIC, expand=0)
        crop = ((ext_w - W) // 2, (ext_h - H) // 2, (ext_w - W) // 2 + W, (ext_h - H) // 2 + H)
        temp_cropped = bg_img.crop(crop)
        img_pil = Image.alpha_composite(img_pil.convert('RGBA'), temp_cropped).convert('RGB')

    draw = ImageDraw.Draw(img_pil)

    # ── Texto central
    bold_path, regular_path = _resolve_font_paths(cfg.font_path)
    try:
        font_bold = _load_font(bold_path, FONT_BOLD_SIZE)
    except Exception:
        font_bold = _load_font(regular_path, FONT_BOLD_SIZE)
    subgenre_font = _load_font(regular_path, FONT_SUBGENRE_SIZE)

    genres_list = _as_list(genres)
    subgenres_list = _as_list(subgenres)

    genre_colors = [GENRE_COLORS.get(music_genres.get_parent(g), GENRE_COLORS['Otros']) for g in genres_list]

    genre_heights = [_text_size(draw, g.upper(), font_bold)[1] for g in genres_list]
    total_genres_height = sum(genre_heights) + (len(genres_list) - 1) * GENRE_LINE_SPACING

    num_subgenre_lines = (len(subgenres_list) + MAX_SUBGENRES_PER_LINE - 1) // MAX_SUBGENRES_PER_LINE
    total_subgenres_height = 0
    if num_subgenre_lines > 0:
        subgenre_line_height = _text_size(draw, "X", subgenre_font)[1]
        total_subgenres_height = num_subgenre_lines * subgenre_line_height + (num_subgenre_lines - 1) * SUBGENRE_LINE_SPACING

    total_block_height = total_genres_height + total_subgenres_height
    bottom_size = (Y_FORMAT_ROW + Y_INFO_ROW + ICON_SIZE) + GENRE_LINE_SPACING
    y_central = (img_pil.height - total_block_height) // 2 - bottom_size

    PADDING = 100  # píxeles que sobresalen a cada lado

    y_genre = y_central
    for i, g in enumerate(genres_list):
        text = g.upper()

        # Obtener bounding box del texto
        bbox = draw.textbbox((0, 0), text, font=font_bold)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

        x = (img_pil.width - text_w) // 2

        # Métricas de la fuente
        ascent, descent = font_bold.getmetrics()
        # Centro vertical real del texto
        line_y = y_genre + ascent // 2

        # Dibujar línea de fondo centrada verticalmente y con padding
        draw.line(
            (x - PADDING, line_y, x + text_w + PADDING, line_y),
            fill=genre_colors[i],
            width=150
        )

        # Dibujar texto encima
        draw.text((x, y_genre), text, font=font_bold, fill=(30, 30, 30))

        y_genre += text_h + GENRE_LINE_SPACING


    # === FILA SUPERIOR: ICONOS DE FORMATO ===
    format_icons_imgs: List[Image.Image] = []
    formats_list = _as_list(format)
    if formats_list:
        for f in formats_list:
            fkey = f.lower()
            filename = VALID_FORMATS.get(fkey)
            if not filename:
                logger.debug("Formato '%s' no reconocido; omitido", f)
                continue
            icon_path = os.path.join(cfg.icon_dir, filename)
            if os.path.exists(icon_path):
                try:
                    format_icons_imgs.append(_load_icon(icon_path, ICON_SIZE))
                except Exception as e:
                    logger.warning("No se pudo cargar icono '%s': %s", icon_path, e)
            else:
                logger.debug("Icono no encontrado: %s", icon_path)

    if format_icons_imgs:
        n_format = len(format_icons_imgs)
        total_width = n_format * ICON_SIZE + (n_format - 1) * ICON_GAP
        x0 = (W - total_width) // 2
        y_icons = cfg.text_box_position + Y_FORMAT_ROW
        for i, icon_img in enumerate(format_icons_imgs):
            x_icon = x0 + i * (ICON_SIZE + ICON_GAP)
            img_pil.paste(icon_img, (x_icon, y_icons), icon_img)



    y_subgenre = y_genre + SUBGENRE_LINE_SPACING
    for i in range(0, len(subgenres_list), MAX_SUBGENRES_PER_LINE):
        chunk = subgenres_list[i:i+MAX_SUBGENRES_PER_LINE]
        sub_text = ', '.join(chunk).upper()
        w_s, h_s = _text_size(draw, sub_text, subgenre_font)
        x = (img_pil.width - w_s) // 2
        draw.text((x, y_subgenre), sub_text, font=subgenre_font, fill=SUBGENRE_COLOR)
        y_subgenre += h_s + SUBGENRE_LINE_SPACING

    # ── Círculos: año / bandera / duración
    year = _safe_year_from_date(date_release)
    try:
        minutes = int(duration) if duration is not None else None
    except Exception:
        minutes = None

    try:
        circle_font = _load_font(bold_path, FONT_CIRCLE_SIZE)
    except Exception:
        circle_font = _load_font(regular_path, FONT_CIRCLE_SIZE)

    icon_size = CIRCLE_RADIUS * 2
    icon_gap = ICON_GAP
    line_elems: List[Dict[str, Any]] = []

    if year:
        line_elems.append({'type': 'year', 'text': year, 'color': _get_decade_color(year)})

    # Bandera
    country_icon_img: Optional[Image.Image] = None
    flag_path = None
    if country:
        code_full = country.lower()
        candidate_full = os.path.join(cfg.flag_dir, f"{code_full}.png")
        candidate2 = os.path.join(cfg.flag_dir, f"{code_full[:2]}.png") if len(code_full) >= 2 else None
        if os.path.exists(candidate_full):
            flag_path = candidate_full
        elif candidate2 and os.path.exists(candidate2):
            flag_path = candidate2
        if flag_path:
            try:
                country_icon_img = _load_icon(flag_path, icon_size)
            except Exception as e:
                logger.warning("No se pudo cargar bandera '%s': %s", flag_path, e)

    if country_icon_img:
        line_elems.append({'type': 'icon', 'img': country_icon_img})

    if minutes is not None:
        line_elems.append({'type': 'duration', 'text': str(minutes), 'color': _get_duration_color(minutes)})

    n_elems = len(line_elems)
    if n_elems > 0:
        total_width = n_elems * icon_size + (n_elems - 1) * icon_gap
        x0 = (cfg.resolution[1] - total_width) // 2
        y0 = cfg.text_box_position + Y_INFO_ROW

        for i, elem in enumerate(line_elems):
            cx = x0 + i * (icon_size + icon_gap) + icon_size // 2
            cy = y0 + icon_size // 2
            if elem['type'] in ('year', 'duration'):
                # Dibujo especializado por tipo
                if elem['type'] == 'duration' and minutes is not None:
                    # Reloj de minutos (sector sombreado)
                    draw_duration_clock(draw, cx, cy, CIRCLE_RADIUS, minutes, elem['color'])
                    text_color = _get_duration_text_color(minutes)
                else:
                    # Círculo plano (año)
                    bbox = (cx - CIRCLE_RADIUS, cy - CIRCLE_RADIUS, cx + CIRCLE_RADIUS, cy + CIRCLE_RADIUS)
                    draw.ellipse(bbox, fill=elem['color'])
                    text_color = _get_decade_text_color(elem['text'])

                # Texto centrado
                draw.text((cx, cy), elem['text'], font=circle_font, fill=text_color, anchor="mm")

            elif elem['type'] == 'icon':
                img_pil.paste(elem['img'], (cx - icon_size // 2, cy - icon_size // 2), elem['img'])

    # ── Borde de esquinas (cohesión)
    result = draw_corner_border(img_pil, genre_colors, border_width=150, triangle_size=400, base_color=(30, 30, 30))
    return result

# ───────────────────────────────────────── DEMO LOCAL

import random
import os
import cv2
from datetime import datetime

# === LISTAS DE APOYO ===

MOODS = [
    "angry","aggressive","anxious","bittersweet","calm","meditative","disturbing","energetic","manic",
    "happy","playful","lethargic","longing","mellow","soothing","passionate","quirky","romantic","sad",
    "depressive","lonely","melancholic","sombre","sensual","sentimental","uplifting","triumphant",
    "apocalyptic","cold","dark","funereal","infernal","ominous","scary","epic","ethereal","futuristic",
    "hypnotic","martial","mechanical","medieval","mysterious","natural","aquatic","desert","forest","rain",
    "tropical","nocturnal","party","pastoral","peaceful","psychedelic","ritualistic","seasonal","autumn",
    "spring","summer","winter","space","spiritual","surreal","suspenseful","tribal","urban","warm",
    "bright","storm","beach","hazy"
]

PAISES = [None, "US", "GB", "ES", "FR", "DE", "BR", "AR", "MX", "JP", "KR", "IT", "NL", "SE", "CA", "AU"]

FORMATOS_OPCIONES = [
    None,
    ["cd"],
    ["vinilo"],
    ["cd", "vinilo"],
    ["vinilo", "cd"]
]

# === CATEGORÍAS DE GÉNEROS (recortadas para el ejemplo) ===
CATEGORIAS_GENEROS = {
    "Rock": ["Garage Rock", "Math Rock", "Prog Rock", "Shoegaze"],
    "Metal": ["Heavy Metal", "Thrash Metal", "Death Metal", "Doom Metal"],
    "Punk": ["Hardcore Punk", "Ska Punk", "Pop Punk"],
    "Pop": ["Dream Pop", "Synthpop", "Art Pop"],
    "Hip Hop": ["Trap", "Boom Bap", "Jazz Rap", "West Coast Hip Hop"],
    "Jazz": ["Bebop", "Cool Jazz", "Jazz Fusion"],
    "Electronica": ["Ambient", "IDM", "Trip Hop", "House", "Techno"],
    "Folk": ["Indie Folk", "Neofolk", "Freak Folk"]
}


def generar_generos(n):
    """Devuelve n géneros de distintas categorías"""
    categorias = list(CATEGORIAS_GENEROS.keys())
    random.shuffle(categorias)
    seleccionados = []
    for cat in categorias:
        if len(seleccionados) >= n:
            break
        seleccionados.append(random.choice(CATEGORIAS_GENEROS[cat]))
    return seleccionados


def generar_subgeneros():
    """Devuelve entre 0 y 4 subgéneros aleatorios"""
    todos = sum(CATEGORIAS_GENEROS.values(), [])
    k = random.randint(0, 4)
    return random.sample(todos, k) if k > 0 else []


def generar_moods():
    """Devuelve entre 5 y 8 moods aleatorios"""
    return random.sample(MOODS, random.randint(5, 8))


def generar_pais():
    return random.choice(PAISES)


def generar_formato():
    return random.choice(FORMATOS_OPCIONES)


# === PRUEBA DEMO VARIADA ===
if __name__ == "__main__":
    os.makedirs("_out", exist_ok=True)

    decadas = list(range(1960, 2030, 10))
    duraciones_base = [25, 40, 55, 70, 85]  # progresión para que no repita siempre

    contador = 0
    for i, dec in enumerate(decadas):
        # elegir una duración distinta en cada década
        duracion = duraciones_base[i % len(duraciones_base)]

        # generar unas cuantas variaciones por década
        for _ in range(3):
            contador += 1
            num_generos = random.randint(1, 5)
            genres = generar_generos(num_generos)
            subgenres = generar_subgeneros()
            moods = generar_moods()
            pais = generar_pais()
            formato = generar_formato()
            fecha = f"01/01/{dec}"

            demo = make_extra_card(
                genres=genres,
                subgenres=subgenres,
                moods=moods,
                country=pais,
                format=formato,
                date_release=fecha,
                duration=duracion,
            )

            nombre = f"_out/test/test_card_{contador:03d}.jpg"
            cv2.imwrite(nombre, cv2.cvtColor(demo, cv2.COLOR_RGB2BGR))
            logger.info(
                f"Guardada {nombre} | decada={dec}, duracion={duracion}, "
                f"genres={genres}, subgenres={subgenres}, pais={pais}, formato={formato}, moods={moods}"
            )
