import pygame
import sys
import random
import os  # för assets-path
import math  # <-- NY
import asyncio

# Importera din matematiska modell
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

pygame.mixer.pre_init(44100, -16, 2, 512)  # <-- NYTT: bättre latency
pygame.init()

# ------------------- KONFIG / KONSTANTER -------------------
# Bas-upplösning (intern koordinatsystem)
BASE_WIDTH = 1600
BASE_HEIGHT = 1000

# Dessa används bara för layout (ändras inte vid resize)
WINDOW_WIDTH = BASE_WIDTH
WINDOW_HEIGHT = BASE_HEIGHT

# Grid-layout
CELL_SIZE = 130
GRID_COLS = NUM_REELS
GRID_ROWS = VISIBLE_ROWS
GRID_WIDTH = GRID_COLS * CELL_SIZE
GRID_HEIGHT = GRID_ROWS * CELL_SIZE
GRID_X = (WINDOW_WIDTH - GRID_WIDTH) // 2
GRID_Y = (WINDOW_HEIGHT - GRID_HEIGHT) // 2 + 10
# Färger (fallback om inga PNGs finns)
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

# Typsnitt (bas-storlekar)
FONT_SMALL = pygame.font.SysFont("arial", 18)
FONT_MEDIUM = pygame.font.SysFont("arial", 26)
FONT_LARGE = pygame.font.SysFont("arial", 36)
FONT_HUGE = pygame.font.SysFont("arial", 52, bold=True)

# ------------------- SPRÅK / TEXTER -------------------  # <-- NY
LANG_SEQUENCE = ["sv", "en", "de", "fr", "es"]            # ordning på språkknappen

TEXT = {                                                  # <-- NY
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

# Betnivåer
BET_LEVELS = [1, 2, 4, 6, 8, 10, 15, 20, 25, 50, 100]

# Free spins-konfiguration
N_FREE_SPINS = 10
FS_BUY_MULT = 130       # kostar 130x bet att köpa FS
MAX_WIN_MULT = 5000.0   # cap per bonus i bet-multiplar

# Symbolvisning – byt "S" mot "Scatter"
DISPLAY_NAMES = {
    "S": "Scatter"
}

# Färger per symbol (fallback om inga PNG:er finns)
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
    "S": (255, 230, 50),  # Scatter
    "W": (200, 255, 255),  # Wild reel symbol (fallback)
}

# Big win
BIG_WIN_THRESHOLD_MULT = 30.0  # 30x bet
BIG_WIN_DURATION_MS = 6000     # 6 sek
# FS transition (scatter trigger) timings
SCATTER_FLASH_DURATION_MS = 1500   # scatters blinkar
FS_FADEOUT_DURATION_MS = 1000      # används som duration både för fade in och fade out
# Autospin delay i FS
FS_AUTO_SPIN_DELAY_MS = 1100
# Extra delay efter en vinnande / retriggad FS
FS_AUTO_SPIN_DELAY_WIN_MS = 2000
# Overlay-tid för retrigger-meddelande
RETRIGGER_OVERLAY_DURATION_MS = 2200
# Spin-timing
SPIN_FIRST_STOP_MS = 900
SPIN_REEL_STEP_MS = 450
SPIN_SYMBOL_CHANGE_MS = 40 # <-- CHANGED: smoother reel updates
# Wild-reel drop-animation
WILD_DROP_STEP_MS = 300
# Symboler som används för spinn-animation (ingen scatter)
SPIN_SYMBOLS = [s for s in SYMBOLS if s != "S"]
# Bonus-slut-transition (FS -> base)
END_FS_FADE_DURATION_MS = 1000
PAYTABLE_BTN_RADIUS = 26  # liten "info"-cirkel uppe till vänster

# ------------------- LJUDVOLYM -------------------
MASTER_VOLUME = 1.0           # global master om du vill (kan lämnas som 1.0)
MUSIC_BASE_VOLUME = 0.2       # bas–nivå för musik
MUSIC_VOLUME = 1.0            # styrs av MUSIC–slidern (0–1)
SFX_VOLUME = 1.0              # styrs av SFX–slidern (0–1)
music_duck_factor = 1.0       # 1.0 normalt, 0.5 vid big win-duck

# Lista av (sound_objekt, base_volume)
ALL_SOUNDS = []

# ------------------- ASSET-LOADING (PNG-stöd) -------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.join(BASE_DIR, "assets")

try:
    print("ASSET_DIR:", ASSET_DIR)
    print("Filer i assets:", os.listdir(ASSET_DIR))
except Exception as e:
    print("Kunde inte läsa assets-mappen:", e)


# ------------------- LJUD -------------------  # <-- NYTT
def load_sound(filename, base_volume=1.0):
    full_path = os.path.join(ASSET_DIR, filename)
    try:
        s = pygame.mixer.Sound(full_path)
        # spara både objektet och dess "grundvolym"
        ALL_SOUNDS.append((s, base_volume))
        # initial volym: bas * SFX_VOLUME * MASTER_VOLUME
        s.set_volume(base_volume * SFX_VOLUME * MASTER_VOLUME)
        return s
    except Exception as e:
        print(f"[VARNING] kunde inte ladda ljud {full_path}: {e}")
        return None



def update_global_volume():
    """Anropa när MUSIC_VOLUME / SFX_VOLUME / MASTER_VOLUME eller duck-factor ändras."""

    # --- SFX ---
    for s, base in ALL_SOUNDS:
        try:
            s.set_volume(base * SFX_VOLUME * MASTER_VOLUME)
        except Exception:
            pass

    # --- Musik ---
    try:
        pygame.mixer.music.set_volume(
            MUSIC_BASE_VOLUME * MUSIC_VOLUME * MASTER_VOLUME * music_duck_factor
        )
    except Exception:
        pass

# Effekter – byt filnamn till dina riktiga
SND_SPIN_START      = load_sound("s_spin_start.wav",      0.7) #fixed
SND_REEL_STOP       = load_sound("s_reel_stop.wav",       0.45) #fixed
SND_BUTTON_CLICK    = load_sound("s_button_click.wav",    0.5) #dont need
SND_WIN_SMALL       = load_sound("s_win_small.wav",       0.5) #fixed
SND_WIN_BIG         = load_sound("s_win_big.wav",         0.8) #fixed
SND_SCATTER_HIT     = load_sound("s_scatter_hit.wav",     0.8) #fixed but needs change
SND_FS_TRIGGER      = load_sound("s_fs_trigger.wav",      0.9)
SND_RETRIGGER       = load_sound("s_retrigger.wav",       0.9)

# Musik – vi använder pygame.mixer.music för loopad bakgrundsmusik
def play_music(mode):
    """
    mode: 'base' eller 'fs'
    Laddar och loopar rätt musik. Fungerar även om fil saknas.
    """
    global music_duck_factor
    try:
        if mode == "base":
            music_file = os.path.join(ASSET_DIR, "music_base.wav")
        else:
            music_file = os.path.join(ASSET_DIR, "music_fs.wav")

        if not os.path.exists(music_file):
            print(f"[INFO] ingen musikfil hittades: {music_file}")
            return

        pygame.mixer.music.load(music_file)
        pygame.mixer.music.set_volume(
            MUSIC_BASE_VOLUME * MUSIC_VOLUME * MASTER_VOLUME * music_duck_factor
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

def draw_bonus_logo_electric(surface):
    """
    3D-logga för bonusen:
      'Electric Cassette Spins'
    Färgtema: gul → ljusblå → blå
    3D: mörkblå nästan svart
    Svag båge över grid-blocket.
    """

    text = "ELECTRIC CASSETTE SPINS"

    # Mitt över grid-blocket, lite ovanför
    center_x = GRID_X + GRID_WIDTH // 2
    baseline_y = GRID_Y - 130   # ungefär var mitten av texten ska hamna

    font = pygame.font.SysFont("arial", 64, bold=True)

    # Bonus colorway
    TOP = (255, 126, 0)          # brandgul
    MID = (252, 214, 10)        # gul
    BOT = (0, 255, 255)            # cyan
    side_color = (0, 0, 0)     # nästan svart-blå
    outline_color = (0, 0, 0)

    depth_vec = (2, 2)
    depth_len = 8

    def smoothstep(t: float) -> float:
        # 3t^2 - 2t^3
        return t * t * (3 - 2 * t)

    def vertical_three_gradient(surface_in):
        w, h = surface_in.get_size()
        out = pygame.Surface((w, h), pygame.SRCALPHA)
        if h <= 1:
            return surface_in.copy()

        MID_POS = 0.38  # position (0–1) where MID is placed; < 0.5 = more room for MID→BOT

        for y in range(h):
            t = y / (h - 1)  # 0..1

            if t <= MID_POS:
                # TOP -> MID from t in [0, MID_POS]
                t2 = t / MID_POS              # normalize to 0..1
                t2 = smoothstep(t2)
                col = (
                    int(TOP[0] * (1 - t2) + MID[0] * t2),
                    int(TOP[1] * (1 - t2) + MID[1] * t2),
                    int(TOP[2] * (1 - t2) + MID[2] * t2),
                )
            else:
                # MID -> BOT from t in [MID_POS, 1]
                t2 = (t - MID_POS) / (1 - MID_POS)  # normalize to 0..1
                # bias toward BOT a bit more: sqrt makes us reach BOT earlier
                t2 = smoothstep(t2) ** 0.7
                col = (
                    int(MID[0] * (1 - t2) + BOT[0] * t2),
                    int(MID[1] * (1 - t2) + BOT[1] * t2),
                    int(MID[2] * (1 - t2) + BOT[2] * t2),
                )

            pygame.draw.line(out, col, (0, y), (w, y))

        result = surface_in.copy()
        result.blit(out, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        return result

    def draw_char_on_arc(ch, center, radius, angle_rad):
        cx, cy = center

        # Punkt på cirkeln
        px = cx + radius * math.sin(angle_rad)
        py = cy - radius * math.cos(angle_rad)

        angle_deg = math.degrees(angle_rad)

        base_white = font.render(ch, True, (255, 255, 255))
        colored = vertical_three_gradient(base_white)

        w, h = colored.get_size()
        outline = pygame.Surface((w + 10, h + 10), pygame.SRCALPHA)
        ocx, ocy = (w + 10) // 2, (h + 10) // 2

        for ox, oy in [(-2,0),(2,0),(0,-2),(0,2),(-2,-2),(2,-2),(-2,2),(2,2)]:
            o = font.render(ch, True, outline_color)
            outline.blit(o, o.get_rect(center=(ocx + ox, ocy + oy)))

        outline.blit(colored, colored.get_rect(center=(ocx, ocy)))

        side = outline.copy()
        side.fill((*side_color, 255), special_flags=pygame.BLEND_RGBA_MULT)

        front_rot = pygame.transform.rotozoom(outline, -angle_deg, 1.0)
        side_rot  = pygame.transform.rotozoom(side,   -angle_deg, 1.0)

        # 3D-extrusion längs samma vektor
        for i in range(depth_len, 0, -1):
            dx = depth_vec[0] * i
            dy = depth_vec[1] * i
            surface.blit(side_rot, side_rot.get_rect(center=(px + dx, py + dy)))

        surface.blit(front_rot, front_rot.get_rect(center=(px, py)))

    # ---- Båge-setup ----
    widths = [font.size(ch)[0] for ch in text]
    letter_spacing = 0  # lite tajtare, speciellt med båge

    total_width = sum(widths) + letter_spacing * (len(text) - 1)

    total_angle_deg = 30            # svag båge
    total_angle = math.radians(total_angle_deg)

    radius = total_width / total_angle

    # Cirkelcentrum så att bågens mitt hamnar vid baseline_y
    circle_center = (center_x, baseline_y + radius)

    start_angle = -total_angle / 2.0

    x_cursor = 0.0
    for idx, ch in enumerate(text):
        w = widths[idx]
        char_center_x = x_cursor + w / 2.0
        frac = char_center_x / total_width
        angle = start_angle + frac * total_angle

        if ch != " ":
            draw_char_on_arc(ch, circle_center, radius, angle)

        x_cursor += w + letter_spacing

def draw_logo_mixtape_megaways(surface):

    center_x = GRID_X + GRID_WIDTH // 2
    target_arc_y = GRID_Y - 170
    meg_y        = GRID_Y - 75

    mix_text = "MIXTAPE"
    meg_text = "MEGAWAYS"

    mix_font = pygame.font.SysFont("arial", 110, bold=True)
    meg_font = pygame.font.SysFont("arial", 60, bold=True)

    # BEHÅLLER DINA FÄRGER
    MIX_TOP = (150, 240, 255)
    MIX_BOTTOM = (50, 90, 180)
    MEG_TOP = (200, 250, 255)
    MEG_BOTTOM = (80, 130, 210)

    # NU: EXTREMT MÖRK 3D-FÄRG
    side_color = (5, 10, 25)          # nästan svart blå — passar temat
    outline_color = (0, 0, 0)

    # Tydligare, men stadig 3D
    depth_vec = (2, 2)
    depth_len = 8

    def apply_vertical_gradient(text_surf, top_col, bot_col):
        w, h = text_surf.get_size()
        grad = pygame.Surface((w, h), pygame.SRCALPHA)
        for y in range(h):
            t = y / h
            r = int(top_col[0] * (1 - t) + bot_col[0] * t)
            g = int(top_col[1] * (1 - t) + bot_col[1] * t)
            b = int(top_col[2] * (1 - t) + bot_col[2] * t)
            pygame.draw.line(grad, (r, g, b), (0, y), (w, y))
        result = text_surf.copy()
        result.blit(grad, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        return result

    # ----------- 3D FÖR HELA YTAN (inkl outline!) --------------
    def extrude_3d(surface, img, cx, cy):
        for i in range(depth_len, 0, -1):
            dx = depth_vec[0] * i
            dy = depth_vec[1] * i
            rect = img.get_rect(center=(cx + dx, cy + dy))
            surface.blit(img, rect)

    # ============= MEGAWAYS ==============
    def draw_3d_flat(text, font, cx, cy, top_col, bot_col):

        base_white = font.render(text, True, (255, 255, 255))
        colored = apply_vertical_gradient(base_white, top_col, bot_col)

        # ---- SKAPA OUTLINE-LAGER ----
        w, h = colored.get_size()
        outline_surf = pygame.Surface((w + 8, h + 8), pygame.SRCALPHA)
        ocx, ocy = (w + 8)//2, (h + 8)//2
        for ox, oy in [(-2,0),(2,0),(0,-2),(0,2),(-2,-2),(-2,2),(2,-2),(2,2)]:
            o = font.render(text, True, outline_color)
            outline_surf.blit(o, o.get_rect(center=(ocx+ox, ocy+oy)))

        outline_surf.blit(colored, colored.get_rect(center=(ocx, ocy)))

        # ---- 3D EXTRUSION (NU ÄVEN OUTLINE!) ----
        # Först gör vi ett mörkt lager av hela outline_surf
        side_surf = outline_surf.copy()
        side_surf.fill((side_color[0], side_color[1], side_color[2], 255),
                       special_flags=pygame.BLEND_RGBA_MULT)

        extrude_3d(surface, side_surf, cx, cy)

        # ---- FRÄMRE LAGRET ----
        surface.blit(outline_surf, outline_surf.get_rect(center=(cx, cy)))

    # ============ MIXTAPE ==============
    def draw_char_on_arc(ch, font, center, radius, angle, top_col, bot_col):
        cx, cy = center
        px = cx + radius * math.sin(angle)
        py = cy - radius * math.cos(angle)
        angle_deg = math.degrees(angle)

        base_white = font.render(ch, True, (255,255,255))
        colored = apply_vertical_gradient(base_white, top_col, bot_col)

        w, h = colored.get_size()
        outline_surf = pygame.Surface((w+8, h+8), pygame.SRCALPHA)
        ocx, ocy = (w+8)//2, (h+8)//2
        for ox, oy in [(-2,0),(2,0),(0,-2),(0,2),(-2,-2),(-2,2),(2,-2),(2,2)]:
            o = font.render(ch, True, outline_color)
            outline_surf.blit(o, o.get_rect(center=(ocx+ox, ocy+oy)))
        outline_surf.blit(colored, colored.get_rect(center=(ocx,ocy)))

        # Mörk 3D-version av hela bokstaven inkl outline
        side_surf = outline_surf.copy()
        side_surf.fill((side_color[0], side_color[1], side_color[2], 255),
                       special_flags=pygame.BLEND_RGBA_MULT)

        # rotera båda
        front_rot = pygame.transform.rotozoom(outline_surf, -angle_deg, 1.0)
        side_rot  = pygame.transform.rotozoom(side_surf,   -angle_deg, 1.0)

        # extrudera outline + färg
        for i in range(depth_len, 0, -1):
            dx = depth_vec[0] * i
            dy = depth_vec[1] * i
            surface.blit(side_rot, side_rot.get_rect(center=(px+dx, py+dy)))

        # främre lagret
        surface.blit(front_rot, front_rot.get_rect(center=(px, py)))


    # ========== BÅGEN ==========
    letter_spacing = -5
    widths = [mix_font.size(ch)[0] for ch in mix_text]
    total_width = sum(widths) + letter_spacing * (len(widths)-1)

    total_angle = math.radians(30)     # svag båge
    radius = total_width / total_angle
    circle_center = (center_x, target_arc_y + radius)
    start_angle = -total_angle / 2

    x = 0
    for idx, ch in enumerate(mix_text):
        w = widths[idx]
        frac = (x + w/2) / total_width
        angle = start_angle + frac * total_angle
        draw_char_on_arc(ch, mix_font, circle_center, radius, angle,
                         MIX_TOP, MIX_BOTTOM)
        x += w + letter_spacing

    # ---- MEGAWAYS ----
    draw_3d_flat(meg_text, meg_font, center_x, meg_y, MEG_TOP, MEG_BOTTOM)

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

SPIN_BUTTON_IMG = load_image("spin_button.png", (140, 140))
SPIN_BUTTON_IMG_PRESSED = load_image("spin_button_pressed.png", (140, 140))
SPIN_BUTTON_IMG_DISABLED = load_image("spin_button_disabled.png", (140, 140))

BUY_BUTTON_IMG = load_button_image("buy_button.png", 260, 100)
BUY_BUTTON_IMG_DISABLED = load_button_image("buy_button_disabled.png", 260, 100)
BUY_BUTTON_IMG_PRESSED = load_button_image("buy_button_pressed.png", 260, 100)

BET_MINUS_IMG = load_button_image("bet_minus.png", 120, 80)
BET_MINUS_IMG_DISABLED = load_button_image("bet_minus_disabled.png", 120, 80)
BET_MINUS_IMG_PRESSED = load_button_image("bet_minus_pressed.png", 120, 80)

BET_PLUS_IMG = load_button_image("bet_plus.png", 120, 80)
BET_PLUS_IMG_DISABLED = load_button_image("bet_plus_disabled.png", 120, 80)
BET_PLUS_IMG_PRESSED = load_button_image("bet_plus_pressed.png", 120, 80)

# --- Språkflaggor ---
FLAG_IMAGES = {}
for lang_code in LANG_SEQUENCE:   # ["sv", "en", "de", "fr", "es"]
    img = load_image(f"flag_{lang_code}.png", (80, 50))
    if img is not None:
        FLAG_IMAGES[lang_code] = img
    else:
        print(f"[VARNING] kunde inte ladda flagga: flag_{lang_code}.png")

ALL_SYMBOL_FILES = [
    "A", "B", "C", "D", "E", "F", "G", "H", "I", "S",
    "W1", "W2", "W3", "W4",
]

SYMBOL_IMAGES = {}
for sym in ALL_SYMBOL_FILES:
    img = load_image(f"symbol_{sym}.png", (CELL_SIZE - 20, CELL_SIZE - 20))
    if img is not None:
        SYMBOL_IMAGES[sym] = img
    else:
        print(f"[VARNING] Hittade inte PNG: symbol_{sym}.png")


# ------------------- HJÄLPFUNKTIONER -------------------
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
    cx, cy = center
    if img is not None:
        if disabled and img_disabled is not None:
            img_to_use = img_disabled
        elif pressed and img_pressed is not None:
            img_to_use = img_pressed
        else:
            img_to_use = img
        rect = img_to_use.get_rect(center=center)
        surface.blit(img_to_use, rect)
    else:
        if disabled:
            base_col = (90, 90, 90)
        elif hover:
            base_col = tuple(min(255, int(ch * 1.2)) for ch in color)
        else:
            base_col = color

        pygame.draw.circle(surface, base_col, center, radius)
        pygame.draw.circle(surface, WHITE, center, radius, width=3)

def draw_button(surface, rect, text, font, color,
                hover=False, disabled=False, img=None, img_disabled=None):
    if img is not None:
        img_to_use = img_disabled if disabled and img_disabled is not None else img
        surface.blit(img_to_use, rect)
        txt_col = BLACK
    else:
        base_col = color
        if disabled:
            base_col = (90, 90, 90)
        elif hover:
            base_col = tuple(min(255, int(ch * 1.2)) for ch in color)
        pygame.draw.rect(surface, base_col, rect, border_radius=14)
        pygame.draw.rect(surface, WHITE, rect, width=2, border_radius=14)
        txt_col = BLACK if not disabled else (180, 180, 180)

    if text:
        draw_text(surface, text, rect.centerx, rect.centery - 1, font, txt_col, center=True)

def draw_paytable_icon(surface, center, radius, hover=False):
    """Vit ihålig cirkel med ett 'i' inuti."""
    line_width = 4 if hover else 3
    color = WHITE

    # Ihålig cirkel
    pygame.draw.circle(surface, color, center, radius, width=line_width)

    # Litet 'i' i mitten
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

# ========================================================
# PARTICLE SYSTEM – Global lists
# ========================================================
particles_logo = []
particles_dust = []
particles_win = []
particles_fs_strips = []

# ========================================================
# NEON DUST – konstant glitter i bakgrunden
# ========================================================
def spawn_neon_dust(game_mode):
    color = (120, 220, 255) if game_mode == "base" else (255, 220, 90)
    for _ in range(2):  # light density
        particles_dust.append({
            "x": random.uniform(0, BASE_WIDTH),
            "y": random.uniform(0, BASE_HEIGHT),
            "vx": 0,
            "vy": random.uniform(0.1, 0.4),
            "life": random.uniform(1.2, 2.0),
            "size": random.randint(1, 3),
            "color": color
        })

# ========================================================
# WIN SPARKS – liten explosion i en vinnande cell
# ========================================================
def spawn_win_sparks(x, y):
    for _ in range(10):
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(1.0, 3.0)
        particles_win.append({
            "x": x,
            "y": y,
            "vx": math.cos(angle) * speed,
            "vy": math.sin(angle) * speed,
            "life": random.uniform(0.2, 0.4),
            "size": random.randint(2, 3),
            "color": (255, 255, 180)
        })

# ========================================================
# UPDATE + DRAW ALL PARTICLES
# ========================================================
def update_and_draw_bg_particles(surface):       # <-- NY
    """Ritar bara bakgrunds-partiklar (neon dust) bakom grid."""
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

def update_and_draw_fg_particles(surface):       # <-- NY
    """Ritar logo-sparks och win-sparks ovanpå grid."""
    now_dt = 1 / 60

    # LOGO SPARKS – 'riktiga' blixtar som bara fade:ar (ingen ormrörelse)
    dead = []
    for p in particles_logo:
        p["life"] -= now_dt
        if p["life"] <= 0:
            dead.append(p)
            continue

        max_life = p.get("max_life", 0.1)
        t = max(0.0, min(1.0, p["life"] / max_life))

        base_col = p["color"]

        # lätt flicker för att det ska kännas elektriskt
        flicker = 0.8 + 0.4 * random.random()

        # beräkna färg + clamp till [0, 255]  <-- FIX
        r = int(base_col[0] * (0.4 + 0.6 * t) * flicker)
        g = int(base_col[1] * (0.4 + 0.6 * t) * flicker)
        b = int(base_col[2] * (0.6 + 0.4 * t) * flicker)

        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))

        col = (r, g, b)

        thickness = p.get("thickness", 2)

        pts = [(int(x), int(y)) for (x, y) in p["points"]]

        # yttre glow
        glow_col = (
            int(col[0] * 0.4),
            int(col[1] * 0.4),
            int(col[2] * 0.7),
        )
        pygame.draw.lines(
            surface,
            glow_col,
            False,
            pts,
            thickness + 2,
        )
        # inre kärna
        pygame.draw.lines(surface, col, False, pts, thickness)

        # eventuell sidogren
        bpts = p.get("branch_points")
        if bpts:
            bpts_int = [(int(x), int(y)) for (x, y) in bpts]
            branch_col = (
                int(col[0] * 0.5),
                int(col[1] * 0.5),
                int(col[2] * 0.8),
            )
            pygame.draw.lines(
                surface,
                branch_col,
                False,
                bpts_int,
                max(1, thickness - 1),
            )

    for p in dead:
        particles_logo.remove(p)

    # WIN SPARKS
    dead = []
    for p in particles_win:
        p["life"] -= now_dt
        if p["life"] <= 0:
            dead.append(p)
            continue
        p["x"] += p["vx"]
        p["y"] += p["vy"]
        pygame.draw.circle(surface, p["color"], (int(p["x"]), int(p["y"])), p["size"])
    for p in dead:
        particles_win.remove(p)
  
def draw_grid(surface, grid, font, win_positions=None, time_ms=0,
              wild_reels=None, fs_mults=None,
              wild_drop_start_times=None,
              is_spinning=False,                 # <-- NEW
              reel_stop_times=None):             # <-- NEW
    if grid is None:
        return

    win_positions = win_positions or set()
    wild_reels = set(wild_reels or [])
    fs_mults = fs_mults or {}
    wild_drop_start_times = wild_drop_start_times or {}

    blink_phase = (time_ms // 200) % 2

    # PANEL runt grid
    panel_margin = 24
    extra_bottom = 50
    panel_rect = pygame.Rect(
        GRID_X - panel_margin,
        GRID_Y - panel_margin,
        GRID_WIDTH + 2 * panel_margin,
        GRID_HEIGHT + 2 * panel_margin + extra_bottom,
    )

    shadow_offset = 10
    shadow_rect = panel_rect.move(shadow_offset, shadow_offset)
    shadow_surface = pygame.Surface(shadow_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(
        shadow_surface,
        (0, 0, 0, 140),
        pygame.Rect(0, 0, shadow_rect.width, shadow_rect.height),
        border_radius=28,
    )
    surface.blit(shadow_surface, shadow_rect.topleft)

    pygame.draw.rect(surface, (10, 10, 30), panel_rect, border_radius=28)

    glass_margin = 10
    glass_rect = panel_rect.inflate(-glass_margin * 2, -glass_margin * 2)
    glass_surface = pygame.Surface(glass_rect.size, pygame.SRCALPHA)

    GLASS_COLOR = (80, 180, 255, 85)
    pygame.draw.rect(
        glass_surface,
        GLASS_COLOR,
        pygame.Rect(0, 0, glass_rect.width, glass_rect.height),
        border_radius=24,
    )

    highlight_surface = pygame.Surface(glass_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(
        highlight_surface,
        (255, 255, 255, 55),
        pygame.Rect(0, 0, glass_rect.width, glass_rect.height // 2),
        border_radius=24,
    )
    glass_surface.blit(highlight_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    pygame.draw.rect(
        glass_surface,
        (120, 220, 255, 160),
        pygame.Rect(0, 0, glass_rect.width, glass_rect.height),
        width=3,
        border_radius=24,
    )

    surface.blit(glass_surface, glass_rect.topleft)

    # CELLER
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            x = GRID_X + c * CELL_SIZE
            y = GRID_Y + r * CELL_SIZE
            cell_rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
            # Är det här hjulet fortfarande i spin-fasen?      # <-- NEW
            reel_spinning = False
            if is_spinning and reel_stop_times is not None:
                if c < len(reel_stop_times) and time_ms < reel_stop_times[c]:
                    reel_spinning = True
            if c in wild_reels:
                base_bg = (30, 55, 100)
            else:
                base_bg = (25, 25, 45)

            tl = tr = bl = br = 0
            corner_radius = 18

            if r == 0 and c == 0:
                tl = corner_radius
            elif r == 0 and c == GRID_COLS - 1:
                tr = corner_radius
            elif r == GRID_ROWS - 1 and c == 0:
                bl = corner_radius
            elif r == GRID_ROWS - 1 and c == GRID_COLS - 1:
                br = corner_radius

            pygame.draw.rect(
                surface,
                base_bg,
                cell_rect,
                border_top_left_radius=tl,
                border_top_right_radius=tr,
                border_bottom_left_radius=bl,
                border_bottom_right_radius=br,
            )

            cell_shadow_rect = cell_rect.move(4, 6)
            cell_shadow_surf = pygame.Surface(cell_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(
                cell_shadow_surf,
                (0, 0, 0, 120),
                pygame.Rect(0, 0, cell_rect.width, cell_rect.height),
                border_top_left_radius=tl,
                border_top_right_radius=tr,
                border_bottom_left_radius=bl,
                border_bottom_right_radius=br,
            )
            surface.blit(cell_shadow_surf, cell_shadow_rect.topleft)

            highlight_rect = cell_rect.inflate(-4, -4)
            highlight_surf = pygame.Surface(highlight_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(
                highlight_surf,
                (255, 255, 255, 30),
                pygame.Rect(0, 0, highlight_rect.width, highlight_rect.height // 2),
                border_top_left_radius=tl,
                border_top_right_radius=tr,
            )
            surface.blit(highlight_surf, highlight_rect.topleft)

            if (r, c) in win_positions:
                if blink_phase == 0:
                    overlay_col = (255, 255, 255, 110)
                    spawn_win_sparks(x + CELL_SIZE//2,
                 y + CELL_SIZE//2)
                else:
                    overlay_col = (255, 240, 120, 60)

                overlay_surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                pygame.draw.rect(
                    overlay_surf,
                    overlay_col,
                    pygame.Rect(0, 0, CELL_SIZE, CELL_SIZE),
                    border_top_left_radius=tl,
                    border_top_right_radius=tr,
                    border_bottom_left_radius=bl,
                    border_bottom_right_radius=br,
                )
                surface.blit(overlay_surf, (x, y))

            if c in wild_reels:
                border_color = (80, 230, 255)
                border_width = 4
            else:
                border_color = BLACK
                border_width = 2
            pygame.draw.rect(
                surface,
                border_color,
                cell_rect,
                width=border_width,
                border_top_left_radius=tl,
                border_top_right_radius=tr,
                border_bottom_left_radius=bl,
                border_bottom_right_radius=br,
            )

            if c in wild_reels:
                # Wild reel ska ALLTID visa sina W1–W4 bilder
                if c in wild_drop_start_times:
                    elapsed = max(0, time_ms - wild_drop_start_times[c])
                    visible_rows = min(4, 1 + elapsed // WILD_DROP_STEP_MS)
                else:
                    # Ingen drop – visa full wild reel direkt
                    visible_rows = 4

                if r < visible_rows:
                    sym_key = f"W{r+1}"
                else:
                    sym_key = grid[r][c]
            else:
                sym_key = grid[r][c]

            inner_rect = cell_rect.inflate(-18, -18)
            img = SYMBOL_IMAGES.get(sym_key)
            if img is not None:
                if reel_spinning:
                    # --- MOTION BLUR FÖR PNG-SYMBOLER ---       # <-- NEW
                    # Rita samma symbol flera gånger med lite offset + alpha
                    offsets_and_alpha = [(-8, 80), (0, 180), (8, 80)]
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
                # Fallback om inga PNGs finns
                sym_col = SYMBOL_COLORS.get(sym_key, WHITE)
                if reel_spinning:
                    # Lite "smetning" även för fallback-rutor   # <-- NEW
                    offsets_and_alpha = [(-8, 90), (0, 190), (8, 90)]
                    for dy, alpha in offsets_and_alpha:
                        tmp = pygame.Surface(inner_rect.size, pygame.SRCALPHA)
                        pygame.draw.rect(
                            tmp,
                            (*sym_col, alpha),
                            pygame.Rect(0, 0, inner_rect.width, inner_rect.height),
                            border_radius=12,
                        )
                        surface.blit(tmp, inner_rect.move(0, dy).topleft)
                else:
                    pygame.draw.rect(surface, sym_col, inner_rect, border_radius=12)
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
            # --- HEL-CELLS-GRADIENT (svart → mörkare nedåt), ovanpå symbolen ---
            shade_rect = cell_rect.inflate(-4, -4)
            shade_surf = pygame.Surface(shade_rect.size, pygame.SRCALPHA)

            max_alpha = 130        # hur mörk botten ska vara (justera efter smak)
            h = shade_rect.height

            # hela cellen
            for i in range(h):
                t = i / h           # 0 (toppen) → 1 (botten)
                alpha = int(max_alpha * t)
                pygame.draw.rect(
                    shade_surf,
                    (0, 0, 0, alpha),
                    pygame.Rect(0, i, shade_rect.width, 1),
                )

            surface.blit(shade_surf, shade_rect.topleft)

    # MULTIPLIER-CIRKLAR
    circle_y = GRID_Y + GRID_HEIGHT + 32
    circle_radius = 22

    for c in range(GRID_COLS):
        cx = GRID_X + c * CELL_SIZE + CELL_SIZE // 2

        mult_val = fs_mults.get(c, 1)
        is_wild_reel = (c in wild_reels and c in fs_mults)

        if is_wild_reel:
            fill_col = (40, 30, 0)
            border_col = (255, 220, 0)
            text_col = YELLOW
            glow_r = circle_radius + 6
            glow_surf = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (255, 220, 0, 140), (glow_r, glow_r), glow_r)
            surface.blit(glow_surf, (cx - glow_r, circle_y - glow_r))
        else:
            fill_col = (15, 20, 40)
            border_col = (80, 90, 130)
            text_col = GREY

        pygame.draw.circle(surface, fill_col, (cx, circle_y), circle_radius)
        pygame.draw.circle(surface, border_col, (cx, circle_y), circle_radius, 3)
        draw_text(surface, f"x{mult_val}", cx, circle_y, FONT_SMALL, text_col, center=True)

async def main():
    global MASTER_VOLUME, music_duck_factor, MUSIC_VOLUME, SFX_VOLUME
    screen = pygame.display.set_mode((BASE_WIDTH, BASE_HEIGHT)) #screen = pygame.display.set_mode((BASE_WIDTH, BASE_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Megaways Slot – GUI")

    game_surface = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))
    clock = pygame.time.Clock()

    render_scale = 1.0
    render_offset = (0, 0)

    # Ljud / musik state                                  # <-- NYTT
    reel_stop_played = [False] * GRID_COLS               # per-hjul-stoppljud
    current_music_mode = "base"
    music_ducked_for_bigwin = False
    play_music("base")  # starta bas-låten om fil finns

    # ---------- Spelstatus ----------
    paytable_visible = False
    paytable_mode = "paytable"          # <-- NY (växlar PAYTABLE/INFO)
    current_language_index = 0          # <-- NY (0 = svenska)
    particles = []
    last_particle_spawn = 0
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
    fs_last_spin_win = 0.0  # NY: vinst på senaste free spin
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

    # ------------------- LAYOUT (bas-koords) -------------------
    spin_radius = 70
    spin_center = (WINDOW_WIDTH - 230, WINDOW_HEIGHT - 270)
    spin_button_rect = pygame.Rect(
        spin_center[0] - spin_radius,
        spin_center[1] - spin_radius,
        spin_radius * 2,
        spin_radius * 2,
    )

    bet_label_pos = (spin_center[0], spin_center[1] - spin_radius - 35)

    buy_w, buy_h = BUY_BUTTON_IMG.get_size()
    minus_w, minus_h = BET_MINUS_IMG.get_size()
    plus_w, plus_h = BET_PLUS_IMG.get_size()

    bet_minus_rect = pygame.Rect(
        spin_center[0] - 108,
        spin_center[1] + spin_radius-5,
        minus_w,
        minus_h,
    )
    bet_plus_rect = pygame.Rect(
        spin_center[0] + 28,
        spin_center[1] + spin_radius -5,
        plus_w,
        plus_h,
    )

    buy_button_rect = pygame.Rect(
        GRID_X - 70 - buy_w,
        GRID_Y + GRID_HEIGHT // 2 - buy_h // 2,
        buy_w,
        buy_h,
    )

    paytable_button_rect = pygame.Rect(
        0, 0,
        PAYTABLE_BTN_RADIUS * 2,
        PAYTABLE_BTN_RADIUS * 2,
    )
    paytable_button_rect.center = (50, 50)  # uppe vänster i bas-koordinater

    language_button_rect = pygame.Rect(0, 0, 90, 40)     # <-- NY
    language_button_rect.center = (WINDOW_WIDTH - 90, 50)  # uppe höger  <-- NY

    # --- Volym–sliders ---  (MUSIC + SFX)
    music_slider_rect = pygame.Rect(0, 0, 260, 24)
    music_slider_rect.center = (WINDOW_WIDTH // 2 - 550, 855)

    sfx_slider_rect = pygame.Rect(0, 0, 260, 24)
    sfx_slider_rect.center = (WINDOW_WIDTH // 2  - 550, 890)

    music_slider_dragging = False
    sfx_slider_dragging = False


    confirm_width, confirm_height = 500, 260
    confirm_rect = pygame.Rect(
        (WINDOW_WIDTH - confirm_width) // 2,
        (WINDOW_HEIGHT - confirm_height) // 2,
        confirm_width,
        confirm_height,
    )
    confirm_yes_rect = pygame.Rect(
        confirm_rect.centerx - 160,
        confirm_rect.bottom - 80,
        130,
        50,
    )
    confirm_no_rect = pygame.Rect(
        confirm_rect.centerx + 30,
        confirm_rect.bottom - 80,
        130,
        50,
    )
    # <-- NY: close-knapp för paytable
    paytable_close_rect = None
    info_toggle_rect = None   # <-- NY: pilknapp inne i paytable


    running = True
    while running:
        dt = clock.tick(120)
        now = pygame.time.get_ticks()
        current_language = LANG_SEQUENCE[current_language_index]  # <-- NY
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                wx, wy = event.pos



                # BIG WIN overlay: klick stänger bara overlay, ingen annan input
                if big_win_active:
                    big_win_active = False
                    big_win_end_time = 0
                    if music_ducked_for_bigwin:
                        try:
                            music_duck_factor = 1.0
                            update_global_volume()
                            music_ducked_for_bigwin = False
                        except Exception:
                            pass
                        music_ducked_for_bigwin = False
                    continue
                offset_x, offset_y = render_offset
                mx = (wx - offset_x) / render_scale
                my = (wy - offset_y) / render_scale

                # MUSIC–slider
                if music_slider_rect.collidepoint(mx, my):
                    music_slider_dragging = True
                    inner_left = music_slider_rect.left + 20
                    inner_right = music_slider_rect.right - 20
                    if inner_right > inner_left:
                        t = (mx - inner_left) / (inner_right - inner_left)
                        MUSIC_VOLUME = max(0.0, min(1.0, t))
                        update_global_volume()
                    continue

                # SFX–slider
                if sfx_slider_rect.collidepoint(mx, my):
                    sfx_slider_dragging = True
                    inner_left = sfx_slider_rect.left + 20
                    inner_right = sfx_slider_rect.right - 20
                    if inner_right > inner_left:
                        t = (mx - inner_left) / (inner_right - inner_left)
                        SFX_VOLUME = max(0.0, min(1.0, t))
                        update_global_volume()
                    continue

                # Klick under FS-trigger-transition
                if fs_transition_active:
                    if fs_transition_phase in ("fade_in", "waiting_click"):
                        fs_transition_phase = "fade_out"
                        fs_transition_start = now
                        if pending_fs_from_scatter:
                            game_mode = "fs"
                            bonus_state = "running"
                            fs_next_spin_time = now + FS_AUTO_SPIN_DELAY_MS
                            pending_fs_from_scatter = False
                            if current_music_mode != "fs":         # <-- NYTT
                                current_music_mode = "fs"
                                play_music("fs")
                    continue

                # Klick under BONUS OVER-transition
                if end_fs_transition_active:
                    if end_fs_transition_phase in ("fade_in", "waiting_click"):
                        end_fs_transition_phase = "fade_out"
                        end_fs_transition_start = now
                        game_mode = "base"
                    continue

                # Buy-confirm overlay
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
                
                # Stäng paytable via rött kryss
                if paytable_visible and paytable_close_rect is not None:
                    if paytable_close_rect.collidepoint(mx, my):
                        paytable_visible = False
                        continue

                # Pilknapp inne i paytable-panelen: växla PAYTABLE <-> INFO  <-- NY
                if paytable_visible and info_toggle_rect is not None:
                    if info_toggle_rect.collidepoint(mx, my):
                        paytable_mode = "info" if paytable_mode == "paytable" else "paytable"
                        continue

                # Paytable-knapp: öppna/stäng panelen (ALLTID start på PAYTABLE)
                if paytable_button_rect.collidepoint(mx, my):
                    if not paytable_visible:
                        paytable_visible = True
                        paytable_mode = "paytable"
                    else:
                        paytable_visible = False
                    continue

                # Language-knapp – byt språk i ordning SV -> EN -> DE -> FR -> ES  <-- NY
                if language_button_rect.collidepoint(mx, my):
                    current_language_index = (current_language_index + 1) % len(LANG_SEQUENCE)
                    continue


                # --- Bet-knappar (respektera min/max visuellt & logiskt) ---
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
                    message = f"Bet ändrad till {bet}"
                    bet_minus_held = True

                elif can_change_bet and bet_plus_rect.collidepoint(mx, my) and bet_index < len(BET_LEVELS) - 1:
                    bet_index += 1
                    bet = BET_LEVELS[bet_index]
                    message = f"Bet ändrad till {bet}"
                    bet_plus_held = True

                # Köp FS-knapp
                if (bonus_state == "none" and not is_spinning and game_mode == "base"
                        and not big_win_active and buy_button_rect.collidepoint(mx, my)
                        and not buy_confirm_visible):
                    cost = FS_BUY_MULT * bet
                    if balance >= cost:
                        buy_confirm_visible = True
                        buy_confirm_cost = cost
                    else:
                        message = "För lite saldo för att köpa free spins!"

                # Spin-knapp
                if (bonus_state == "none"
                        and spin_button_rect.collidepoint(mx, my)
                        and not is_spinning and not big_win_active
                        and not buy_confirm_visible):

                    # Man får bara manuellt spinna i base game (FS auto-spinnar)
                    if game_mode == "base":
                        if balance < bet:
                            message = "För lite saldo för att spinna."
                        else:
                            spin_held = True
                            balance -= bet

                            # --- starta nytt spin ---
                            is_spinning = True
                            spin_result_applied = False
                            spin_start_time = now

                            reel_stop_times = [
                                spin_start_time + SPIN_FIRST_STOP_MS + SPIN_REEL_STEP_MS * i
                                for i in range(GRID_COLS)
                            ]
                            reel_stop_played = [False] * GRID_COLS

                            # Grid-resultatet för detta spin (VIKTIGT!)
                            final_grid = spin_grid_same_probs()

                            # Animations-grid (rullar symboler tills hjulen stannar)
                            spin_anim_grid = [
                                [random.choice(SPIN_SYMBOLS) for _ in range(GRID_COLS)]
                                for _ in range(GRID_ROWS)
                            ]
                            last_spin_anim_update = now

                            # Nollställ gammal vinstvisning för tydlighet
                            last_win = 0.0
                            last_win_positions = set()
                            message = ""

                            if SND_SPIN_START:
                                SND_SPIN_START.play()

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                bet_minus_held = False
                bet_plus_held = False
                spin_held = False
                music_slider_dragging = False
                sfx_slider_dragging = False
            
            elif event.type == pygame.MOUSEMOTION:
                wx, wy = event.pos
                offset_x, offset_y = render_offset
                mx = (wx - offset_x) / render_scale
                my = (wy - offset_y) / render_scale

                # Dra MUSIC–slider
                if music_slider_dragging:
                    inner_left = music_slider_rect.left + 20
                    inner_right = music_slider_rect.right - 20
                    if inner_right > inner_left:
                        t = (mx - inner_left) / (inner_right - inner_left)
                        MUSIC_VOLUME = max(0.0, min(1.0, t))
                        update_global_volume()

                # Dra SFX–slider
                if sfx_slider_dragging:
                    inner_left = sfx_slider_rect.left + 20
                    inner_right = sfx_slider_rect.right - 20
                    if inner_right > inner_left:
                        t = (mx - inner_left) / (inner_right - inner_left)
                        SFX_VOLUME = max(0.0, min(1.0, t))
                        update_global_volume()


        # ---------- AUTOSPIN FÖR FS ----------
        if (game_mode == "fs"
                and bonus_state == "running"
                and not is_spinning
                and fs_spins_left > 0
                and fs_total_mult < MAX_WIN_MULT
                and not big_win_active):

            if fs_next_spin_time is None:
                fs_next_spin_time = now + FS_AUTO_SPIN_DELAY_MS

            if now >= fs_next_spin_time:
                # dra ner direkt vid spin-start
                if fs_spins_left > 0:
                    fs_spins_left -= 1
                is_spinning = True
                spin_result_applied = False
                spin_start_time = now
                reel_stop_times = [
                    spin_start_time + SPIN_FIRST_STOP_MS + SPIN_REEL_STEP_MS * i
                    for i in range(GRID_COLS)
                ]
                reel_stop_played = [False] * GRID_COLS      # <-- NYTT
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
                    current_wild_reels = random.sample(range(NUM_REELS), k)
                    # säkerställ att indexen är i range och sortera dem
                    current_wild_reels = sorted(
                        r for r in current_wild_reels if 0 <= r < NUM_REELS
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

        # ---------- SPINLOGIK ----------
        if is_spinning:
            # Spela stoppljud + scatter-ljud per hjul
            for c in range(GRID_COLS):
                if not reel_stop_played[c] and now >= reel_stop_times[c]:
                    if SND_REEL_STOP:
                        SND_REEL_STOP.play()

                    # SCATTER-ljud om den här kolumnen har minst en 'S'
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
                        if current_grid is None:
                            base_mult = 0.0    # safety fallback så vi aldrig kraschar
                        else:
                            base_mult = evaluate_megaways_win(current_grid, paytable)

                    win_amount = base_mult * bet
                    balance += win_amount
                    last_win = win_amount

                    if win_amount > 0:
                        if win_amount >= BIG_WIN_THRESHOLD_MULT * bet:
                            if SND_WIN_BIG:
                                SND_WIN_BIG.play()
                            # ducka musiken
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
                        last_win_positions = find_winning_positions(
                            current_grid, paytable
                        )

                    if win_amount >= BIG_WIN_THRESHOLD_MULT * bet:
                        big_win_active = True
                        big_win_end_time = now + BIG_WIN_DURATION_MS

                    scatter_count = sum(
                        1
                        for row in current_grid
                        for sym in row
                        if sym == "S"
                    )

                    if scatter_count == 3:
                        fs_spins_left = N_FREE_SPINS
                        fs_total_win = 0.0
                        fs_total_mult = 0.0
                        fs_last_spin_win = 0.0  # NY
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

                    if current_wild_mults:
                        spin_mult_factor = sum(current_wild_mults.values())
                    else:
                        spin_mult_factor = 1

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
                    retrigger_scatter_positions = set()   # NY

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

                        # Start BONUS OVER-overlay
                        end_fs_transition_active = True
                        end_fs_transition_phase = "fade_in"
                        end_fs_transition_start = now

                        # "Tape stop" – fadea ut FS-musiken snabbt istället för separat ljud
                        try:
                            pygame.mixer.music.fadeout(1500)  # 1.5 s fade, justera fritt (800–2000 typ)
                        except Exception as e:
                            print("[VARNING] kunde inte fadeout musik vid bonus-slut:", e)
                    else:
                        if extra_spins > 0:
                            message = (
                                f"FS vinst: {spin_win:.2f} | +{extra_spins} extra spins! "
                                f"FS total: {fs_total_win:.2f} | "
                                f"Spins kvar: {fs_spins_left}"
                            )
                        else:
                            message = (
                                f"FS vinst: {spin_win:.2f} | "
                                f"FS total: {fs_total_win:.2f} | "
                                f"Spins kvar: {fs_spins_left}"
                            )

                    if bonus_state == "running":
                        if spin_win > 0 or extra_spins > 0:
                            delay = FS_AUTO_SPIN_DELAY_WIN_MS
                        else:
                            delay = FS_AUTO_SPIN_DELAY_MS
                        fs_next_spin_time = now + delay

        # ---------- RITNING PÅ game_surface ----------
        surface = game_surface
        if game_mode == "fs" and BG_FS_IMG is not None:
            surface.blit(BG_FS_IMG, (0, 0))
            spawn_neon_dust(game_mode="fs")

        elif game_mode == "base" and BG_BASE_IMG is not None:
            surface.blit(BG_BASE_IMG, (0, 0))
            spawn_neon_dust(game_mode="base")
        else:
            surface.fill(BG_FS if game_mode == "fs" else BG_BASE)
        # Rita bakgrundspartiklar bakom grid/logga             # <-- NY
        update_and_draw_bg_particles(surface)
        if game_mode == "fs":
            draw_bonus_logo_electric(surface)
        else:
            # Base game: logga utan partiklar
            draw_logo_mixtape_megaways(surface)
            # ingen spawn_logo_sparks här (så inget hamnar på base game-loggan)

        if game_mode == "fs":
            left_x = GRID_X
            base_y = GRID_Y
            if bonus_state in ("ready_to_start", "running", "finished_waiting"):
                # --- Cirkel: SPINS KVAR (samma färgtema som grid) ---
                circle_center = (left_x -140, base_y+ 70)
                circle_radius = 65

                # Bas
                pygame.draw.circle(surface, (25, 25, 45), circle_center, circle_radius)
                # Highlight upptill
                circle_highlight = pygame.Surface((circle_radius*2, circle_radius*2), pygame.SRCALPHA)
                pygame.draw.circle(
                    circle_highlight,
                    (255, 255, 255, 45),
                    (circle_radius, circle_radius),
                    circle_radius
                )
                # Klipp bort nedre halvan så highlighten bara är upptill
                pygame.draw.rect(
                    circle_highlight,
                    (0, 0, 0, 0),
                    pygame.Rect(0, circle_radius, circle_radius*2, circle_radius)
                )
                surface.blit(circle_highlight, (circle_center[0]-circle_radius, circle_center[1]-circle_radius))
                # Kant
                pygame.draw.circle(surface, (120, 220, 255), circle_center, circle_radius, 3)

                draw_text(surface, TEXT[current_language]["FS_SPINS_LEFT"],
                          circle_center[0], circle_center[1] - 18,
                          FONT_SMALL, GREY, center=True)
                draw_text(surface, str(fs_spins_left), circle_center[0], circle_center[1] + 12,
                          FONT_LARGE, WHITE, center=True)

                # --- Ruta: TOTAL BONUSVINST (grid-style box) ---
                total_rect = pygame.Rect(left_x + 720, base_y, 300, 70)
                # Skugga
                total_shadow = total_rect.move(4, 6)
                shadow_surf = pygame.Surface(total_rect.size, pygame.SRCALPHA)
                pygame.draw.rect(
                    shadow_surf,
                    (0, 0, 0, 120),
                    pygame.Rect(0, 0, total_rect.width, total_rect.height),
                    border_radius=18,
                )
                surface.blit(shadow_surf, total_shadow.topleft)
                # Bas
                pygame.draw.rect(surface, (25, 25, 45), total_rect, border_radius=18)
                # Highlight upptill
                total_highlight = pygame.Surface(total_rect.size, pygame.SRCALPHA)
                pygame.draw.rect(
                    total_highlight,
                    (255, 255, 255, 35),
                    pygame.Rect(0, 0, total_rect.width, total_rect.height // 2),
                    border_radius=18,
                )
                surface.blit(total_highlight, total_rect.topleft)
                # Kant
                pygame.draw.rect(surface, (120, 220, 255), total_rect, width=2, border_radius=18)

                draw_text(surface, TEXT[current_language]["FS_TOTAL_WIN"],
                          total_rect.centerx, total_rect.top + 15,
                          FONT_SMALL, GREY, center=True)
                draw_text(surface, f"{fs_total_win:.2f}", total_rect.centerx,
                          total_rect.bottom - 26, FONT_MEDIUM, WHITE, center=True)

                # --- Ruta: DETTA FS-SPINN (grid-style box) ---
                spin_rect = pygame.Rect(left_x + 720, base_y + 90, 300, 70)
                spin_shadow = spin_rect.move(4, 6)
                spin_shadow_surf = pygame.Surface(spin_rect.size, pygame.SRCALPHA)
                pygame.draw.rect(
                    spin_shadow_surf,
                    (0, 0, 0, 120),
                    pygame.Rect(0, 0, spin_rect.width, spin_rect.height),
                    border_radius=18,
                )
                surface.blit(spin_shadow_surf, spin_shadow.topleft)

                pygame.draw.rect(surface, (25, 25, 45), spin_rect, border_radius=18)
                spin_highlight = pygame.Surface(spin_rect.size, pygame.SRCALPHA)
                pygame.draw.rect(
                    spin_highlight,
                    (255, 255, 255, 35),
                    pygame.Rect(0, 0, spin_rect.width, spin_rect.height // 2),
                    border_radius=18,
                )
                surface.blit(spin_highlight, spin_rect.topleft)
                pygame.draw.rect(surface, (120, 220, 255), spin_rect, width=2, border_radius=18)

                draw_text(surface, TEXT[current_language]["FS_THIS_SPIN"],
                          spin_rect.centerx, spin_rect.top + 15,
                          FONT_SMALL, GREY, center=True)
                draw_text(surface, f"{fs_last_spin_win:.2f}", spin_rect.centerx,
                          spin_rect.bottom - 26, FONT_MEDIUM, WHITE, center=True)

        now_ms = pygame.time.get_ticks()

        # Wild-reels: under spin -> använd droppande reels,  efter spin -> använd hela current_wild_reels           # <-- NY / ÄNDRA
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
        # Lägg på retrigger-scatters som blinkar medan overlayen är aktiv
        if (game_mode == "fs"
                and bonus_state == "running"
                and now < retrigger_overlay_until
                and retrigger_scatter_positions):
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
            is_spinning=is_spinning,                             # <-- NEW
            reel_stop_times=reel_stop_times if is_spinning else None,  # <-- NEW
        )
        # --- Hover i bas-koords ---
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

        # Minus-ikon
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

        # Plus-ikon
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

        # Spin-knapp
        hover_spin = spin_button_rect.collidepoint(mouse_pos)
        spin_label = "SPIN" if game_mode == "base" else "FS"

        # Disabled när:
        #  - bonus overlay / FS
        #  - buy-confirm
        #  - i base och inte råd att spinna
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
            pressed=spin_held and not spin_disabled,     # <-- NY
            img=SPIN_BUTTON_IMG,
            img_disabled=SPIN_BUTTON_IMG_DISABLED,       # disabled-bild
            img_pressed=SPIN_BUTTON_IMG_PRESSED,         # pressed-bild
        )

        # Buy-knapp
        hover_buy = buy_button_rect.collidepoint(mouse_pos)
        cost = FS_BUY_MULT * bet

        buy_disabled_input = (game_mode != "base"
                              or big_win_active
                              or is_spinning
                              or bonus_state != "none"
                              or buy_confirm_visible
                              or balance < cost)

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

        # Paytable-knapp (vit info-cirkel uppe till vänster)
        hover_paytable = paytable_button_rect.collidepoint(mouse_pos)
        draw_paytable_icon(
            surface,
            paytable_button_rect.center,
            PAYTABLE_BTN_RADIUS,
            hover=hover_paytable
        )

        # Language-knapp (glas + flagga)
        hover_lang = language_button_rect.collidepoint(mouse_pos)

        # Bakgrund
        pygame.draw.rect(surface, (10, 10, 30), language_button_rect, border_radius=16)

        high_surf = pygame.Surface(language_button_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(
            high_surf,
            (255, 255, 255, 40 if hover_lang else 20),
            pygame.Rect(0, 0, language_button_rect.width, language_button_rect.height // 2),
            border_radius=16,
        )
        surface.blit(high_surf, language_button_rect.topleft)

        pygame.draw.rect(surface, (120, 220, 255), language_button_rect, width=2, border_radius=16)

        flag_img = FLAG_IMAGES.get(current_language)
        if flag_img is not None:
            flag_rect = flag_img.get_rect(center=language_button_rect.center)
            surface.blit(flag_img, flag_rect)
        else:
            # fallback: textkod
            lang_label = TEXT[current_language]["LANG_NAME"]
            draw_text(
                surface, lang_label,
                language_button_rect.centerx, language_button_rect.centery,
                FONT_SMALL, WHITE, center=True
            )
        
        # --- Volym–sliders (MUSIC + SFX) ---
        slider_inner_margin = 18

        def draw_slider(rect, value, label):
            # bakgrund
            pygame.draw.rect(surface, (10, 10, 30), rect, border_radius=12)

            inner = rect.inflate(-4, -4)
            track_y = inner.centery

            # grå "tom" bar
            pygame.draw.line(
                surface,
                (60, 60, 80),
                (inner.left + slider_inner_margin, track_y),
                (inner.right - slider_inner_margin, track_y),
                4,
            )

            # fylld del
            inner_left = inner.left + slider_inner_margin
            inner_right = inner.right - slider_inner_margin
            if inner_right > inner_left:
                filled_x = inner_left + value * (inner_right - inner_left)
            else:
                filled_x = inner_left

            pygame.draw.line(
                surface,
                (100, 190, 255),
                (inner_left, track_y),
                (filled_x, track_y),
                4,
            )

            # handtag
            handle_x = filled_x
            handle_radius = 9
            pygame.draw.circle(surface, (210, 230, 255), (int(handle_x), track_y), handle_radius)
            pygame.draw.circle(surface, (0, 0, 0), (int(handle_x), track_y), handle_radius, 1)

            # label
            draw_text(
                surface,
                label,
                rect.left - 40,
                rect.centery,
                FONT_SMALL,
                WHITE,
                center=True,
            )

        # Rita båda
        draw_slider(music_slider_rect, MUSIC_VOLUME, "MUSIC")
        draw_slider(sfx_slider_rect, SFX_VOLUME, "SFX")

        # --- Bottom-bar i samma stil som grid-panelen ---
        bottom_margin_x = 15
        bottom_margin_y = 30
        bottom_height = 52

        bottom_rect = pygame.Rect(
            bottom_margin_x,
            WINDOW_HEIGHT - bottom_height - bottom_margin_y,
            WINDOW_WIDTH - 2 * bottom_margin_x,
            bottom_height,
        )

        # Skugga
        bottom_shadow = bottom_rect.move(6, 6)
        bottom_shadow_surf = pygame.Surface(bottom_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(
            bottom_shadow_surf,
            (0, 0, 0, 140),
            pygame.Rect(0, 0, bottom_rect.width, bottom_rect.height),
            border_radius=24,
        )
        surface.blit(bottom_shadow_surf, bottom_shadow.topleft)

        # Baspanel
        pygame.draw.rect(surface, (10, 10, 30), bottom_rect, border_radius=24)

        # Glass/highlight-lager
        inner_rect = bottom_rect.inflate(-8, -8)
        glass_surf = pygame.Surface(inner_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(
            glass_surf,
            (80, 180, 255, 70),
            pygame.Rect(0, 0, inner_rect.width, inner_rect.height),
            border_radius=20,
        )
        # Highlight upptill
        top_highlight = pygame.Surface(inner_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(
            top_highlight,
            (255, 255, 255, 40),
            pygame.Rect(0, 0, inner_rect.width, inner_rect.height // 2),
            border_radius=20,
        )
        glass_surf.blit(top_highlight, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        # Kant
        pygame.draw.rect(
            glass_surf,
            (120, 220, 255, 160),
            pygame.Rect(0, 0, inner_rect.width, inner_rect.height),
            width=2,
            border_radius=20,
        )

        surface.blit(glass_surf, inner_rect.topleft)

        # --- Texter inuti bottom-bar ---
        center_y = inner_rect.centery

        # Saldo (vänster)
        saldo_x = inner_rect.left + 180
        draw_text(surface, f"{TEXT[current_language]['LABEL_SALDO']}: {balance:.2f}",
                  saldo_x, center_y, FONT_SMALL, WHITE, center=True)

        # Senaste vinst (mitten)
        last_win_x = inner_rect.centerx
        draw_text(surface, f"{TEXT[current_language]['LABEL_LAST_WIN']}: {last_win:.2f}",
                  last_win_x, center_y, FONT_SMALL, WHITE, center=True)

        # Bet/insats (höger)
        bet_x = inner_rect.right - 180
        draw_text(surface, f"{TEXT[current_language]['LABEL_BET']}: {bet:.2f}",
                  bet_x, center_y, FONT_SMALL, WHITE, center=True)

        if paytable_visible:
            # Bakgrund overlay 50% svart
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            surface.blit(overlay, (0, 0))

            # Panel
            panel_w, panel_h = 1000, 650
            panel_x = (WINDOW_WIDTH - panel_w) // 2
            panel_y = (WINDOW_HEIGHT - panel_h) // 2

            panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
            pygame.draw.rect(panel, (20, 20, 40), (0, 0, panel_w, panel_h), border_radius=20)
            pygame.draw.rect(panel, CYAN, (0, 0, panel_w, panel_h), width=3, border_radius=20)
            surface.blit(panel, (panel_x, panel_y))

                        # --- Rött kryss uppe till höger på panelen ---
            close_size = 34
            paytable_close_rect = pygame.Rect(
                panel_x + panel_w - close_size - 16,
                panel_y + 16,
                close_size,
                close_size,
            )

            # --- Pilknapp för att byta sida (PAYTABLE <-> INFO) ---
            toggle_w = 40
            toggle_h = close_size
            info_toggle_rect = pygame.Rect(
                paytable_close_rect.left - toggle_w - 10,
                paytable_close_rect.top,
                toggle_w,
                toggle_h,
            )

            hover_toggle = info_toggle_rect.collidepoint(mouse_pos)

            # Glasig knapp
            pygame.draw.rect(surface, (10, 10, 30), info_toggle_rect, border_radius=10)
            toggle_inner = info_toggle_rect.inflate(-4, -4)
            inner_surf = pygame.Surface(toggle_inner.size, pygame.SRCALPHA)
            pygame.draw.rect(
                inner_surf,
                (80, 180, 255, 70),
                pygame.Rect(0, 0, toggle_inner.width, toggle_inner.height),
                border_radius=8,
            )
            top_high = pygame.Surface(toggle_inner.size, pygame.SRCALPHA)
            pygame.draw.rect(
                top_high,
                (255, 255, 255, 40 if hover_toggle else 20),
                pygame.Rect(0, 0, toggle_inner.width, toggle_inner.height // 2),
                border_radius=8,
            )
            inner_surf.blit(top_high, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            pygame.draw.rect(
                inner_surf,
                (120, 220, 255, 170),
                pygame.Rect(0, 0, toggle_inner.width, toggle_inner.height),
                width=2,
                border_radius=8,
            )
            surface.blit(inner_surf, toggle_inner.topleft)

            # Triangelpil
            cx, cy = info_toggle_rect.center
            if paytable_mode == "paytable":
                pts = [(cx - 6, cy - 10), (cx + 6, cy), (cx - 6, cy + 10)]
            else:
                pts = [(cx + 6, cy - 10), (cx - 6, cy), (cx + 6, cy + 10)]
            pygame.draw.polygon(surface, WHITE, pts)

            hover_toggle = info_toggle_rect.collidepoint(mouse_pos)
            toggle_col = (60, 160, 220) if not hover_toggle else (100, 200, 255)

            pygame.draw.rect(surface, toggle_col, info_toggle_rect, border_radius=10)
            pygame.draw.rect(surface, WHITE, info_toggle_rect, width=2, border_radius=10)

            arrow_char = ">" if paytable_mode == "paytable" else "<"
            draw_text(surface, arrow_char,
                      info_toggle_rect.centerx, info_toggle_rect.centery,
                      FONT_LARGE, WHITE, center=True)

            close_hover = paytable_close_rect.collidepoint(mouse_pos)
            base_col = (200, 60, 60) if not close_hover else (255, 100, 100)


            # Själva X:et
            cx, cy = paytable_close_rect.center
            r = close_size // 2 - 6
            thickness = 4
            pygame.draw.line(surface, base_col, (cx - r, cy - r), (cx + r, cy + r), thickness)
            pygame.draw.line(surface, base_col, (cx - r, cy + r), (cx + r, cy - r), thickness)

            # Titel (växlar text beroende på mode)                     # <-- ÄNDRA
            title_key = "PAYTABLE_TITLE" if paytable_mode == "paytable" else "INFO_TITLE"
            draw_text(surface, TEXT[current_language][title_key],
                      panel_x + panel_w // 2, panel_y + 40,
                      FONT_LARGE, WHITE, center=True)

            if paytable_mode == "paytable":                            # <-- NY
                # --- PAYTABLE-SIDA (som du hade innan) ---
                pay_syms = []
                for sym in SYMBOLS:
                    if sym in ("S", "W"):
                        continue
                    if any((sym, n) in paytable for n in (3, 4, 5, 6)):
                        pay_syms.append(sym)

                cols = 3
                cell_w = panel_w // cols
                cell_h = 150
                start_y = panel_y + 100

                for idx, sym in enumerate(pay_syms):
                    col = idx % cols
                    row = idx // cols

                    cell_x = panel_x + col * cell_w
                    cell_y = start_y + row * cell_h

                    center_x = cell_x + cell_w // 2

                    img = SYMBOL_IMAGES.get(sym)
                    if img is not None:
                        img_rect = img.get_rect(center=(center_x, cell_y + 35))
                        surface.blit(img, img_rect)
                    else:
                        draw_text(surface, sym, center_x, cell_y + 35, FONT_LARGE, WHITE, center=True)

                    text_x = cell_x + 127
                    line_y = cell_y + 75

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
                            line_y += 22

            else:
                # --- INFO-SIDA (scatters / maxwin / wild reels) ---      # <-- NY
                info_y = panel_y + 130
                center_x = panel_x + panel_w // 2

                draw_text(surface, TEXT[current_language]["INFO_SCATTERS"],
                          center_x, info_y, FONT_MEDIUM, YELLOW, center=True)
                draw_text(surface, TEXT[current_language]["INFO_MAXWIN"],
                          center_x, info_y + 40, FONT_MEDIUM, WHITE, center=True)
                draw_text(surface, TEXT[current_language]["INFO_WILDS"],
                          center_x, info_y + 90, FONT_SMALL, GREY, center=True)

            # --- Regeltext längst ner (som på bilden) ---
            rule_line1 = TEXT[current_language]["RULE_LINE1"]
            rule_line2 = TEXT[current_language]["RULE_LINE2"]

            draw_text(
                surface,
                rule_line1,
                panel_x + panel_w // 2,
                panel_y + panel_h - 60,
                FONT_SMALL,
                GREY,
                center=True
            )
            draw_text(
                surface,
                rule_line2,
                panel_x + panel_w // 2,
                panel_y + panel_h - 35,
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
        # RITA FOREGROUND-PARTIKLAR ALLRA SIST (ovanför grid, knappar, osv.)
        update_and_draw_fg_particles(surface)
        if buy_confirm_visible:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            surface.blit(overlay, (0, 0))

            # --- Dynamisk storlek beroende på språk/text ---  <-- NYTT
            title_text = TEXT[current_language]["BUY_TITLE"]
            question_text = TEXT[current_language]["BUY_QUESTION"].format(cost=buy_confirm_cost)

            title_w, title_h = FONT_LARGE.size(title_text)
            q_w, q_h = FONT_MEDIUM.size(question_text)

            padding_x = 80
            padding_y_top = 40
            padding_y_bottom = 40
            spacing_title_question = 30
            spacing_question_buttons = 60

            button_width, button_height = 130, 50
            button_spacing = 40
            buttons_total_width = 2 * button_width + button_spacing

            # bredden måste rymma titel, fråga OCH knappar
            content_width = max(title_w, q_w, buttons_total_width)
            confirm_width = max(500, content_width + 2 * padding_x)

            confirm_height = (
                padding_y_top
                + title_h
                + spacing_title_question
                + q_h
                + spacing_question_buttons
                + button_height
                + padding_y_bottom
            )

            # uppdatera rektangeln centrerat på skärmen
            confirm_rect.width = confirm_width
            confirm_rect.height = confirm_height
            confirm_rect.x = (WINDOW_WIDTH - confirm_width) // 2
            confirm_rect.y = (WINDOW_HEIGHT - confirm_height) // 2

            # knapparna längst ned i panelen
            buttons_y = confirm_rect.bottom - padding_y_bottom - button_height
            buttons_start_x = confirm_rect.centerx - buttons_total_width // 2

            confirm_yes_rect = pygame.Rect(
                buttons_start_x,
                buttons_y,
                button_width,
                button_height,
            )
            confirm_no_rect = pygame.Rect(
                buttons_start_x + button_width + button_spacing,
                buttons_y,
                button_width,
                button_height,
            )

            # --- Rita panelen i "glas"-stil som grid/bottombar ---
            panel_surf = pygame.Surface(confirm_rect.size, pygame.SRCALPHA)

            # Bas
            pygame.draw.rect(
                panel_surf,
                (10, 10, 30),
                pygame.Rect(0, 0, confirm_rect.width, confirm_rect.height),
                border_radius=20,
            )

            # Glas / highlight
            inner = pygame.Rect(6, 6, confirm_rect.width - 12, confirm_rect.height - 12)
            glass = pygame.Surface(inner.size, pygame.SRCALPHA)
            pygame.draw.rect(
                glass,
                (80, 180, 255, 70),
                pygame.Rect(0, 0, inner.width, inner.height),
                border_radius=18,
            )

            top_high = pygame.Surface(inner.size, pygame.SRCALPHA)
            pygame.draw.rect(
                top_high,
                (255, 255, 255, 45),
                pygame.Rect(0, 0, inner.width, inner.height // 2),
                border_radius=18,
            )
            glass.blit(top_high, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

            pygame.draw.rect(
                glass,
                (120, 220, 255, 170),
                pygame.Rect(0, 0, inner.width, inner.height),
                width=2,
                border_radius=18,
            )

            panel_surf.blit(glass, inner.topleft)

            # Skugga under panelen
            shadow = pygame.Surface(confirm_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(
                shadow,
                (0, 0, 0, 150),
                pygame.Rect(0, 0, confirm_rect.width, confirm_rect.height),
                border_radius=24,
            )
            surface.blit(shadow, confirm_rect.move(4, 6).topleft)

            surface.blit(panel_surf, confirm_rect.topleft)

            # Titel
            title_y = confirm_rect.top + padding_y_top
            draw_text(surface, title_text,
                      confirm_rect.centerx, title_y,
                      FONT_LARGE, YELLOW, center=True)

            # Frågetexten under titeln
            question_y = title_y + title_h + spacing_title_question
            draw_text(surface, question_text,
                      confirm_rect.centerx, question_y,
                      FONT_MEDIUM, WHITE, center=True)

            # Hover på knappar (med nya rektar)
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

                    title_surf = FONT_HUGE.render(TEXT[current_language]["FS_TRIGGER_TITLE"],
                                                  True, YELLOW)
                    title_surf.set_alpha(alpha)
                    title_rect = title_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 20))
                    surface.blit(title_surf, title_rect)

                    sub_surf = FONT_MEDIUM.render(TEXT[current_language]["CLICK_TO_CONTINUE"],
                                                  True, WHITE)
                    sub_surf.set_alpha(alpha)
                    sub_rect = sub_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 40))
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

                    # NYTT: när vi är tillbaka i base, visa ny random grid
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

                title_surf = FONT_HUGE.render(TEXT[current_language]["BONUS_OVER_TITLE"],
                                              True, CYAN)
                title_surf.set_alpha(alpha_end)
                title_rect = title_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 60))
                surface.blit(title_surf, title_rect)

                win_surf = FONT_LARGE.render(
                    TEXT[current_language]["BONUS_OVER_WIN"].format(amount=last_bonus_total),
                    True, WHITE
                )
                win_surf.set_alpha(alpha_end)
                win_rect = win_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
                surface.blit(win_surf, win_rect)

                hint_surf = FONT_MEDIUM.render(TEXT[current_language]["CLICK_TO_CONTINUE"],
                                               True, GREY)
                hint_surf.set_alpha(alpha_end)
                hint_rect = hint_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 60))
                surface.blit(hint_surf, hint_rect)

        if big_win_active:
            if now >= big_win_end_time:
                big_win_active = False
                if music_ducked_for_bigwin:
                    try:
                        music_duck_factor = 1.0
                        update_global_volume()
                        music_ducked_for_bigwin = False
                    except Exception:
                        pass
                    music_ducked_for_bigwin = False
            else:
                overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 200))
                surface.blit(overlay, (0, 0))

                scale_phase = (now // 120) % 2
                big_font = pygame.font.SysFont("arial", 64 + 6 * scale_phase, bold=True)

                draw_text(surface, TEXT[current_language]["BIG_WIN_TITLE"],
                          WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 40,
                          big_font, YELLOW, center=True)

                draw_text(surface, f"{last_win:.2f}", WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20,
                          FONT_LARGE, WHITE, center=True)
                        
        # ---------- SKALA TILL FÖNSTRET ----------
        window_w, window_h = screen.get_size()

        scale_x = window_w / BASE_WIDTH
        scale_y = window_h / BASE_HEIGHT
        render_scale = min(scale_x, scale_y)

        scaled_w = int(BASE_WIDTH * render_scale)
        scaled_h = int(BASE_HEIGHT * render_scale)

        offset_x = (window_w - scaled_w) // 2
        offset_y = (window_h - scaled_h) // 2
        render_offset = (offset_x, offset_y)

        scaled_surface = pygame.transform.smoothscale(game_surface, (scaled_w, scaled_h))

        screen.fill((0, 0, 0))
        screen.blit(scaled_surface, (offset_x, offset_y))

        pygame.display.flip()
        # VIKTIGT för webben:
        await asyncio.sleep(0)

    pygame.quit()
    #sys.exit()

if __name__ == "__main__":
    asyncio.run(main())
