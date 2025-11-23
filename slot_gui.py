import pygame
import sys
import random
import os  # för assets-path

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

pygame.init()

# ------------------- KONFIG / KONSTANTER -------------------

# Fönsterstorlek
WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 900

# Grid-layout
CELL_SIZE = 130
GRID_COLS = NUM_REELS
GRID_ROWS = VISIBLE_ROWS
GRID_WIDTH = GRID_COLS * CELL_SIZE
GRID_HEIGHT = GRID_ROWS * CELL_SIZE

GRID_X = (WINDOW_WIDTH - GRID_WIDTH) // 2
GRID_Y = 140

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

# Typsnitt
FONT_SMALL = pygame.font.SysFont("arial", 18)
FONT_MEDIUM = pygame.font.SysFont("arial", 26)
FONT_LARGE = pygame.font.SysFont("arial", 36)
FONT_HUGE = pygame.font.SysFont("arial", 52, bold=True)

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
BIG_WIN_DURATION_MS = 5000     # 5 sek

# Autospin delay i FS
FS_AUTO_SPIN_DELAY_MS = 900

# Extra delay efter en vinnande / retriggad FS, så att det hinner blinka längre
FS_AUTO_SPIN_DELAY_WIN_MS = 2000  # justera efter smak

# Overlay-tid för retrigger-meddelande
RETRIGGER_OVERLAY_DURATION_MS = 2200

# Spin-timing
SPIN_FIRST_STOP_MS = 800      # första hjulet stannar efter 0.8 s
SPIN_REEL_STEP_MS = 350       # nästa hjul 0.35 s senare osv
SPIN_SYMBOL_CHANGE_MS = 75    # hur ofta symbolerna byts under snurr

# Wild-reel drop-animation
WILD_DROP_STEP_MS = 150      # tid mellan att W / I / L / D dyker upp

# Symboler som används för spinn-animation (ingen scatter)
SPIN_SYMBOLS = [s for s in SYMBOLS if s != "S"]

# ------------------- ASSET-LOADING (PNG-stöd) -------------------

# Rotmapp för assets relativt denna fil
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.join(BASE_DIR, "assets")

# Debug: skriv ut vad som finns i assets
try:
    print("ASSET_DIR:", ASSET_DIR)
    print("Filer i assets:", os.listdir(ASSET_DIR))
except Exception as e:
    print("Kunde inte läsa assets-mappen:", e)


def load_image(filename, scale_to=None):
    full_path = os.path.join(ASSET_DIR, filename)
    try:
        img = pygame.image.load(full_path)

        # Bara convert_alpha om ett display-fönster redan är skapat
        if pygame.display.get_surface() is not None:
            img = img.convert_alpha()

        if scale_to is not None:
            img = pygame.transform.smoothscale(img, scale_to)

        return img
    except Exception as e:
        print(f"[VARNING] kunde inte ladda {full_path}: {e}")
        return None

def load_button_image(filename, max_w, max_h):
    """
    Ladda en knappbild och skala ned så att den får plats i (max_w, max_h)
    utan att ändra proportionerna. Skalar aldrig upp, bara ned.
    """
    full_path = os.path.join(ASSET_DIR, filename)
    try:
        img = pygame.image.load(full_path)

        if pygame.display.get_surface() is not None:
            img = img.convert_alpha()

        w, h = img.get_size()
        # skala så att den får plats men behåller aspect ratio
        scale = min(max_w / w, max_h / h, 1.0)
        new_size = (int(w * scale), int(h * scale))
        if new_size != (w, h):
            img = pygame.transform.smoothscale(img, new_size)
        return img
    except Exception as e:
        print(f"[VARNING] kunde inte ladda {full_path}: {e}")
        return None



def load_image_any(filenames, scale_to=None):
    """Försök flera filnamn och returnera första som funkar."""
    for name in filenames:
        img = load_image(name, scale_to)
        if img is not None:
            return img
    return None


# Bakgrunder (om du vill använda egna PNG:er)
BG_BASE_IMG = load_image("bg_base.png", (WINDOW_WIDTH, WINDOW_HEIGHT))
BG_FS_IMG = load_image("bg_fs.png", (WINDOW_WIDTH, WINDOW_HEIGHT))

SPIN_BUTTON_IMG = load_image("spin_button.png", (140, 140))
SPIN_BUTTON_IMG_DISABLED = load_image("spin_button_disabled.png", (140, 140))

# Buy-knapp (försök både disabled/disable ifall du döpt om)
BUY_BUTTON_IMG          = load_button_image("buy_button.png",         260, 100)
BUY_BUTTON_IMG_DISABLED = load_button_image("buy_button_disabled.png", 260, 100)
BUY_BUTTON_IMG_PRESSED  = load_button_image("buy_button_pressed.png", 260, 100)

# Bet +/- knappar – behåll aspect ratio, max 120x80
BET_MINUS_IMG          = load_button_image("bet_minus.png",          120, 80)
BET_MINUS_IMG_DISABLED = load_button_image("bet_minus_disabled.png", 120, 80)
BET_MINUS_IMG_PRESSED  = load_button_image("bet_minus_pressed.png",  120, 80)

BET_PLUS_IMG           = load_button_image("bet_plus.png",           120, 80)
BET_PLUS_IMG_DISABLED  = load_button_image("bet_plus_disabled.png",  120, 80)
BET_PLUS_IMG_PRESSED   = load_button_image("bet_plus_pressed.png",   120, 80)


# Symbolbilder – t.ex. assets/symbol_A.png osv
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
    """Visningsnamn för symboler."""
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
                      hover=False, disabled=False, img=None, img_disabled=None):
    cx, cy = center
    if disabled:
        base_col = (90, 90, 90)
    elif hover:
        base_col = tuple(min(255, int(ch * 1.2)) for ch in color)
    else:
        base_col = color

    if img is not None:
        # Rita PNG om finns
        img_to_use = img_disabled if disabled and img_disabled is not None else img
        rect = img_to_use.get_rect(center=center)
        surface.blit(img_to_use, rect)
    else:
        # Fallback: rita en cirkel
        pygame.draw.circle(surface, base_col, center, radius)
        pygame.draw.circle(surface, WHITE, center, radius, width=3)

    # Vi visar ingen text när vi har snygg PNG
    # txt_col = BLACK if not disabled else (180, 180, 180)
    # draw_text(surface, text, cx, cy, font, txt_col, center=True)


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


def find_winning_positions(grid, paytable, wild_reels=None):
    """
    Returnerar ett set med (row, col) som ingår i någon vinstkombination.
    Tar hänsyn till wild reels: hela wild-hjul markeras om de deltar i vinsten.
    """
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


def draw_grid(surface, grid, font, win_positions=None, time_ms=0,
              wild_reels=None, fs_mults=None,
              wild_drop_start_times=None):
    """
    Ritar grid med symboler.
    - win_positions blinkar feint
    - wild_reels (kolumner) markeras
    - wild-reels visas som W1/W2/W3/W4 PNG när deras drop startat
      (innan dess visas vanliga symboler)
    - om fs_mults finns: "xN" visas över respektive wild-reel
    """
    if grid is None:
        return

    win_positions = win_positions or set()
    wild_reels = set(wild_reels or [])
    fs_mults = fs_mults or {}
    wild_drop_start_times = wild_drop_start_times or {}

    blink_phase = (time_ms // 200) % 2  # 0 eller 1

    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            x = GRID_X + c * CELL_SIZE
            y = GRID_Y + r * CELL_SIZE
            cell_rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

            # Bakgrund
            if c in wild_reels:
                base_bg = (30, 50, 90)
            else:
                base_bg = DARK_GREY

            pygame.draw.rect(surface, base_bg, cell_rect, border_radius=16)

            # Vinst-blink
            if (r, c) in win_positions:
                if blink_phase == 0:
                    overlay_col = (255, 255, 255, 70)
                else:
                    overlay_col = (255, 255, 255, 25)
                overlay = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                overlay.fill(overlay_col)
                surface.blit(overlay, (x, y))

            # Kant
            border_color = CYAN if c in wild_reels else BLACK
            pygame.draw.rect(surface, border_color, cell_rect, width=2, border_radius=16)

            # Symbol / wild-symbol med drop-animation
            if c in wild_reels and c in wild_drop_start_times:
                # drop är igång -> bestäm hur många rader som ska visa WILD
                elapsed = max(0, time_ms - wild_drop_start_times[c])
                visible_rows = min(4, 1 + elapsed // WILD_DROP_STEP_MS)  # upp till 4 rader WILD

                if r < visible_rows:
                    sym_key = f"W{r+1}"  # W1, W2, W3, W4
                else:
                    sym_key = grid[r][c]
            elif c in wild_reels:
                # reel är wild men droppet har inte börjat -> visa vanliga symboler
                sym_key = grid[r][c]
            else:
                sym_key = grid[r][c]

            inner_rect = cell_rect.inflate(-16, -16)

            # PNG-baserad symbol om tillgänglig
            img = SYMBOL_IMAGES.get(sym_key)
            if img is not None:
                img_rect = img.get_rect(center=inner_rect.center)
                surface.blit(img, img_rect)
            else:
                sym_col = SYMBOL_COLORS.get(sym_key, WHITE)
                pygame.draw.rect(surface, sym_col, inner_rect, border_radius=12)
                text = symbol_display(sym_key)
                draw_text(surface, text, x + CELL_SIZE // 2, y + CELL_SIZE // 2,
                          font, BLACK, center=True)

    # Rita multipel ovanför wild-reels
    if wild_reels and fs_mults:
        for c in wild_reels:
            if c in fs_mults:
                cx = GRID_X + c * CELL_SIZE + CELL_SIZE // 2
                cy = GRID_Y - 22
                draw_text(surface, f"x{fs_mults[c]}", cx, cy, FONT_SMALL, YELLOW, center=True)


def main():
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Megaways Slot – GUI")

    clock = pygame.time.Clock()

    # ---------- Spelstatus ----------

    balance = 1000.0
    bet_index = 0
    bet = BET_LEVELS[bet_index]

    current_grid = spin_grid_same_probs()
    last_win = 0.0
    last_win_positions = set()

    # big win
    big_win_active = False
    big_win_end_time = 0

    # retrigger overlay
    retrigger_overlay_until = 0
    retrigger_overlay_text = ""

    # wild drop-animation state (per FS-spin)
    wild_drop_start_times = {}  # {reel_index: start_time_ms}

    # animation / spin
    is_spinning = False
    spin_start_time = 0
    reel_stop_times = [0] * GRID_COLS
    spin_result_applied = False
    final_grid = None

    # spin-animation grid (slöare symbolbyte)
    spin_anim_grid = None
    last_spin_anim_update = 0

    # free spins state
    game_mode = "base"          # "base" eller "fs"
    fs_spins_left = 0
    fs_total_win = 0.0
    fs_total_mult = 0.0
    current_wild_reels = []
    current_wild_mults = {}     # {reel_index: mult}

    # bonus state:
    # "none"            – inget pågående
    # "ready_to_start"  – bonus triggad / köpt, vänta på klick för att starta autospins
    # "running"         – free spins snurrar
    # "finished_waiting"– bonus klar, vänta på klick för att återgå till base
    bonus_state = "none"

    # om den aktuella bonusen är *köpt* (inte triggad via scatters)
    bonus_bought = False

    # autospin för free spins
    fs_next_spin_time = None

    # bonus slut-info
    last_bonus_total = 0.0

    message = ""

    # Buy-confirm overlay state
    buy_confirm_visible = False
    buy_confirm_cost = 0.0

    # Bet-knappar pressed state (för pressed PNG)
    bet_minus_held = False
    bet_plus_held = False

    # ------------------- KNAPP-POSITIONER / LAYOUT -------------------

    # SPIN-knapp – rund nere i höger hörn
    spin_radius = 70
    spin_center = (WINDOW_WIDTH - 220, WINDOW_HEIGHT - 200)
    # rektangel för hit-detection (enklare)
    spin_button_rect = pygame.Rect(
        spin_center[0] - spin_radius,
        spin_center[1] - spin_radius,
        spin_radius * 2,
        spin_radius * 2,
    )

    # Bet-belopp över spin-knappen
    bet_label_pos = (spin_center[0], spin_center[1] - spin_radius - 35)

    # Bet minus/plus UNDER spin-knappen
    # Hämta verklig storlek från bilderna
    buy_w, buy_h = BUY_BUTTON_IMG.get_size()
    minus_w, minus_h = BET_MINUS_IMG.get_size()
    plus_w, plus_h = BET_PLUS_IMG.get_size()

    # Bet minus/plus UNDER spin-knappen
    bet_minus_rect = pygame.Rect(
        spin_center[0] - 110,
        spin_center[1] + spin_radius,
        minus_w,
        minus_h,
    )
    bet_plus_rect = pygame.Rect(
        spin_center[0] + 30,
        spin_center[1] + spin_radius ,
        plus_w,
        plus_h,
    )

    # Köp FS-knapp: vänster om slot-grid – centrera höjden
    buy_button_rect = pygame.Rect(
        GRID_X - 70 - buy_w,              # lite padding från griden
        GRID_Y + GRID_HEIGHT // 2 - buy_h // 2,
        buy_w,
        buy_h,
    )



    # Buy-confirm overlay-layout
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

    running = True
    while running:
        dt = clock.tick(60)
        now = pygame.time.get_ticks()

        # ------------- EVENTLOOP -------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos

                # 1) Hantera buy-confirm overlay först
                if buy_confirm_visible:
                    if confirm_yes_rect.collidepoint(mx, my):
                        # Utför själva köpet
                        if balance >= buy_confirm_cost:
                            balance -= buy_confirm_cost
                            bonus_bought = True  # den här bonusen är köpt
                            # initiera free spins-bonus men starta inte direkt
                            game_mode = "fs"
                            fs_spins_left = N_FREE_SPINS
                            fs_total_win = 0.0
                            fs_total_mult = 0.0
                            current_wild_reels = []
                            current_wild_mults = {}
                            wild_drop_start_times = {}
                            last_win_positions = set()
                            message = f"Köpte free spins för {buy_confirm_cost:.2f}"
                            bonus_state = "ready_to_start"
                            fs_next_spin_time = None
                        else:
                            message = "För lite saldo för att köpa free spins!"

                        buy_confirm_visible = False
                        continue

                    elif confirm_no_rect.collidepoint(mx, my):
                        # Avbryt köp
                        buy_confirm_visible = False
                        message = ""
                        continue

                    # Klick någon annanstans på overlayen gör ingenting
                    continue

                # 2) Bonus-overlay klick
                if bonus_state == "ready_to_start":
                    # Starta bonus-autospin efter klick
                    bonus_state = "running"
                    fs_next_spin_time = now + FS_AUTO_SPIN_DELAY_MS
                    message = ""
                    continue

                if bonus_state == "finished_waiting":
                    # Avsluta bonus, tillbaka till base
                    bonus_state = "none"
                    game_mode = "base"
                    fs_spins_left = 0
                    fs_total_win = 0.0
                    fs_total_mult = 0.0
                    current_wild_reels = []
                    current_wild_mults = {}
                    wild_drop_start_times = {}
                    bonus_bought = False  # klar med köpt/triggad bonus
                    message = ""
                    continue

                # 3) Vanliga klick (om ingen overlay är aktiv)
                # Klick på bet minus/plus – endast i base-läge och när vi inte snurrar & ingen big win & ingen buy-confirm
                if (bonus_state == "none" and not is_spinning
                        and game_mode == "base" and not big_win_active
                        and not buy_confirm_visible):
                    if bet_minus_rect.collidepoint(mx, my):
                        if bet_index > 0:
                            bet_index -= 1
                            bet = BET_LEVELS[bet_index]
                            message = f"Bet ändrad till {bet}"
                        bet_minus_held = True
                    elif bet_plus_rect.collidepoint(mx, my):
                        if bet_index < len(BET_LEVELS) - 1:
                            bet_index += 1
                            bet = BET_LEVELS[bet_index]
                            message = f"Bet ändrad till {bet}"
                        bet_plus_held = True

                # Köp free spins (bara i base, inte under spin eller big win eller overlay)
                if (bonus_state == "none" and not is_spinning and game_mode == "base"
                        and not big_win_active and buy_button_rect.collidepoint(mx, my)
                        and not buy_confirm_visible):
                    cost = FS_BUY_MULT * bet
                    if balance >= cost:
                        # Visa confirm-overlay istället för att köpa direkt
                        buy_confirm_visible = True
                        buy_confirm_cost = cost
                    else:
                        message = "För lite saldo för att köpa free spins!"

                # Spin-knapp – i base-läge; i FS autospin endast via bonus_state=="running"
                if (bonus_state == "none"
                        and spin_button_rect.collidepoint(mx, my)
                        and not is_spinning and not big_win_active
                        and not buy_confirm_visible):
                    if game_mode == "base":
                        if balance < bet:
                            message = "För lite saldo för att spinna."
                        else:
                            balance -= bet
                            is_spinning = True
                            spin_result_applied = False
                            spin_start_time = now
                            # reel-stoptider: 0.8 s, 1.1 s, 1.4 s, ...
                            reel_stop_times = [
                                spin_start_time + SPIN_FIRST_STOP_MS + SPIN_REEL_STEP_MS * i
                                for i in range(GRID_COLS)
                            ]
                            final_grid = spin_grid_same_probs()
                            last_win = 0.0
                            last_win_positions = set()
                            wild_drop_start_times = {}
                            message = ""

                            # initiera spin-animationsgrid
                            spin_anim_grid = [
                                [random.choice(SPIN_SYMBOLS) for _ in range(GRID_COLS)]
                                for _ in range(GRID_ROWS)
                            ]
                            last_spin_anim_update = now

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                # Släpp pressed-state för +/- knappar
                bet_minus_held = False
                bet_plus_held = False

        # ------------- AUTOSPIN FÖR FREE SPINS -------------
        if (game_mode == "fs"
                and bonus_state == "running"
                and not is_spinning
                and fs_spins_left > 0
                and fs_total_mult < MAX_WIN_MULT
                and not big_win_active):

            if fs_next_spin_time is None:
                fs_next_spin_time = now + FS_AUTO_SPIN_DELAY_MS

            if now >= fs_next_spin_time:
                # starta ett free spin
                is_spinning = True
                spin_result_applied = False
                spin_start_time = now
                reel_stop_times = [
                    spin_start_time + SPIN_FIRST_STOP_MS + SPIN_REEL_STEP_MS * i
                    for i in range(GRID_COLS)
                ]
                final_grid = spin_grid_same_probs()

                # bestäm wild reels för detta FS-spin
                k = random.choices(
                    WILD_REEL_COUNTS, weights=WILD_REEL_COUNT_WEIGHTS, k=1
                )[0]
                if k <= 0:
                    current_wild_reels = []
                    current_wild_mults = {}
                else:
                    k = min(k, NUM_REELS)
                    current_wild_reels = random.sample(range(NUM_REELS), k)
                    # multiplikator FÖR VARJE wild reel
                    current_wild_mults = {}
                    for r_idx in current_wild_reels:
                        m = random.choices(FS_MULTIPLIERS, weights=FS_MULT_WEIGHTS, k=1)[0]
                        current_wild_mults[r_idx] = m

                wild_drop_start_times = {}  # reset för detta spin
                last_win = 0.0
                last_win_positions = set()
                message = ""
                fs_next_spin_time = None

                # initiera spin-animationsgrid
                spin_anim_grid = [
                    [random.choice(SPIN_SYMBOLS) for _ in range(GRID_COLS)]
                    for _ in range(GRID_ROWS)
                ]
                last_spin_anim_update = now

        # ------------- SPINLOGIK / ANIMATION UPDATE -------------
        if is_spinning:
            # uppdatera spin_anim_grid lite mer sällan (slöare snurr)
            if spin_anim_grid is not None and now - last_spin_anim_update >= SPIN_SYMBOL_CHANGE_MS:
                for r in range(GRID_ROWS):
                    for c in range(GRID_COLS):
                        if now < reel_stop_times[c]:
                            # hjulet snurrar fortfarande -> slumpa symbol
                            spin_anim_grid[r][c] = random.choice(SPIN_SYMBOLS)
                        else:
                            # hjulet har "stannat" -> visa resultat-kolumnen
                            spin_anim_grid[r][c] = final_grid[r][c]
                last_spin_anim_update = now

                # starta wild-drop på hjul vars stoppid har passerats
                if game_mode == "fs" and bonus_state == "running":
                    for c in current_wild_reels:
                        if c not in wild_drop_start_times and now >= reel_stop_times[c]:
                            wild_drop_start_times[c] = now

            # kolla om alla hjul har stannat
            if all(now >= t for t in reel_stop_times) and not spin_result_applied:
                # spin är färdig – applicera resultat
                is_spinning = False
                spin_result_applied = True
                current_grid = final_grid

                # ev. avsluta big win overlay från tidigare spin
                if big_win_active and now >= big_win_end_time:
                    big_win_active = False

                if game_mode == "base":
                    # base game win
                    base_mult = evaluate_megaways_win(current_grid, paytable)
                    win_amount = base_mult * bet
                    balance += win_amount
                    last_win = win_amount
                    last_win_positions = find_winning_positions(
                        current_grid, paytable
                    )

                    # big win?
                    if win_amount >= BIG_WIN_THRESHOLD_MULT * bet:
                        big_win_active = True
                        big_win_end_time = now + BIG_WIN_DURATION_MS

                    # kolla scatter-trigger
                    scatter_count = sum(
                        1
                        for row in current_grid
                        for sym in row
                        if sym == "S"
                    )

                    if scatter_count == 3:
                        # starta bonus-läge, men autostarta inte
                        game_mode = "fs"
                        fs_spins_left = N_FREE_SPINS
                        fs_total_win = 0.0
                        fs_total_mult = 0.0
                        current_wild_reels = []
                        current_wild_mults = {}
                        wild_drop_start_times = {}
                        last_win_positions = set()
                        bonus_bought = False  # triggat via scatters
                        message = "FREE SPINS triggat!"
                        bonus_state = "ready_to_start"
                        fs_next_spin_time = None
                    else:
                        if win_amount > 0:
                            message = f"Vinst: {win_amount:.2f}"
                        else:
                            message = ""

                elif game_mode == "fs":
                    # free spins-win – använder current_wild_reels och current_wild_mults
                    base_mult = evaluate_megaways_win(
                        current_grid, paytable, wild_reels=current_wild_reels
                    )

                    if current_wild_mults:
                        spin_mult_factor = sum(current_wild_mults.values())
                    else:
                        spin_mult_factor = 1

                    spin_mult = base_mult * spin_mult_factor

                    # max win-cappning i multiplar
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

                    last_win_positions = find_winning_positions(
                        current_grid, paytable, wild_reels=current_wild_reels
                    )

                    # big win i bonus?
                    if spin_win >= BIG_WIN_THRESHOLD_MULT * bet:
                        big_win_active = True
                        big_win_end_time = now + BIG_WIN_DURATION_MS

                    # --- RETRIGGERS I BONUSEN: 2 eller 3 scatters ger extra spins ---
                    #  men scatters under wild-reels får INTE räknas
                    scatter_count_nonwild = 0
                    for r in range(len(current_grid)):
                        for c in range(len(current_grid[0])):
                            if c in current_wild_reels:
                                continue
                            if current_grid[r][c] == "S":
                                scatter_count_nonwild += 1

                    extra_spins = 0
                    if scatter_count_nonwild == 2:
                        extra_spins = 1
                    elif scatter_count_nonwild == 3:
                        extra_spins = 3

                    # förbrukar ett spin
                    fs_spins_left -= 1
                    # lägg till extra + retrigger-overlay
                    if extra_spins > 0:
                        fs_spins_left += extra_spins
                        retrigger_overlay_text = f"RETRIGGER! +{extra_spins} SPINS"
                        retrigger_overlay_until = now + RETRIGGER_OVERLAY_DURATION_MS

                    # kolla om bonusen är slut
                    if fs_spins_left <= 0 or fs_total_mult >= MAX_WIN_MULT:
                        last_bonus_total = fs_total_win
                        message = f"FREE SPINS över! Total: {fs_total_win:.2f}"
                        bonus_state = "finished_waiting"
                        fs_next_spin_time = None
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

                    # planera nästa autospin (om bonusen fortsätter att vara running)
                    if bonus_state == "running":
                        if spin_win > 0 or extra_spins > 0:
                            delay = FS_AUTO_SPIN_DELAY_WIN_MS
                        else:
                            delay = FS_AUTO_SPIN_DELAY_MS
                        fs_next_spin_time = now + delay

        # ------------- RITNING -------------
        # Bakgrund – PNG om finns, annars färg
        if game_mode == "fs" and BG_FS_IMG is not None:
            screen.blit(BG_FS_IMG, (0, 0))
        elif game_mode == "base" and BG_BASE_IMG is not None:
            screen.blit(BG_BASE_IMG, (0, 0))
        else:
            screen.fill(BG_FS if game_mode == "fs" else BG_BASE)

        # Titel
        if game_mode == "fs":
            draw_text(
                screen,
                "MEGAWAYS – FREE SPINS",
                WINDOW_WIDTH // 2,
                50,
                FONT_HUGE,
                YELLOW,
                center=True,
            )
        else:
            draw_text(
                screen,
                "MEGAWAYS SLOT",
                WINDOW_WIDTH // 2,
                50,
                FONT_HUGE,
                CYAN,
                center=True,
            )

        # Info över grid (t.ex. senaste vinst)
        draw_text(
            screen,
            f"Senaste vinst: {last_win:.2f}",
            WINDOW_WIDTH // 2,
            100,
            FONT_MEDIUM,
            WHITE,
            center=True,
        )

        # FS-info (vänstersida om vi är i bonus)
        if game_mode == "fs":
            left_x = 40
            base_y = 150
            if bonus_state in ("ready_to_start", "running", "finished_waiting"):
                draw_text(screen, "BONUSLÄGE!", left_x, base_y, FONT_MEDIUM, YELLOW)
                draw_text(screen, f"FS spins kvar: {fs_spins_left}", left_x, base_y + 40, FONT_MEDIUM, YELLOW)
                draw_text(screen, f"FS total vinst: {fs_total_win:.2f}", left_x, base_y + 80, FONT_MEDIUM, YELLOW)
                if current_wild_reels and bonus_state == "running":
                    reels_str = ", ".join(
                        f"{r+1}:x{current_wild_mults.get(r, 1)}" for r in current_wild_reels
                    )
                    draw_text(
                        screen,
                        f"Wild reels (hjul:mult): {reels_str}",
                        left_x,
                        base_y + 120,
                        FONT_SMALL,
                        ORANGE,
                    )

        # Grid
        now_ms = pygame.time.get_ticks()
        # vilka wild-hjul ska vara aktiva visuellt? (de som påbörjat droppet)
        active_wild_reels = set(wild_drop_start_times.keys()) if (game_mode == "fs" and bonus_state == "running") else None

        if is_spinning and spin_anim_grid is not None:
            draw_grid(
                screen,
                spin_anim_grid,
                FONT_MEDIUM,
                win_positions=set(),
                time_ms=now_ms,
                wild_reels=active_wild_reels,
                fs_mults=current_wild_mults if game_mode == "fs" and bonus_state == "running" else None,
                wild_drop_start_times=wild_drop_start_times,
            )
        else:
            draw_grid(
                screen,
                current_grid,
                FONT_MEDIUM,
                win_positions=last_win_positions,
                time_ms=now_ms,
                wild_reels=active_wild_reels,
                fs_mults=current_wild_mults if game_mode == "fs" and bonus_state == "running" else None,
                wild_drop_start_times=wild_drop_start_times,
            )

        # Bet-belopp ovanför spin-knappen
        draw_text(screen, f"Bet: {bet:.2f}", bet_label_pos[0], bet_label_pos[1], FONT_MEDIUM, WHITE, center=True)

        # Bet-knappar under spin-knapp
        mouse_pos = pygame.mouse.get_pos()
        hover_minus = bet_minus_rect.collidepoint(mouse_pos)
        hover_plus = bet_plus_rect.collidepoint(mouse_pos)

        bet_buttons_disabled = (game_mode != "base"
                                or big_win_active
                                or is_spinning
                                or bonus_state != "none"
                                or buy_confirm_visible)

        # välj rätt PNG för minus
        if bet_buttons_disabled:
            minus_img = BET_MINUS_IMG_DISABLED
        elif bet_minus_held:
            minus_img = BET_MINUS_IMG_PRESSED
        else:
            minus_img = BET_MINUS_IMG

        draw_button(
            screen,
            bet_minus_rect,
            "",
            FONT_LARGE,
            RED,
            hover_minus,
            disabled=bet_buttons_disabled,
            img=minus_img,
            img_disabled=None,
        )

        # välj rätt PNG för plus
        if bet_buttons_disabled:
            plus_img = BET_PLUS_IMG_DISABLED
        elif bet_plus_held:
            plus_img = BET_PLUS_IMG_PRESSED
        else:
            plus_img = BET_PLUS_IMG

        draw_button(
            screen,
            bet_plus_rect,
            "",
            FONT_LARGE,
            GREEN,
            hover_plus,
            disabled=bet_buttons_disabled,
            img=plus_img,
            img_disabled=None,
        )

        # SPIN-knapp (rund, nere till höger)
        hover_spin = spin_button_rect.collidepoint(mouse_pos)
        spin_label = "SPIN" if game_mode == "base" else "FS"
        spin_disabled = (is_spinning or big_win_active
                         or (game_mode == "fs")  # inga manuella spins i bonus
                         or bonus_state != "none"
                         or buy_confirm_visible)
        draw_round_button(
            screen,
            spin_center,
            spin_radius,
            spin_label,
            FONT_MEDIUM,
            ORANGE,
            hover=hover_spin,
            disabled=spin_disabled,
            img=SPIN_BUTTON_IMG,
            img_disabled=SPIN_BUTTON_IMG_DISABLED,
        )

        # Buy FS-knapp (vänster om grid)
        hover_buy = buy_button_rect.collidepoint(mouse_pos)
        cost = FS_BUY_MULT * bet

        # när knappen *får* klickas
        buy_disabled_input = (game_mode != "base"
                              or big_win_active
                              or is_spinning
                              or bonus_state != "none"
                              or buy_confirm_visible
                              or balance < cost)

        # bild-logik:
        # - om bonusen är köpt och vi är i fs -> pressed-bild
        # - om vi är i base och inte har råd -> disabled-bild
        # - annars -> vanlig bild
        if bonus_bought and game_mode == "fs":
            buy_img = BUY_BUTTON_IMG_PRESSED
        elif game_mode == "base" and balance < cost:
            buy_img = BUY_BUTTON_IMG_DISABLED
        else:
            buy_img = BUY_BUTTON_IMG

        draw_button(
            screen,
            buy_button_rect,
            "",
            FONT_SMALL,
            YELLOW,
            hover_buy,
            disabled=buy_disabled_input,
            img=buy_img,
            img_disabled=None,
        )

        # Saldo längst nere i vänster hörn
        draw_text(
            screen,
            f"Saldo: {balance:.2f}",
            30,
            WINDOW_HEIGHT - 40,
            FONT_MEDIUM,
            WHITE,
            center=False,
        )

        # Meddelanderad (mitt nere, ovan saldo)
        if message:
            draw_text(
                screen,
                message,
                WINDOW_WIDTH // 2,
                WINDOW_HEIGHT - 40,
                FONT_SMALL,
                GREY,
                center=True,
            )

        # Bonus-overlays (klick-baserade, ej tidsbaserade)
        if bonus_state == "ready_to_start":
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            draw_text(screen, "FREE SPINS TRIGGADE!", WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 40,
                      FONT_HUGE, YELLOW, center=True)
            draw_text(screen, "Klicka för att starta bonus", WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20,
                      FONT_MEDIUM, WHITE, center=True)

        elif bonus_state == "finished_waiting":
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            draw_text(screen, "BONUS OVER", WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 60,
                      FONT_HUGE, CYAN, center=True)
            draw_text(screen, f"Du vann: {last_bonus_total:.2f}", WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2,
                      FONT_LARGE, WHITE, center=True)
            draw_text(screen, "Klicka för att fortsätta", WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 60,
                      FONT_MEDIUM, GREY, center=True)

        # Retrigger-overlay (tidsbaserad, bara när bonusen kör)
        if bonus_state == "running" and now < retrigger_overlay_until:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            screen.blit(overlay, (0, 0))
            draw_text(screen, retrigger_overlay_text,
                      WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2,
                      FONT_LARGE, YELLOW, center=True)

        # Buy-confirm overlay (ovanpå allt annat utom big win)
        if buy_confirm_visible:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            screen.blit(overlay, (0, 0))

            pygame.draw.rect(screen, (30, 30, 60), confirm_rect, border_radius=16)
            pygame.draw.rect(screen, YELLOW, confirm_rect, width=3, border_radius=16)

            draw_text(screen, "KÖP BONUS?", confirm_rect.centerx, confirm_rect.top + 40,
                      FONT_LARGE, YELLOW, center=True)
            draw_text(
                screen,
                f"Vill du köpa free spins för {buy_confirm_cost:.2f} kr?",
                confirm_rect.centerx,
                confirm_rect.top + 100,
                FONT_MEDIUM,
                WHITE,
                center=True,
            )

            mouse_pos = pygame.mouse.get_pos()
            yes_hover = confirm_yes_rect.collidepoint(mouse_pos)
            no_hover = confirm_no_rect.collidepoint(mouse_pos)

            draw_button(screen, confirm_yes_rect, "JA", FONT_MEDIUM, GREEN,
                        hover=yes_hover, disabled=False)
            draw_button(screen, confirm_no_rect, "NEJ", FONT_MEDIUM, RED,
                        hover=no_hover, disabled=False)

        # Big win overlay (tar över allt)
        if big_win_active:
            if now >= big_win_end_time:
                big_win_active = False
            else:
                overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 200))
                screen.blit(overlay, (0, 0))

                # liten puls i textstorlek
                scale_phase = (now // 120) % 2
                big_font = pygame.font.SysFont("arial", 64 + 6 * scale_phase, bold=True)

                draw_text(screen, "BIG WIN!", WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 40,
                          big_font, YELLOW, center=True)
                draw_text(screen, f"{last_win:.2f}", WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20,
                          FONT_LARGE, WHITE, center=True)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
