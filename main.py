import pygame
import sys
import random
import os
import math
import asyncio

# ------------------- IMPORTERA MATH-MODELL -------------------

from slot_math import (
    SYMBOLS,
    spin_grid_same_probs,
    evaluate_megaways_win,
    paytable,
    symbol_probs,
    VISIBLE_ROWS,
    NUM_REELS,
    WILD_REEL_COUNTS,
    WILD_REEL_COUNT_WEIGHTS,
    FS_MULTIPLIERS,
    FS_MULT_WEIGHTS,
)

# ------------------- WEB-OPTIMIZING FLAGS -------------------

# Web-versionen: kör helst utan ljud/musik för prestanda.
ENABLE_SOUND = True
ENABLE_MUSIC = True

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

# ------------------- KONFIG / KONSTANTER -------------------

# Lägre basupplösning för web → betydligt billigare rendering.
BASE_WIDTH = 1280
BASE_HEIGHT = 720

WINDOW_WIDTH = BASE_WIDTH
WINDOW_HEIGHT = BASE_HEIGHT

# Grid-layout
CELL_SIZE = 110  # något mindre än PC-versionen
GRID_COLS = NUM_REELS
GRID_ROWS = VISIBLE_ROWS
GRID_WIDTH = GRID_COLS * CELL_SIZE
GRID_HEIGHT = GRID_ROWS * CELL_SIZE

GRID_X = (WINDOW_WIDTH - GRID_WIDTH) // 2
GRID_Y = (WINDOW_HEIGHT - GRID_HEIGHT) // 2 + 10

# Färger
BG_BASE = (8, 8, 20)
BG_FS = (15, 10, 35)
WHITE = (255, 255, 255)
GREY = (170, 170, 170)
DARK_GREY = (40, 40, 60)
GREEN = (0, 200, 0)
RED = (200, 60, 60)
YELLOW = (255, 220, 0)
CYAN = (80, 220, 220)
ORANGE = (255, 160, 60)
BLACK = (0, 0, 0)

# Typsnitt
FONT_SMALL = pygame.font.SysFont("arial", 16)
FONT_MEDIUM = pygame.font.SysFont("arial", 22)
FONT_LARGE = pygame.font.SysFont("arial", 32)
FONT_HUGE = pygame.font.SysFont("arial", 48, bold=True)

# ------------------- SPRÅK / TEXTER -------------------

LANG_SEQUENCE = ["sv", "en", "de", "fr", "es"]

TEXT = {
    "sv": {
        "LABEL_SALDO": "Saldo",
        "LABEL_LAST_WIN": "Senaste vinst",
        "LABEL_BET": "Insats",
        "FS_SPINS_LEFT": "SPINS KVAR",
        "FS_TOTAL_WIN": "TOTAL BONUSVINST",
        "FS_THIS_SPIN": "DETTA SPINN",
        "PAYTABLE_TITLE": "Vinsttabell",
        "RULE_LINE1": "MATCHA 3, 4 ELLER 5 SYMBOLER PÅ INTILLIGGANDE HJUL",
        "RULE_LINE2": "MED START FRÅN FÖRSTA HJULET FÖR ATT VINNA",
        "INFO_TITLE": "INFO",
        "INFO_SCATTERS": "3 SCATTER-symboler triggar free spins.",
        "INFO_MAXWIN": "Maxvinst: 5000x insats.",
        "INFO_WILDS": "Under free spins kan hela wild-hjul med multiplikatorer landa.",
        "LANG_NAME": "SV",
        "BUY_TITLE": "KÖP BONUS?",
        "BUY_QUESTION": "Vill du köpa free spins för {cost:.2f} kr?",
        "BTN_YES": "JA",
        "BTN_NO": "NEJ",
        "FS_TRIGGER_TITLE": "FREE SPINS TRIGGADE!",
        "CLICK_TO_CONTINUE": "Klicka för att fortsätta",
        "BONUS_OVER_TITLE": "BONUS ÖVER",
        "BONUS_OVER_WIN": "Du vann: {amount:.2f}",
        "BIG_WIN_TITLE": "BIG WIN!",
    },
    "en": {
        "LABEL_SALDO": "Balance",
        "LABEL_LAST_WIN": "Last win",
        "LABEL_BET": "Bet",
        "FS_SPINS_LEFT": "SPINS LEFT",
        "FS_TOTAL_WIN": "TOTAL BONUS WIN",
        "FS_THIS_SPIN": "THIS SPIN",
        "PAYTABLE_TITLE": "PAYTABLE",
        "RULE_LINE1": "MATCH 3, 4 or 5 SYMBOLS ON ADJACENT REELS",
        "RULE_LINE2": "STARTING FROM THE LEFTMOST REEL TO WIN",
        "INFO_TITLE": "INFO",
        "INFO_SCATTERS": "3 SCATTER symbols trigger free spins.",
        "INFO_MAXWIN": "Max win: 5000x bet.",
        "INFO_WILDS": "During free spins, full wild reels with multipliers can land.",
        "LANG_NAME": "EN",
        "BUY_TITLE": "BUY BONUS?",
        "BUY_QUESTION": "Do you want to buy free spins for {cost:.2f} kr?",
        "BTN_YES": "YES",
        "BTN_NO": "NO",
        "FS_TRIGGER_TITLE": "FREE SPINS TRIGGERED!",
        "CLICK_TO_CONTINUE": "Click to continue",
        "BONUS_OVER_TITLE": "BONUS OVER",
        "BONUS_OVER_WIN": "You won: {amount:.2f}",
        "BIG_WIN_TITLE": "BIG WIN!",
    },
    "de": {
        "LABEL_SALDO": "Guthaben",
        "LABEL_LAST_WIN": "Letzter Gewinn",
        "LABEL_BET": "Einsatz",
        "FS_SPINS_LEFT": "SPINS ÜBRIG",
        "FS_TOTAL_WIN": "GESAMT BONUSGEWINN",
        "FS_THIS_SPIN": "DIESER SPIN",
        "PAYTABLE_TITLE": "GEWINNTABELLE",
        "RULE_LINE1": "TREFFE 3, 4 ODER 5 SYMBOLE AUF BENACHBARTEN WALZEN",
        "RULE_LINE2": "BEGINNEND AUF DER LINKEN WALZE, UM ZU GEWINNEN",
        "INFO_TITLE": "INFO",
        "INFO_SCATTERS": "3 SCATTER-Symbole lösen Freispiele aus.",
        "INFO_MAXWIN": "Maximalgewinn: 5000x Einsatz.",
        "INFO_WILDS": "Während der Freispiele können volle Wild-Walzen mit Multiplikatoren landen.",
        "LANG_NAME": "DE",
        "BUY_TITLE": "BONUS KAUFEN?",
        "BUY_QUESTION": "Möchtest du Freispiele für {cost:.2f} kr kaufen?",
        "BTN_YES": "JA",
        "BTN_NO": "NEIN",
        "FS_TRIGGER_TITLE": "FREISPIELE AUSGELÖST!",
        "CLICK_TO_CONTINUE": "Klicken zum Fortfahren",
        "BONUS_OVER_TITLE": "BONUS VORBEI",
        "BONUS_OVER_WIN": "Du hast gewonnen: {amount:.2f}",
        "BIG_WIN_TITLE": "BIG WIN!",
    },
    "fr": {
        "LABEL_SALDO": "Solde",
        "LABEL_LAST_WIN": "Dernier gain",
        "LABEL_BET": "Mise",
        "FS_SPINS_LEFT": "TOURS RESTANTS",
        "FS_TOTAL_WIN": "GAIN TOTAL BONUS",
        "FS_THIS_SPIN": "CE TOUR",
        "PAYTABLE_TITLE": "TABLE DE GAINS",
        "RULE_LINE1": "ALIGNEZ 3, 4 OU 5 SYMBOLES SUR DES ROULEAUX ADJACENTS",
        "RULE_LINE2": "À PARTIR DU ROULEAU LE PLUS À GAUCHE POUR GAGNER",
        "INFO_TITLE": "INFO",
        "INFO_SCATTERS": "3 symboles SCATTER déclenchent les free spins.",
        "INFO_MAXWIN": "Gain max : 5000x la mise.",
        "INFO_WILDS": "Pendant les free spins, des rouleaux wilds complets avec multiplicateurs peuvent tomber.",
        "LANG_NAME": "FR",
        "BUY_TITLE": "ACHETER LE BONUS ?",
        "BUY_QUESTION": "Voulez-vous acheter des free spins pour {cost:.2f} kr ?",
        "BTN_YES": "OUI",
        "BTN_NO": "NON",
        "FS_TRIGGER_TITLE": "FREE SPINS DÉCLENCHÉS !",
        "CLICK_TO_CONTINUE": "Cliquez pour continuer",
        "BONUS_OVER_TITLE": "BONUS TERMINÉ",
        "BONUS_OVER_WIN": "Vous avez gagné : {amount:.2f}",
        "BIG_WIN_TITLE": "BIG WIN !",
    },
    "es": {
        "LABEL_SALDO": "Saldo",
        "LABEL_LAST_WIN": "Última ganancia",
        "LABEL_BET": "Apuesta",
        "FS_SPINS_LEFT": "GIROS RESTANTES",
        "FS_TOTAL_WIN": "GANANCIA TOTAL DEL BONO",
        "FS_THIS_SPIN": "ESTA TIRADA",
        "PAYTABLE_TITLE": "TABLA DE PAGOS",
        "RULE_LINE1": "ALINEA 3, 4 O 5 SÍMBOLOS EN RODILLOS ADYACENTES",
        "RULE_LINE2": "EMPEZANDO DESDE EL RODILLO MÁS A LA IZQUIERDA PARA GANAR",
        "INFO_TITLE": "INFO",
        "INFO_SCATTERS": "3 símbolos SCATTER activan los free spins.",
        "INFO_MAXWIN": "Ganancia máxima: 5000x la apuesta.",
        "INFO_WILDS": "Durante los free spins pueden aparecer rodillos wild completos con multiplicadores.",
        "LANG_NAME": "ES",
        "BUY_TITLE": "¿COMPRAR BONUS?",
        "BUY_QUESTION": "¿Quieres comprar free spins por {cost:.2f} kr?",
        "BTN_YES": "SÍ",
        "BTN_NO": "NO",
        "FS_TRIGGER_TITLE": "¡FREE SPINS ACTIVADOS!",
        "CLICK_TO_CONTINUE": "Haz clic para continuar",
        "BONUS_OVER_TITLE": "BONUS FINALIZADO",
        "BONUS_OVER_WIN": "Has ganado: {amount:.2f}",
        "BIG_WIN_TITLE": "BIG WIN!",
    },
}

BET_LEVELS = [1, 2, 4, 6, 8, 10, 15, 20, 25, 50, 100]

N_FREE_SPINS = 10
FS_BUY_MULT = 130
MAX_WIN_MULT = 5000.0

DISPLAY_NAMES = {"S": "Scatter"}

SYMBOL_COLORS = {
    "A": (255, 80, 80),
    "B": (255, 120, 80),
    "C": (255, 200, 80),
    "D": (180, 255, 80),
    "E": (80, 255, 120),
    "F": (80, 200, 255),
    "G": (120, 120, 255),
    "H": (200, 80, 255),
    "I": (255, 80, 180),
    "S": (255, 230, 50),
    "W": (200, 255, 255),
}

BIG_WIN_THRESHOLD_MULT = 30.0
BIG_WIN_DURATION_MS = 6000

SCATTER_FLASH_DURATION_MS = 1500
FS_FADEOUT_DURATION_MS = 1000
FS_AUTO_SPIN_DELAY_MS = 1100
FS_AUTO_SPIN_DELAY_WIN_MS = 2000
RETRIGGER_OVERLAY_DURATION_MS = 2200

SPIN_FIRST_STOP_MS = 700          # något snabbare
SPIN_REEL_STEP_MS = 350
SPIN_SYMBOL_CHANGE_MS = 50

WILD_DROP_STEP_MS = 250

SPIN_SYMBOLS = [s for s in SYMBOLS if s != "S"]

END_FS_FADE_DURATION_MS = 800

PAYTABLE_BTN_RADIUS = 22

# ------------------- LJUDVOLYM (SAMMA LOGIK SOM DESKTOP) -------------------

MASTER_VOLUME = 1.0              # styr både musik & SFX
MUSIC_BASE_VOLUME = 0.2          # basnivå för musik innan master/duck
music_duck_factor = 1.0          # 1.0 normalt, 0.5 vid big win-dukning

ALL_SOUNDS = []                  # alla SFX-ljud
SOUND_BASE_VOLUMES = {}          # sound -> basvolym

# ------------------- ASSETS -------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.join(BASE_DIR, "assets")


def load_sound(filename, base_volume=1.0):
    """
    Laddar ett ljud, sparar dess 'grundvolym' och applicerar MASTER_VOLUME.
    """
    if not ENABLE_SOUND:
        return None
    full_path = os.path.join(ASSET_DIR, filename)
    try:
        s = pygame.mixer.Sound(full_path)
        SOUND_BASE_VOLUMES[s] = base_volume
        s.set_volume(base_volume * MASTER_VOLUME)
        ALL_SOUNDS.append(s)
        return s
    except Exception as e:
        print(f"[VARNING] kunde inte ladda ljud {full_path}: {e}")
        return None


def update_global_volume():
    """
    Anropas när MASTER_VOLUME eller music_duck_factor ändras.
    Justerar alla SFX + musikvolym.
    """
    if ENABLE_SOUND:
        for s in ALL_SOUNDS:
            try:
                base = SOUND_BASE_VOLUMES.get(s, 1.0)
                s.set_volume(base * MASTER_VOLUME)
            except Exception:
                pass

    if ENABLE_MUSIC:
        try:
            pygame.mixer.music.set_volume(
                MUSIC_BASE_VOLUME * MASTER_VOLUME * music_duck_factor
            )
        except Exception:
            pass


SND_SPIN_START = load_sound("s_spin_start.wav", 0.6)
SND_REEL_STOP = load_sound("s_reel_stop.wav", 0.4)
SND_WIN_SMALL = load_sound("s_win_small.wav", 0.5)
SND_WIN_BIG = load_sound("s_win_big.wav", 0.8)
SND_SCATTER_HIT = load_sound("s_scatter_hit.wav", 0.7)
SND_FS_TRIGGER = load_sound("s_fs_trigger.wav", 0.9)
SND_RETRIGGER = load_sound("s_retrigger.wav", 0.9)


def play_music(mode):
    if not ENABLE_MUSIC:
        return
    try:
        if mode == "base":
            music_file = os.path.join(ASSET_DIR, "music_base.wav")
        else:
            music_file = os.path.join(ASSET_DIR, "music_fs.wav")

        if not os.path.exists(music_file):
            return

        pygame.mixer.music.load(music_file)
        pygame.mixer.music.set_volume(
            MUSIC_BASE_VOLUME * MASTER_VOLUME * music_duck_factor
        )
        pygame.mixer.music.play(-1)
    except Exception as e:
        print(f"[VARNING] kunde inte spela musik ({mode}): {e}")


def load_image(filename, scale_to=None):
    full_path = os.path.join(ASSET_DIR, filename)
    try:
        img = pygame.image.load(full_path)
        if pygame.display.get_surface() is not None:
            img = img.convert_alpha()
        if scale_to is not None:
            img = pygame.transform.smoothscale(img, scale_to)
        return img
    except Exception as e:
        print(f"[VARNING] kunde inte ladda {full_path}: {e}")
        return None


def load_button_image(filename, max_w, max_h):
    full_path = os.path.join(ASSET_DIR, filename)
    try:
        img = pygame.image.load(full_path)
        if pygame.display.get_surface() is not None:
            img = img.convert_alpha()
        w, h = img.get_size()
        scale = min(max_w / w, max_h / h, 1.0)
        new_size = (int(w * scale), int(h * scale))
        if new_size != (w, h):
            img = pygame.transform.smoothscale(img, new_size)
        return img
    except Exception as e:
        print(f"[VARNING] kunde inte ladda {full_path}: {e}")
        return None


def load_image_any(filenames, scale_to=None):
    for name in filenames:
        img = load_image(name, scale_to)
        if img is not None:
            return img
    return None


BG_BASE_IMG = load_image("bg_base.png", (WINDOW_WIDTH, WINDOW_HEIGHT))
BG_FS_IMG = load_image("bg_fs.png", (WINDOW_WIDTH, WINDOW_HEIGHT))

SPIN_BUTTON_IMG = load_image("spin_button.png", (120, 120))
SPIN_BUTTON_IMG_PRESSED = load_image("spin_button_pressed.png", (120, 120))
SPIN_BUTTON_IMG_DISABLED = load_image("spin_button_disabled.png", (120, 120))

BUY_BUTTON_IMG = load_button_image("buy_button.png", 220, 90)
BUY_BUTTON_IMG_DISABLED = load_button_image("buy_button_disabled.png", 220, 90)
BUY_BUTTON_IMG_PRESSED = load_button_image("buy_button_pressed.png", 220, 90)

BET_MINUS_IMG = load_button_image("bet_minus.png", 100, 70)
BET_MINUS_IMG_DISABLED = load_button_image("bet_minus_disabled.png", 100, 70)
BET_MINUS_IMG_PRESSED = load_button_image("bet_minus_pressed.png", 100, 70)

BET_PLUS_IMG = load_button_image("bet_plus.png", 100, 70)
BET_PLUS_IMG_DISABLED = load_button_image("bet_plus_disabled.png", 100, 70)
BET_PLUS_IMG_PRESSED = load_button_image("bet_plus_pressed.png", 100, 70)

FLAG_IMAGES = {}
for lang_code in LANG_SEQUENCE:
    img = load_image(f"flag_{lang_code}.png", (70, 45))
    if img is not None:
        FLAG_IMAGES[lang_code] = img

ALL_SYMBOL_FILES = [
    "A", "B", "C", "D", "E", "F", "G", "H", "I", "S",
    "W1", "W2", "W3", "W4",
]

SYMBOL_IMAGES = {}
for sym in ALL_SYMBOL_FILES:
    img = load_image(f"symbol_{sym}.png", (CELL_SIZE - 16, CELL_SIZE - 16))
    if img is not None:
        SYMBOL_IMAGES[sym] = img

# ------------------- HJÄLPMEDEL -------------------


def symbol_display(sym: str) -> str:
    return DISPLAY_NAMES.get(sym, sym)


def draw_text(surface, text, x, y, font, color=WHITE, center=False):
    img = font.render(text, True, color)
    rect = img.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surface.blit(img, rect)


def draw_round_button(surface, center, radius, text, font, color,
                      hover=False, disabled=False, pressed=False,
                      img=None, img_disabled=None, img_pressed=None):
    if img is not None:
        if disabled and img_disabled is not None:
            img_to_use = img_disabled
        elif pressed and img_pressed is not None:
            img_to_use = img_pressed
        else:
            img_to_use = img
        rect = img_to_use.get_rect(center=center)
        surface.blit(img_to_use, rect)
        return

    cx, cy = center
    if disabled:
        base_col = (90, 90, 90)
    elif hover:
        base_col = tuple(min(255, int(ch * 1.2)) for ch in color)
    else:
        base_col = color

    pygame.draw.circle(surface, base_col, center, radius)
    pygame.draw.circle(surface, WHITE, center, radius, width=2)

    if text:
        draw_text(surface, text, cx, cy, font, BLACK, center=True)


def draw_button(surface, rect, text, font, color,
                hover=False, disabled=False, img=None, img_disabled=None):
    if img is not None:
        img_to_use = img_disabled if disabled and img_disabled is not None else img
        surface.blit(img_to_use, rect)
        txt_col = BLACK
    else:
        base_col = (90, 90, 90) if disabled else color
        if hover and not disabled:
            base_col = tuple(min(255, int(ch * 1.15)) for ch in base_col)
        pygame.draw.rect(surface, base_col, rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, rect, width=2, border_radius=10)
        txt_col = BLACK if not disabled else (180, 180, 180)

    if text:
        draw_text(surface, text, rect.centerx, rect.centery, font, txt_col, center=True)


def draw_paytable_icon(surface, center, radius, hover=False):
    line_width = 4 if hover else 3
    color = WHITE
    pygame.draw.circle(surface, color, center, radius, width=line_width)
    text_surf = FONT_LARGE.render("i", True, color)
    text_rect = text_surf.get_rect(center=center)
    surface.blit(text_surf, text_rect)


def find_winning_positions(grid, paytable, wild_reels=None):
    if grid is None:
        return set()

    wild_reels = set(wild_reels or [])
    num_rows = len(grid)
    num_reels = len(grid[0]) if num_rows > 0 else 0
    win_positions = set()

    paying_symbols = set(sym for (sym, _) in paytable.keys())

    for sym in paying_symbols:
        counts_per_reel = []
        for col in range(num_reels):
            if col in wild_reels:
                count = VISIBLE_ROWS
            else:
                count = sum(1 for row in range(num_rows) if grid[row][col] == sym)
            counts_per_reel.append(count)

        consec_reels = 0
        for c in counts_per_reel:
            if c > 0:
                consec_reels += 1
            else:
                break

        if consec_reels >= 3:
            key = (sym, consec_reels)
            if key not in paytable:
                continue

            for col in range(consec_reels):
                if col in wild_reels:
                    for row in range(num_rows):
                        win_positions.add((row, col))
                else:
                    for row in range(num_rows):
                        if grid[row][col] == sym:
                            win_positions.add((row, col))

    return win_positions

# ------------------- PARTICLES (NERTRIMMAT) -------------------

particles_dust = []
particles_win = []  # vi skippar win-sparks spawn för web (men lämnar listan)


def spawn_neon_dust(game_mode):
    # betydligt lägre densitet än PC – ibland inget alls
    if random.random() < 0.4:
        color = (120, 220, 255) if game_mode == "base" else (255, 220, 90)
        particles_dust.append({
            "x": random.uniform(0, BASE_WIDTH),
            "y": random.uniform(0, BASE_HEIGHT),
            "vx": 0,
            "vy": random.uniform(0.08, 0.25),
            "life": random.uniform(1.0, 1.6),
            "size": random.randint(1, 2),
            "color": color
        })


def update_and_draw_bg_particles(surface):
    now_dt = 1 / 60
    dead = []
    for p in particles_dust:
        p["life"] -= now_dt
        if p["life"] <= 0:
            dead.append(p)
            continue
        p["y"] += p["vy"]
        pygame.draw.circle(surface, p["color"], (int(p["x"]), int(p["y"])), p["size"])
    for p in dead:
        particles_dust.remove(p)


def update_and_draw_fg_particles(surface):
    # web-version: inga logo-blixtrar, inga win-sparks (listan används ej)
    pass

# ------------------- FÖRENKLADE LOGGOR FÖR WEB -------------------


def draw_bonus_logo_electric(surface):
    title = "ELECTRIC CASSETTE SPINS"
    sub = "FREE SPINS BONUS"
    center_x = GRID_X + GRID_WIDTH // 2
    y = GRID_Y - 80
    draw_text(surface, title, center_x, y, FONT_LARGE, YELLOW, center=True)
    draw_text(surface, sub, center_x, y + 26, FONT_SMALL, CYAN, center=True)


def draw_logo_mixtape_megaways(surface):
    title = "MIXTAPE MEGAWAYS"
    sub = "ELECTRIC CASSETTE EDITION"
    center_x = GRID_X + GRID_WIDTH // 2
    y = GRID_Y - 80
    draw_text(surface, title, center_x, y, FONT_HUGE, CYAN, center=True)
    draw_text(surface, sub, center_x, y + 28, FONT_SMALL, GREY, center=True)

# ------------------- GRID-RITNING (AVSKALAD) -------------------


def draw_grid(surface, grid, font, win_positions=None, time_ms=0,
              wild_reels=None, fs_mults=None,
              wild_drop_start_times=None,
              is_spinning=False,
              reel_stop_times=None):
    if grid is None:
        return

    win_positions = win_positions or set()
    wild_reels = set(wild_reels or [])
    fs_mults = fs_mults or {}
    wild_drop_start_times = wild_drop_start_times or {}

    blink_phase = (time_ms // 220) % 2

    # Panel runt grid – enkel, inget glas/shadow
    panel_margin = 16
    extra_bottom = 40
    panel_rect = pygame.Rect(
        GRID_X - panel_margin,
        GRID_Y - panel_margin,
        GRID_WIDTH + 2 * panel_margin,
        GRID_HEIGHT + 2 * panel_margin + extra_bottom,
    )
    pygame.draw.rect(surface, (12, 12, 30), panel_rect, border_radius=18)
    pygame.draw.rect(surface, (80, 110, 180), panel_rect, width=2, border_radius=18)

    # CELLER
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            x = GRID_X + c * CELL_SIZE
            y = GRID_Y + r * CELL_SIZE
            cell_rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

            # Reel-spinning?
            reel_spinning = False
            if is_spinning and reel_stop_times is not None:
                if c < len(reel_stop_times) and time_ms < reel_stop_times[c]:
                    reel_spinning = True

            if c in wild_reels:
                base_bg = (30, 55, 100)
            else:
                base_bg = (22, 22, 42)

            pygame.draw.rect(surface, base_bg, cell_rect, border_radius=14)
            pygame.draw.rect(surface, (5, 5, 10), cell_rect, width=1, border_radius=14)

            # Vinst-overlay (utan win-sparks i web-version)
            if (r, c) in win_positions:
                if blink_phase == 0:
                    overlay_col = (255, 255, 255, 110)
                else:
                    overlay_col = (255, 240, 120, 60)
                overlay_surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                pygame.draw.rect(
                    overlay_surf,
                    overlay_col,
                    pygame.Rect(0, 0, CELL_SIZE, CELL_SIZE),
                    border_radius=14,
                )
                surface.blit(overlay_surf, (x, y))

            # Tydlig wild-ram
            if c in wild_reels:
                border_color = (80, 230, 255)
                border_width = 3
            else:
                border_color = BLACK
                border_width = 1
            pygame.draw.rect(surface, border_color, cell_rect, width=border_width, border_radius=14)

            # Symbolval (inkl. wild-drop)
            if c in wild_reels:
                if c in wild_drop_start_times:
                    elapsed = max(0, time_ms - wild_drop_start_times[c])
                    visible_rows = min(4, 1 + elapsed // WILD_DROP_STEP_MS)
                else:
                    visible_rows = 4
                if r < visible_rows:
                    sym_key = f"W{r + 1}"
                else:
                    sym_key = grid[r][c]
            else:
                sym_key = grid[r][c]

            inner_rect = cell_rect.inflate(-14, -14)
            img = SYMBOL_IMAGES.get(sym_key)

            if img is not None:
                if reel_spinning:
                    # --- Motion blur med 3 kopior (billig men snygg) ---
                    offsets_and_alpha = [(-8, 80), (0, 190), (8, 80)]
                    for dy, alpha in offsets_and_alpha:
                        tmp = img.copy()
                        tmp.set_alpha(alpha)
                        tmp_rect = tmp.get_rect(
                            center=(inner_rect.centerx, inner_rect.centery + dy)
                        )
                        surface.blit(tmp, tmp_rect)
                else:
                    img_rect = img.get_rect(center=inner_rect.center)
                    surface.blit(img, img_rect)
            else:
                sym_col = SYMBOL_COLORS.get(sym_key, WHITE)
                if reel_spinning:
                    # --- Motion blur även för fallback-färg-rutor ---
                    offsets_and_alpha = [(-8, 90), (0, 190), (8, 90)]
                    for dy, alpha in offsets_and_alpha:
                        tmp = pygame.Surface(inner_rect.size, pygame.SRCALPHA)
                        pygame.draw.rect(
                            tmp,
                            (*sym_col, alpha),
                            pygame.Rect(0, 0, inner_rect.width, inner_rect.height),
                            border_radius=10,
                        )
                        surface.blit(tmp, inner_rect.move(0, dy).topleft)
                else:
                    pygame.draw.rect(surface, sym_col, inner_rect, border_radius=10)
                    text = symbol_display(sym_key)
                    draw_text(
                        surface,
                        text,
                        x + CELL_SIZE // 2,
                        y + CELL_SIZE // 2,
                        font,
                        BLACK,
                        center=True,
                    )

    # MULTIPLIER-CIRKLAR
    circle_y = GRID_Y + GRID_HEIGHT + 22
    circle_radius = 18
    for c in range(GRID_COLS):
        cx = GRID_X + c * CELL_SIZE + CELL_SIZE // 2
        mult_val = fs_mults.get(c, 1)
        is_wild_reel = (c in wild_reels and c in fs_mults)

        if is_wild_reel:
            fill_col = (40, 30, 0)
            border_col = (255, 220, 0)
            text_col = YELLOW
        else:
            fill_col = (15, 20, 40)
            border_col = (80, 90, 130)
            text_col = GREY

        pygame.draw.circle(surface, fill_col, (cx, circle_y), circle_radius)
        pygame.draw.circle(surface, border_col, (cx, circle_y), circle_radius, 2)
        draw_text(surface, f"x{mult_val}", cx, circle_y, FONT_SMALL, text_col, center=True)

# ------------------- MAIN -------------------


async def main():
    global MASTER_VOLUME, music_duck_factor

    screen = pygame.display.set_mode((BASE_WIDTH, BASE_HEIGHT))
    pygame.display.set_caption("Megaways Slot – Web")

    game_surface = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))
    clock = pygame.time.Clock()

    render_scale = 1.0
    render_offset = (0, 0)

    reel_stop_played = [False] * GRID_COLS
    current_music_mode = "base"
    music_ducked_for_bigwin = False
    play_music("base")

    # Spelstatus
    paytable_visible = False
    paytable_mode = "paytable"
    current_language_index = 0
    balance = 13000.0
    bet_index = 0
    bet = BET_LEVELS[bet_index]

    current_grid = spin_grid_same_probs()
    last_win = 0.0
    last_win_positions = set()

    big_win_active = False
    big_win_end_time = 0

    retrigger_overlay_until = 0
    retrigger_overlay_text = ""
    retrigger_scatter_positions = set()

    wild_drop_start_times = {}

    fs_transition_active = False
    fs_transition_start = 0
    fs_transition_phase = None
    fs_flash_start = 0
    scatter_flash_positions = set()
    pending_fs_from_scatter = False

    is_spinning = False
    spin_start_time = 0
    reel_stop_times = [0] * GRID_COLS
    spin_result_applied = False
    final_grid = None

    spin_anim_grid = None
    last_spin_anim_update = 0

    game_mode = "base"
    fs_spins_left = 0
    fs_total_win = 0.0
    fs_total_mult = 0.0
    fs_last_spin_win = 0.0
    current_wild_reels = []
    current_wild_mults = {}

    bonus_state = "none"
    bonus_bought = False
    fs_next_spin_time = None
    last_bonus_total = 0.0
    message = ""

    buy_confirm_visible = False
    buy_confirm_cost = 0.0

    bet_minus_held = False
    bet_plus_held = False
    spin_held = False

    forced_scatter_spin = False

    end_fs_transition_active = False
    end_fs_transition_start = 0
    end_fs_transition_phase = None

    # Layout
    spin_radius = 60
    spin_center = (WINDOW_WIDTH - 200, WINDOW_HEIGHT - 220)
    spin_button_rect = pygame.Rect(
        spin_center[0] - spin_radius,
        spin_center[1] - spin_radius,
        spin_radius * 2,
        spin_radius * 2,
    )

    buy_w, buy_h = BUY_BUTTON_IMG.get_size() if BUY_BUTTON_IMG else (200, 80)
    minus_w, minus_h = BET_MINUS_IMG.get_size() if BET_MINUS_IMG else (80, 60)
    plus_w, plus_h = BET_PLUS_IMG.get_size() if BET_PLUS_IMG else (80, 60)

    bet_minus_rect = pygame.Rect(
        spin_center[0] - 100,
        spin_center[1] + spin_radius - 5,
        minus_w,
        minus_h,
    )
    bet_plus_rect = pygame.Rect(
        spin_center[0] + 20,
        spin_center[1] + spin_radius - 5,
        plus_w,
        plus_h,
    )

    buy_button_rect = pygame.Rect(
        GRID_X - 50 - buy_w,
        GRID_Y + GRID_HEIGHT // 2 - buy_h // 2,
        buy_w,
        buy_h,
    )

    paytable_button_rect = pygame.Rect(0, 0, PAYTABLE_BTN_RADIUS * 2, PAYTABLE_BTN_RADIUS * 2)
    paytable_button_rect.center = (40, 40)

    language_button_rect = pygame.Rect(0, 0, 80, 36)
    language_button_rect.center = (WINDOW_WIDTH - 80, 40)

    confirm_width, confirm_height = 460, 230
    confirm_rect = pygame.Rect(
        (WINDOW_WIDTH - confirm_width) // 2,
        (WINDOW_HEIGHT - confirm_height) // 2,
        confirm_width,
        confirm_height,
    )
    confirm_yes_rect = pygame.Rect(confirm_rect.left + 60, confirm_rect.bottom - 80, 130, 50)
    confirm_no_rect = pygame.Rect(confirm_rect.right - 60 - 130, confirm_rect.bottom - 80, 130, 50)

    paytable_close_rect = None
    info_toggle_rect = None

    # --- Volym-slider (samma logik som desktop) ---
    volume_slider_rect = pygame.Rect(0, 0, 220, 22)
    volume_slider_rect.center = (WINDOW_WIDTH // 2 - 420, WINDOW_HEIGHT - 90)
    volume_dragging = False

    running = True
    while running:
        dt = clock.tick(60)
        now = pygame.time.get_ticks()
        current_language = LANG_SEQUENCE[current_language_index]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                wx, wy = event.pos
                if big_win_active:
                    big_win_active = False
                    big_win_end_time = 0
                    if music_ducked_for_bigwin and ENABLE_MUSIC:
                        try:
                            music_duck_factor = 1.0
                            update_global_volume()
                        except Exception:
                            pass
                        music_ducked_for_bigwin = False
                    continue

                offset_x, offset_y = render_offset
                mx = (wx - offset_x) / render_scale
                my = (wy - offset_y) / render_scale

                # --- Volym-slider klick ---
                if volume_slider_rect.collidepoint(mx, my):
                    volume_dragging = True
                    slider_inner_left = volume_slider_rect.left + 20
                    slider_inner_right = volume_slider_rect.right - 20
                    if slider_inner_right > slider_inner_left:
                        t = (mx - slider_inner_left) / (slider_inner_right - slider_inner_left)
                        MASTER_VOLUME = max(0.0, min(1.0, t))
                        update_global_volume()
                    continue

                if fs_transition_active:
                    if fs_transition_phase in ("fade_in", "waiting_click"):
                        fs_transition_phase = "fade_out"
                        fs_transition_start = now
                        if pending_fs_from_scatter:
                            game_mode = "fs"
                            bonus_state = "running"
                            fs_next_spin_time = now + FS_AUTO_SPIN_DELAY_MS
                            pending_fs_from_scatter = False
                            if current_music_mode != "fs":
                                current_music_mode = "fs"
                                play_music("fs")
                    continue

                if end_fs_transition_active:
                    if end_fs_transition_phase in ("fade_in", "waiting_click"):
                        end_fs_transition_phase = "fade_out"
                        end_fs_transition_start = now
                        game_mode = "base"
                    continue

                if buy_confirm_visible:
                    if confirm_yes_rect.collidepoint(mx, my):
                        if balance >= buy_confirm_cost:
                            balance -= buy_confirm_cost
                            bonus_bought = True
                            message = f"Köpte free spins för {buy_confirm_cost:.2f}"

                            game_mode = "base"
                            bonus_state = "none"
                            fs_transition_active = False
                            pending_fs_from_scatter = False

                            is_spinning = True
                            spin_result_applied = False
                            spin_start_time = now
                            reel_stop_times = [
                                spin_start_time + SPIN_FIRST_STOP_MS + SPIN_REEL_STEP_MS * i
                                for i in range(GRID_COLS)
                            ]
                            final_grid = spin_grid_same_probs()

                            all_positions = [(r, c) for r in range(GRID_ROWS) for c in range(GRID_COLS)]
                            chosen = random.sample(all_positions, 3)
                            non_scatter_syms = [s for s in SYMBOLS if s != "S"]
                            for r in range(GRID_ROWS):
                                for c in range(GRID_COLS):
                                    if (r, c) in chosen:
                                        final_grid[r][c] = "S"
                                    else:
                                        if final_grid[r][c] == "S":
                                            final_grid[r][c] = random.choice(non_scatter_syms)

                            forced_scatter_spin = True

                            spin_anim_grid = [
                                [random.choice(SPIN_SYMBOLS) for _ in range(GRID_COLS)]
                                for _ in range(GRID_ROWS)
                            ]
                            last_spin_anim_update = now
                        else:
                            message = "För lite saldo för att köpa free spins!"

                        buy_confirm_visible = False
                        continue

                    elif confirm_no_rect.collidepoint(mx, my):
                        buy_confirm_visible = False
                        message = ""
                        continue

                    continue

                if paytable_visible and paytable_close_rect is not None:
                    if paytable_close_rect.collidepoint(mx, my):
                        paytable_visible = False
                        continue

                if paytable_visible and info_toggle_rect is not None:
                    if info_toggle_rect.collidepoint(mx, my):
                        paytable_mode = "info" if paytable_mode == "paytable" else "paytable"
                        continue

                if paytable_button_rect.collidepoint(mx, my):
                    if not paytable_visible:
                        paytable_visible = True
                        paytable_mode = "paytable"
                    else:
                        paytable_visible = False
                    continue

                if language_button_rect.collidepoint(mx, my):
                    current_language_index = (current_language_index + 1) % len(LANG_SEQUENCE)
                    continue

                can_change_bet = (
                    bonus_state == "none"
                    and not is_spinning
                    and game_mode == "base"
                    and not big_win_active
                    and not buy_confirm_visible
                )

                if can_change_bet and bet_minus_rect.collidepoint(mx, my) and bet_index > 0:
                    bet_index -= 1
                    bet = BET_LEVELS[bet_index]
                    bet_minus_held = True

                elif can_change_bet and bet_plus_rect.collidepoint(mx, my) and bet_index < len(BET_LEVELS) - 1:
                    bet_index += 1
                    bet = BET_LEVELS[bet_index]
                    bet_plus_held = True

                cost = FS_BUY_MULT * bet
                if (
                    bonus_state == "none"
                    and not is_spinning
                    and game_mode == "base"
                    and not big_win_active
                    and buy_button_rect.collidepoint(mx, my)
                    and not buy_confirm_visible
                ):
                    if balance >= cost:
                        buy_confirm_visible = True
                        buy_confirm_cost = cost
                    else:
                        message = "För lite saldo för att köpa free spins!"

                if (
                    bonus_state == "none"
                    and spin_button_rect.collidepoint(mx, my)
                    and not is_spinning
                    and not big_win_active
                    and not buy_confirm_visible
                ):
                    if game_mode == "base":
                        if balance < bet:
                            message = "För lite saldo för att spinna."
                        else:
                            spin_held = True
                            balance -= bet
                            is_spinning = True
                            spin_result_applied = False
                            spin_start_time = now
                            reel_stop_times = [
                                spin_start_time + SPIN_FIRST_STOP_MS + SPIN_REEL_STEP_MS * i
                                for i in range(GRID_COLS)
                            ]
                            reel_stop_played = [False] * GRID_COLS
                            final_grid = spin_grid_same_probs()

                            spin_anim_grid = [
                                [random.choice(SPIN_SYMBOLS) for _ in range(GRID_COLS)]
                                for _ in range(GRID_ROWS)
                            ]
                            last_spin_anim_update = now

                            last_win = 0.0
                            last_win_positions = set()
                            message = ""

                            if SND_SPIN_START:
                                SND_SPIN_START.play()

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                bet_minus_held = False
                bet_plus_held = False
                spin_held = False
                volume_dragging = False

            elif event.type == pygame.MOUSEMOTION:
                if volume_dragging:
                    wx, wy = event.pos
                    offset_x, offset_y = render_offset
                    mx = (wx - offset_x) / render_scale
                    my = (wy - offset_y) / render_scale

                    slider_inner_left = volume_slider_rect.left + 20
                    slider_inner_right = volume_slider_rect.right - 20
                    if slider_inner_right > slider_inner_left:
                        t = (mx - slider_inner_left) / (slider_inner_right - slider_inner_left)
                        MASTER_VOLUME = max(0.0, min(1.0, t))
                        update_global_volume()

        # AUTOSPIN FS
        if (
            game_mode == "fs"
            and bonus_state == "running"
            and not is_spinning
            and fs_spins_left > 0
            and fs_total_mult < MAX_WIN_MULT
            and not big_win_active
        ):
            if fs_next_spin_time is None:
                fs_next_spin_time = now + FS_AUTO_SPIN_DELAY_MS

            if now >= fs_next_spin_time:
                if fs_spins_left > 0:
                    fs_spins_left -= 1
                is_spinning = True
                spin_result_applied = False
                spin_start_time = now
                reel_stop_times = [
                    spin_start_time + SPIN_FIRST_STOP_MS + SPIN_REEL_STEP_MS * i
                    for i in range(GRID_COLS)
                ]
                reel_stop_played = [False] * GRID_COLS
                if SND_SPIN_START:
                    SND_SPIN_START.play()
                final_grid = spin_grid_same_probs()

                k = random.choices(
                    WILD_REEL_COUNTS, weights=WILD_REEL_COUNT_WEIGHTS, k=1
                )[0]
                if k <= 0:
                    current_wild_reels = []
                    current_wild_mults = {}
                else:
                    k = min(k, NUM_REELS)
                    current_wild_reels = sorted(
                        r for r in random.sample(range(NUM_REELS), k) if 0 <= r < NUM_REELS
                    )
                    current_wild_mults = {}
                    for r_idx in current_wild_reels:
                        m = random.choices(FS_MULTIPLIERS, weights=FS_MULT_WEIGHTS, k=1)[0]
                        current_wild_mults[r_idx] = m

                wild_drop_start_times = {}
                last_win = 0.0
                last_win_positions = set()
                message = ""
                fs_next_spin_time = None

                spin_anim_grid = [
                    [random.choice(SPIN_SYMBOLS) for _ in range(GRID_COLS)]
                    for _ in range(GRID_ROWS)
                ]
                last_spin_anim_update = now

        # SPINLOGIK
        if is_spinning:
            for c in range(GRID_COLS):
                if not reel_stop_played[c] and now >= reel_stop_times[c]:
                    if SND_REEL_STOP:
                        SND_REEL_STOP.play()
                    if final_grid is not None:
                        try:
                            if any(row[c] == "S" for row in final_grid):
                                if SND_SCATTER_HIT:
                                    SND_SCATTER_HIT.play()
                        except IndexError:
                            pass
                    reel_stop_played[c] = True

            if spin_anim_grid is not None and now - last_spin_anim_update >= SPIN_SYMBOL_CHANGE_MS:
                for r in range(GRID_ROWS):
                    for c in range(GRID_COLS):
                        if now < reel_stop_times[c]:
                            spin_anim_grid[r][c] = random.choice(SPIN_SYMBOLS)
                        else:
                            spin_anim_grid[r][c] = final_grid[r][c]
                last_spin_anim_update = now

                if game_mode == "fs" and bonus_state == "running":
                    drop_duration = (4 - 1) * WILD_DROP_STEP_MS
                    for c in current_wild_reels:
                        if c not in wild_drop_start_times and now >= reel_stop_times[c]:
                            wild_drop_start_times[c] = now
                            for j in range(c + 1, GRID_COLS):
                                reel_stop_times[j] += drop_duration

            if all(now >= t for t in reel_stop_times) and not spin_result_applied:
                is_spinning = False
                spin_result_applied = True
                current_grid = final_grid

                if big_win_active and now >= big_win_end_time:
                    big_win_active = False

                if game_mode == "base":
                    if forced_scatter_spin:
                        base_mult = 0.0
                    else:
                        base_mult = evaluate_megaways_win(current_grid, paytable) if current_grid else 0.0

                    win_amount = base_mult * bet
                    balance += win_amount
                    last_win = win_amount

                    if win_amount > 0:
                        if win_amount >= BIG_WIN_THRESHOLD_MULT * bet:
                            if SND_WIN_BIG:
                                SND_WIN_BIG.play()
                            if ENABLE_MUSIC:
                                try:
                                    music_duck_factor = 0.5
                                    update_global_volume()
                                    music_ducked_for_bigwin = True
                                except Exception:
                                    pass
                        else:
                            if SND_WIN_SMALL:
                                SND_WIN_SMALL.play()

                    if forced_scatter_spin:
                        last_win_positions = set()
                    else:
                        last_win_positions = find_winning_positions(current_grid, paytable)

                    if win_amount >= BIG_WIN_THRESHOLD_MULT * bet:
                        big_win_active = True
                        big_win_end_time = now + BIG_WIN_DURATION_MS

                    scatter_count = sum(
                        1 for row in current_grid for sym in row if sym == "S"
                    )

                    if scatter_count == 3:
                        fs_spins_left = N_FREE_SPINS
                        fs_total_win = 0.0
                        fs_total_mult = 0.0
                        fs_last_spin_win = 0.0
                        current_wild_reels = []
                        current_wild_mults = {}
                        wild_drop_start_times = {}
                        last_win_positions = set()
                        message = ""
                        bonus_state = "transition"
                        fs_next_spin_time = None

                        scatter_flash_positions = set()
                        for rr, row in enumerate(current_grid):
                            for cc, sym in enumerate(row):
                                if sym == "S":
                                    scatter_flash_positions.add((rr, cc))

                        fs_transition_active = True
                        fs_flash_start = now
                        fs_transition_phase = "flash"
                        fs_transition_start = now
                        pending_fs_from_scatter = True
                        if SND_FS_TRIGGER:
                            SND_FS_TRIGGER.play()
                    else:
                        if win_amount > 0:
                            message = f"Vinst: {win_amount:.2f}"
                        else:
                            message = ""

                    forced_scatter_spin = False

                elif game_mode == "fs":
                    base_mult = evaluate_megaways_win(
                        current_grid, paytable, wild_reels=current_wild_reels
                    )

                    spin_mult_factor = sum(current_wild_mults.values()) if current_wild_mults else 1
                    spin_mult = base_mult * spin_mult_factor
                    remaining = MAX_WIN_MULT - fs_total_mult
                    if remaining < 0:
                        remaining = 0
                    if spin_mult > remaining:
                        spin_mult = remaining

                    fs_total_mult += spin_mult
                    spin_win = spin_mult * bet
                    fs_total_win += spin_win
                    balance += spin_win
                    last_win = spin_win
                    fs_last_spin_win = spin_win

                    if spin_win > 0:
                        if spin_win >= BIG_WIN_THRESHOLD_MULT * bet:
                            if SND_WIN_BIG:
                                SND_WIN_BIG.play()
                            if ENABLE_MUSIC:
                                try:
                                    music_duck_factor = 0.5
                                    update_global_volume()
                                    music_ducked_for_bigwin = True
                                except Exception:
                                    pass
                        else:
                            if SND_WIN_SMALL:
                                SND_WIN_SMALL.play()

                    last_win_positions = find_winning_positions(
                        current_grid, paytable, wild_reels=current_wild_reels
                    )

                    if spin_win >= BIG_WIN_THRESHOLD_MULT * bet:
                        big_win_active = True
                        big_win_end_time = now + BIG_WIN_DURATION_MS

                    scatter_count_nonwild = 0
                    retrigger_scatter_positions = set()
                    for r in range(len(current_grid)):
                        for c in range(len(current_grid[0])):
                            if c in current_wild_reels:
                                continue
                            if current_grid[r][c] == "S":
                                scatter_count_nonwild += 1
                                retrigger_scatter_positions.add((r, c))

                    extra_spins = 0
                    if scatter_count_nonwild == 2:
                        extra_spins = 1
                    elif scatter_count_nonwild == 3:
                        extra_spins = 3

                    if extra_spins > 0:
                        fs_spins_left += extra_spins
                        retrigger_overlay_text = f"RETRIGGER! +{extra_spins} SPINS"
                        retrigger_overlay_until = now + RETRIGGER_OVERLAY_DURATION_MS
                        if SND_RETRIGGER:
                            SND_RETRIGGER.play()
                    else:
                        retrigger_scatter_positions = set()

                    if fs_spins_left <= 0 or fs_total_mult >= MAX_WIN_MULT:
                        last_bonus_total = fs_total_win
                        message = f"FREE SPINS över! Total: {fs_total_win:.2f}"
                        bonus_state = "finished_waiting"
                        fs_next_spin_time = None

                        end_fs_transition_active = True
                        end_fs_transition_phase = "fade_in"
                        end_fs_transition_start = now

                        if ENABLE_MUSIC:
                            try:
                                pygame.mixer.music.fadeout(1500)
                            except Exception:
                                pass
                    else:
                        if extra_spins > 0:
                            message = (
                                f"FS vinst: {spin_win:.2f} | +{extra_spins} extra spins! "
                                f"FS total: {fs_total_win:.2f} | Spins kvar: {fs_spins_left}"
                            )
                        else:
                            message = (
                                f"FS vinst: {spin_win:.2f} | "
                                f"FS total: {fs_total_win:.2f} | Spins kvar: {fs_spins_left}"
                            )

                    if bonus_state == "running":
                        delay = FS_AUTO_SPIN_DELAY_WIN_MS if (spin_win > 0 or extra_spins > 0) else FS_AUTO_SPIN_DELAY_MS
                        fs_next_spin_time = now + delay

        # --------- RITNING ---------
        surface = game_surface
        if game_mode == "fs" and BG_FS_IMG is not None:
            surface.blit(BG_FS_IMG, (0, 0))
            spawn_neon_dust("fs")
        elif game_mode == "base" and BG_BASE_IMG is not None:
            surface.blit(BG_BASE_IMG, (0, 0))
            spawn_neon_dust("base")
        else:
            surface.fill(BG_FS if game_mode == "fs" else BG_BASE)

        update_and_draw_bg_particles(surface)

        if game_mode == "fs":
            draw_bonus_logo_electric(surface)
        else:
            draw_logo_mixtape_megaways(surface)

        # FS HUD (cirkeln + rutor) – lättare variant
        if game_mode == "fs" and bonus_state in ("ready_to_start", "running", "finished_waiting"):
            left_x = GRID_X
            base_y = GRID_Y

            circle_center = (left_x - 120, base_y + 60)
            circle_radius = 50
            pygame.draw.circle(surface, (25, 25, 45), circle_center, circle_radius)
            pygame.draw.circle(surface, (120, 220, 255), circle_center, circle_radius, 3)
            draw_text(surface, TEXT[current_language]["FS_SPINS_LEFT"],
                      circle_center[0], circle_center[1] - 14,
                      FONT_SMALL, GREY, center=True)
            draw_text(surface, str(fs_spins_left),
                      circle_center[0], circle_center[1] + 10,
                      FONT_LARGE, WHITE, center=True)

            total_rect = pygame.Rect(left_x + 600, base_y, 260, 60)
            pygame.draw.rect(surface, (25, 25, 45), total_rect, border_radius=14)
            pygame.draw.rect(surface, (120, 220, 255), total_rect, width=2, border_radius=14)
            draw_text(surface, TEXT[current_language]["FS_TOTAL_WIN"],
                      total_rect.centerx, total_rect.top + 14,
                      FONT_SMALL, GREY, center=True)
            draw_text(surface, f"{fs_total_win:.2f}",
                      total_rect.centerx, total_rect.bottom - 22,
                      FONT_MEDIUM, WHITE, center=True)

            spin_rect = pygame.Rect(left_x + 600, base_y + 70, 260, 60)
            pygame.draw.rect(surface, (25, 25, 45), spin_rect, border_radius=14)
            pygame.draw.rect(surface, (120, 220, 255), spin_rect, width=2, border_radius=14)
            draw_text(surface, TEXT[current_language]["FS_THIS_SPIN"],
                      spin_rect.centerx, spin_rect.top + 14,
                      FONT_SMALL, GREY, center=True)
            draw_text(surface, f"{fs_last_spin_win:.2f}",
                      spin_rect.centerx, spin_rect.bottom - 22,
                      FONT_MEDIUM, WHITE, center=True)

        now_ms = pygame.time.get_ticks()
        if game_mode == "fs" and bonus_state == "running":
            if is_spinning:
                active_wild_reels = set(wild_drop_start_times.keys())
            else:
                active_wild_reels = set(current_wild_reels)
        else:
            active_wild_reels = None

        if is_spinning and spin_anim_grid is not None:
            grid_to_draw = spin_anim_grid
            grid_win_positions = set()
        else:
            grid_to_draw = current_grid
            if fs_transition_active and fs_transition_phase == "flash":
                flash_elapsed = now_ms - fs_flash_start
                if flash_elapsed < SCATTER_FLASH_DURATION_MS:
                    grid_win_positions = scatter_flash_positions
                else:
                    grid_win_positions = last_win_positions
            else:
                grid_win_positions = last_win_positions

        if (
            game_mode == "fs"
            and bonus_state == "running"
            and now < retrigger_overlay_until
            and retrigger_scatter_positions
        ):
            grid_win_positions = set(grid_win_positions).union(retrigger_scatter_positions)

        draw_grid(
            surface,
            grid_to_draw,
            FONT_MEDIUM,
            win_positions=grid_win_positions,
            time_ms=now_ms,
            wild_reels=active_wild_reels,
            fs_mults=current_wild_mults if game_mode == "fs" and bonus_state == "running" else None,
            wild_drop_start_times=wild_drop_start_times,
            is_spinning=is_spinning,
            reel_stop_times=reel_stop_times if is_spinning else None,
        )

        # --- UI knappar ---
        wx, wy = pygame.mouse.get_pos()
        offset_x, offset_y = render_offset
        mouse_pos = (
            (wx - offset_x) / render_scale,
            (wy - offset_y) / render_scale,
        )

        hover_minus = bet_minus_rect.collidepoint(mouse_pos)
        hover_plus = bet_plus_rect.collidepoint(mouse_pos)

        bet_buttons_base_disabled = (
            game_mode != "base"
            or big_win_active
            or is_spinning
            or bonus_state != "none"
            or buy_confirm_visible
        )

        minus_at_min = (bet_index == 0)
        plus_at_max = (bet_index == len(BET_LEVELS) - 1)

        minus_disabled = bet_buttons_base_disabled or minus_at_min
        plus_disabled = bet_buttons_base_disabled or plus_at_max

        if minus_disabled:
            minus_img = BET_MINUS_IMG_DISABLED
        elif bet_minus_held:
            minus_img = BET_MINUS_IMG_PRESSED
        else:
            minus_img = BET_MINUS_IMG

        draw_button(
            surface,
            bet_minus_rect,
            "",
            FONT_LARGE,
            RED,
            hover_minus and not minus_disabled,
            disabled=minus_disabled,
            img=minus_img,
            img_disabled=None,
        )

        if plus_disabled:
            plus_img = BET_PLUS_IMG_DISABLED
        elif bet_plus_held:
            plus_img = BET_PLUS_IMG_PRESSED
        else:
            plus_img = BET_PLUS_IMG

        draw_button(
            surface,
            bet_plus_rect,
            "",
            FONT_LARGE,
            GREEN,
            hover_plus and not plus_disabled,
            disabled=plus_disabled,
            img=plus_img,
            img_disabled=None,
        )

        hover_spin = spin_button_rect.collidepoint(mouse_pos)
        spin_label = "SPIN" if game_mode == "base" else "FS"
        spin_disabled = (
            big_win_active
            or buy_confirm_visible
            or bonus_state != "none"
            or (game_mode == "fs")
            or (game_mode == "base" and balance < bet)
        )

        draw_round_button(
            surface,
            spin_center,
            spin_radius,
            spin_label,
            FONT_MEDIUM,
            ORANGE,
            hover=hover_spin and not spin_disabled,
            disabled=spin_disabled,
            pressed=spin_held and not spin_disabled,
            img=SPIN_BUTTON_IMG,
            img_disabled=SPIN_BUTTON_IMG_DISABLED,
            img_pressed=SPIN_BUTTON_IMG_PRESSED,
        )

        hover_buy = buy_button_rect.collidepoint(mouse_pos)
        cost = FS_BUY_MULT * bet
        buy_disabled_input = (
            game_mode != "base"
            or big_win_active
            or is_spinning
            or bonus_state != "none"
            or buy_confirm_visible
            or balance < cost
        )

        if buy_confirm_visible:
            buy_img = BUY_BUTTON_IMG_PRESSED
        elif bonus_bought and game_mode == "fs":
            buy_img = BUY_BUTTON_IMG_PRESSED
        elif game_mode == "base" and balance < cost:
            buy_img = BUY_BUTTON_IMG_DISABLED
        else:
            buy_img = BUY_BUTTON_IMG

        draw_button(
            surface,
            buy_button_rect,
            "",
            FONT_SMALL,
            YELLOW,
            hover_buy and not buy_disabled_input,
            disabled=buy_disabled_input,
            img=buy_img,
            img_disabled=None,
        )

        hover_paytable = paytable_button_rect.collidepoint(mouse_pos)
        draw_paytable_icon(surface, paytable_button_rect.center, PAYTABLE_BTN_RADIUS, hover=hover_paytable)

        hover_lang = language_button_rect.collidepoint(mouse_pos)
        pygame.draw.rect(surface, (10, 10, 30), language_button_rect, border_radius=12)
        pygame.draw.rect(surface, (120, 220, 255), language_button_rect, width=2, border_radius=12)
        flag_img = FLAG_IMAGES.get(current_language)
        if flag_img is not None:
            flag_rect = flag_img.get_rect(center=language_button_rect.center)
            surface.blit(flag_img, flag_rect)
        else:
            lang_label = TEXT[current_language]["LANG_NAME"]
            draw_text(surface, lang_label,
                      language_button_rect.centerx, language_button_rect.centery,
                      FONT_SMALL, WHITE, center=True)

        # --- Volym-slider UI ---
        slider_inner_margin = 18
        pygame.draw.rect(surface, (10, 10, 30), volume_slider_rect, border_radius=10)
        inner = volume_slider_rect.inflate(-4, -4)
        track_y = inner.centery

        # Tom grå bar
        pygame.draw.line(
            surface,
            (60, 60, 80),
            (inner.left + slider_inner_margin, track_y),
            (inner.right - slider_inner_margin, track_y),
            4,
        )

        slider_inner_left = inner.left + slider_inner_margin
        slider_inner_right = inner.right - slider_inner_margin
        if slider_inner_right > slider_inner_left:
            filled_x = slider_inner_left + MASTER_VOLUME * (slider_inner_right - slider_inner_left)
        else:
            filled_x = slider_inner_left

        pygame.draw.line(
            surface,
            (100, 190, 255),
            (slider_inner_left, track_y),
            (filled_x, track_y),
            4,
        )

        handle_x = filled_x
        handle_radius = 8
        pygame.draw.circle(surface, (210, 230, 255), (int(handle_x), track_y), handle_radius)
        pygame.draw.circle(surface, (0, 0, 0), (int(handle_x), track_y), handle_radius, 1)

        # Label
        draw_text(
            surface,
            "VOLUME",
            volume_slider_rect.left - 40,
            volume_slider_rect.centery,
            FONT_SMALL,
            WHITE,
            center=True,
        )

        # Bottom-bar (lite billigare version)
        bottom_height = 42
        bottom_rect = pygame.Rect(
            12,
            WINDOW_HEIGHT - bottom_height - 16,
            WINDOW_WIDTH - 24,
            bottom_height,
        )
        pygame.draw.rect(surface, (10, 10, 26), bottom_rect, border_radius=16)
        pygame.draw.rect(surface, (90, 150, 220), bottom_rect, width=2, border_radius=16)

        inner_rect = bottom_rect.inflate(-8, -8)
        center_y = inner_rect.centery
        saldo_x = inner_rect.left + 160
        last_win_x = inner_rect.centerx
        bet_x = inner_rect.right - 160

        draw_text(surface, f"{TEXT[current_language]['LABEL_SALDO']}: {balance:.2f}",
                  saldo_x, center_y, FONT_SMALL, WHITE, center=True)
        draw_text(surface, f"{TEXT[current_language]['LABEL_LAST_WIN']}: {last_win:.2f}",
                  last_win_x, center_y, FONT_SMALL, WHITE, center=True)
        draw_text(surface, f"{TEXT[current_language]['LABEL_BET']}: {bet:.2f}",
                  bet_x, center_y, FONT_SMALL, WHITE, center=True)

        # Paytable overlay (lättare varianter)
        if paytable_visible:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            surface.blit(overlay, (0, 0))

            panel_w, panel_h = 900, 560
            panel_x = (WINDOW_WIDTH - panel_w) // 2
            panel_y = (WINDOW_HEIGHT - panel_h) // 2

            panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
            pygame.draw.rect(panel, (20, 20, 40), (0, 0, panel_w, panel_h), border_radius=18)
            pygame.draw.rect(panel, CYAN, (0, 0, panel_w, panel_h), width=2, border_radius=18)
            surface.blit(panel, (panel_x, panel_y))

            close_size = 28
            paytable_close_rect = pygame.Rect(
                panel_x + panel_w - close_size - 12,
                panel_y + 12,
                close_size,
                close_size,
            )

            toggle_w = 34
            toggle_h = close_size
            info_toggle_rect = pygame.Rect(
                paytable_close_rect.left - toggle_w - 8,
                paytable_close_rect.top,
                toggle_w,
                toggle_h,
            )

            hover_toggle = info_toggle_rect.collidepoint(mouse_pos)
            pygame.draw.rect(surface, (10, 10, 30), info_toggle_rect, border_radius=8)
            pygame.draw.rect(surface, (120, 220, 255), info_toggle_rect, width=2, border_radius=8)

            cx_t, cy_t = info_toggle_rect.center
            if paytable_mode == "paytable":
                pts = [(cx_t - 6, cy_t - 8), (cx_t + 6, cy_t), (cx_t - 6, cy_t + 8)]
            else:
                pts = [(cx_t + 6, cy_t - 8), (cx_t - 6, cy_t), (cx_t + 6, cy_t + 8)]
            pygame.draw.polygon(surface, WHITE, pts)

            close_hover = paytable_close_rect.collidepoint(mouse_pos)
            base_col = (200, 60, 60) if not close_hover else (255, 100, 100)
            cx, cy = paytable_close_rect.center
            r = close_size // 2 - 4
            thickness = 3
            pygame.draw.line(surface, base_col, (cx - r, cy - r), (cx + r, cy + r), thickness)
            pygame.draw.line(surface, base_col, (cx - r, cy + r), (cx + r, cy - r), thickness)

            title_key = "PAYTABLE_TITLE" if paytable_mode == "paytable" else "INFO_TITLE"
            draw_text(surface, TEXT[current_language][title_key],
                      panel_x + panel_w // 2, panel_y + 32,
                      FONT_LARGE, WHITE, center=True)

            if paytable_mode == "paytable":
                pay_syms = []
                for sym in SYMBOLS:
                    if sym in ("S", "W"):
                        continue
                    if any((sym, n) in paytable for n in (3, 4, 5, 6)):
                        pay_syms.append(sym)

                cols = 3
                cell_w = panel_w // cols
                cell_h = 130
                start_y = panel_y + 80

                for idx, sym in enumerate(pay_syms):
                    col = idx % cols
                    row = idx // cols

                    cell_x = panel_x + col * cell_w
                    cell_y = start_y + row * cell_h

                    center_x = cell_x + cell_w // 2

                    img = SYMBOL_IMAGES.get(sym)
                    if img is not None:
                        img_rect = img.get_rect(center=(center_x, cell_y + 30))
                        surface.blit(img, img_rect)
                    else:
                        draw_text(surface, sym, center_x, cell_y + 30, FONT_LARGE, WHITE, center=True)

                    text_x = cell_x + 110
                    line_y = cell_y + 60

                    for multi in (6, 5, 4, 3):
                        if (sym, multi) in paytable:
                            val = paytable[(sym, multi)]
                            draw_text(
                                surface,
                                f"{multi}x = {val:.2f}",
                                text_x,
                                line_y,
                                FONT_SMALL,
                                GREY
                            )
                            line_y += 20
            else:
                info_y = panel_y + 120
                center_x = panel_x + panel_w // 2
                draw_text(surface, TEXT[current_language]["INFO_SCATTERS"],
                          center_x, info_y, FONT_MEDIUM, YELLOW, center=True)
                draw_text(surface, TEXT[current_language]["INFO_MAXWIN"],
                          center_x, info_y + 36, FONT_MEDIUM, WHITE, center=True)
                draw_text(surface, TEXT[current_language]["INFO_WILDS"],
                          center_x, info_y + 72, FONT_SMALL, GREY, center=True)

            rule_line1 = TEXT[current_language]["RULE_LINE1"]
            rule_line2 = TEXT[current_language]["RULE_LINE2"]
            draw_text(
                surface,
                rule_line1,
                panel_x + panel_w // 2,
                panel_y + panel_h - 54,
                FONT_SMALL,
                GREY,
                center=True
            )
            draw_text(
                surface,
                rule_line2,
                panel_x + panel_w // 2,
                panel_y + panel_h - 30,
                FONT_SMALL,
                GREY,
                center=True
            )

        if bonus_state == "running" and now < retrigger_overlay_until:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            surface.blit(overlay, (0, 0))
            draw_text(surface, retrigger_overlay_text,
                      WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2,
                      FONT_LARGE, YELLOW, center=True)

        update_and_draw_fg_particles(surface)

        if buy_confirm_visible:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            surface.blit(overlay, (0, 0))

            title_text = TEXT[current_language]["BUY_TITLE"]
            question_text = TEXT[current_language]["BUY_QUESTION"].format(cost=buy_confirm_cost)

            panel_surf = pygame.Surface(confirm_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(
                panel_surf,
                (10, 10, 30),
                pygame.Rect(0, 0, confirm_rect.width, confirm_rect.height),
                border_radius=18,
            )
            pygame.draw.rect(
                panel_surf,
                (120, 220, 255),
                pygame.Rect(0, 0, confirm_rect.width, confirm_rect.height),
                width=2,
                border_radius=18,
            )
            surface.blit(panel_surf, confirm_rect.topleft)

            draw_text(surface, title_text,
                      confirm_rect.centerx, confirm_rect.top + 30,
                      FONT_LARGE, YELLOW, center=True)
            draw_text(surface, question_text,
                      confirm_rect.centerx, confirm_rect.top + 80,
                      FONT_MEDIUM, WHITE, center=True)

            yes_hover = confirm_yes_rect.collidepoint(mouse_pos)
            no_hover = confirm_no_rect.collidepoint(mouse_pos)

            draw_button(surface, confirm_yes_rect, TEXT[current_language]["BTN_YES"],
                        FONT_MEDIUM, GREEN, hover=yes_hover, disabled=False)
            draw_button(surface, confirm_no_rect, TEXT[current_language]["BTN_NO"],
                        FONT_MEDIUM, RED, hover=no_hover, disabled=False)

        if fs_transition_active:
            if fs_transition_phase == "flash":
                if now - fs_flash_start >= SCATTER_FLASH_DURATION_MS:
                    fs_transition_phase = "fade_in"
                    fs_transition_start = now

            if fs_transition_phase in ("fade_in", "waiting_click", "fade_out"):
                elapsed = now - fs_transition_start
                alpha = 0

                if fs_transition_phase == "fade_in":
                    t = min(1.0, elapsed / FS_FADEOUT_DURATION_MS)
                    alpha = int(255 * t)
                    if t >= 1.0:
                        fs_transition_phase = "waiting_click"
                elif fs_transition_phase == "waiting_click":
                    alpha = 255
                elif fs_transition_phase == "fade_out":
                    t = min(1.0, elapsed / FS_FADEOUT_DURATION_MS)
                    alpha = int(255 * (1.0 - t))
                    if t >= 1.0:
                        alpha = 0
                        fs_transition_active = False
                        scatter_flash_positions = set()
                        if pending_fs_from_scatter:
                            game_mode = "fs"
                            bonus_state = "running"
                            fs_next_spin_time = now + FS_AUTO_SPIN_DELAY_MS
                            pending_fs_from_scatter = False

                if alpha > 0:
                    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
                    overlay.fill((0, 0, 0, alpha))
                    surface.blit(overlay, (0, 0))

                    title_surf = FONT_HUGE.render(TEXT[current_language]["FS_TRIGGER_TITLE"], True, YELLOW)
                    title_surf.set_alpha(alpha)
                    title_rect = title_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 20))
                    surface.blit(title_surf, title_rect)

                    sub_surf = FONT_MEDIUM.render(TEXT[current_language]["CLICK_TO_CONTINUE"], True, WHITE)
                    sub_surf.set_alpha(alpha)
                    sub_rect = sub_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 30))
                    surface.blit(sub_surf, sub_rect)

        if end_fs_transition_active:
            elapsed_end = now - end_fs_transition_start
            alpha_end = 0

            if end_fs_transition_phase == "fade_in":
                t = min(1.0, elapsed_end / END_FS_FADE_DURATION_MS)
                alpha_end = int(255 * t)
                if t >= 1.0:
                    end_fs_transition_phase = "waiting_click"
            elif end_fs_transition_phase == "waiting_click":
                alpha_end = 255
            elif end_fs_transition_phase == "fade_out":
                t = min(1.0, elapsed_end / END_FS_FADE_DURATION_MS)
                alpha_end = int(255 * (1.0 - t))
                if t >= 1.0:
                    alpha_end = 0
                    end_fs_transition_active = False
                    bonus_state = "none"
                    fs_spins_left = 0
                    fs_total_win = 0.0
                    fs_total_mult = 0.0
                    fs_last_spin_win = 0.0
                    current_wild_reels = []
                    current_wild_mults = {}
                    wild_drop_start_times = {}
                    message = ""

                    current_grid = spin_grid_same_probs()
                    last_win = 0.0
                    last_win_positions = set()

                    if current_music_mode != "base":
                        current_music_mode = "base"
                        play_music("base")

            if alpha_end > 0:
                overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, alpha_end))
                surface.blit(overlay, (0, 0))

                title_surf = FONT_HUGE.render(TEXT[current_language]["BONUS_OVER_TITLE"], True, CYAN)
                title_surf.set_alpha(alpha_end)
                title_rect = title_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
                surface.blit(title_surf, title_rect)

                win_surf = FONT_LARGE.render(
                    TEXT[current_language]["BONUS_OVER_WIN"].format(amount=last_bonus_total), True, WHITE
                )
                win_surf.set_alpha(alpha_end)
                win_rect = win_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
                surface.blit(win_surf, win_rect)

                hint_surf = FONT_MEDIUM.render(TEXT[current_language]["CLICK_TO_CONTINUE"], True, GREY)
                hint_surf.set_alpha(alpha_end)
                hint_rect = hint_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))
                surface.blit(hint_surf, hint_rect)

        if big_win_active:
            if now >= big_win_end_time:
                big_win_active = False
                if music_ducked_for_bigwin and ENABLE_MUSIC:
                    try:
                        music_duck_factor = 1.0
                        update_global_volume()
                    except Exception:
                        pass
                    music_ducked_for_bigwin = False
            else:
                overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 200))
                surface.blit(overlay, (0, 0))

                scale_phase = (now // 140) % 2
                big_font = pygame.font.SysFont("arial", 56 + 4 * scale_phase, bold=True)

                draw_text(surface, TEXT[current_language]["BIG_WIN_TITLE"],
                          WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 30,
                          big_font, YELLOW, center=True)
                draw_text(surface, f"{last_win:.2f}",
                          WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 18,
                          FONT_LARGE, WHITE, center=True)

        # SKALA TILL FÖNSTER
        window_w, window_h = screen.get_size()
        scale_x = window_w / BASE_WIDTH
        scale_y = window_h / BASE_HEIGHT
        render_scale = min(scale_x, scale_y)
        scaled_w = int(BASE_WIDTH * render_scale)
        scaled_h = int(BASE_HEIGHT * render_scale)
        offset_x = (window_w - scaled_w) // 2
        offset_y = (window_h - scaled_h) // 2
        render_offset = (offset_x, offset_y)

        scaled_surface = pygame.transform.scale(game_surface, (scaled_w, scaled_h))

        screen.fill((0, 0, 0))
        screen.blit(scaled_surface, (offset_x, offset_y))
        pygame.display.flip()

        # viktigt för pygbag
        await asyncio.sleep(0)

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
