import pygame
import sys
import random
import os  # NYTT

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

# Grid-layout (ännu större grid nu)
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
    "W": (200, 255, 255),  # Wild reel symbol
}

# Big win
BIG_WIN_THRESHOLD_MULT = 30.0  # 30x bet
BIG_WIN_DURATION_MS = 5000     # 5 sek

# Autospin delay i FS
FS_AUTO_SPIN_DELAY_MS = 900

# Extra delay efter en vinnande FS, så att det hinner blinka längre
FS_AUTO_SPIN_DELAY_WIN_MS = 2000  # justera efter smak

# Overlay-tid för retrigger-meddelande
RETRIGGER_OVERLAY_DURATION_MS = 2200

# Wild-drop: hur länge mellan varje rad (W → WI → WIL → WILD)
WILD_DROP_STEP_MS = 200  # 0.2 s per rad

# Spin-timing
SPIN_FIRST_STOP_MS = 800      # första hjulet stannar efter 0.8 s
SPIN_REEL_STEP_MS = 300       # nästa hjul 0.3 s senare osv
SPIN_SYMBOL_CHANGE_MS = 60    # hur ofta symbolerna byts under snurr

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


# Bakgrunder (om du vill använda egna PNG:er)
BG_BASE_IMG = load_image("bg_base.png", (WINDOW_WIDTH, WINDOW_HEIGHT))
BG_FS_IMG   = load_image("bg_fs.png",  (WINDOW_WIDTH, WINDOW_HEIGHT))

SPIN_BUTTON_IMG          = load_image("spin_button.png", (140, 140))
SPIN_BUTTON_IMG_DISABLED = load_image("spin_button_disabled.png", (140, 140))

BUY_BUTTON_IMG           = load_image("buy_button.png", (180, 70))
BUY_BUTTON_IMG_DISABLED  = load_image("buy_button_disabled.png", (180, 70))

# --- bet +/- knappar ---
BET_MINUS_IMG           = load_image("bet_minus.png", (60, 50))
BET_MINUS_IMG_DISABLED  = load_image("bet_minus_disabled.png", (60, 50))
BET_PLUS_IMG            = load_image("bet_plus.png", (60, 50))
BET_PLUS_IMG_DISABLED   = load_image("bet_plus_disabled.png", (60, 50))

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

    # Text på spin-knappen döljs eftersom PNG:en har grafiken
    # (om du vill ha text ovanpå, avkommentera)
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

    # för +/- och buy använder vi tom text, PNG:en har symbolen
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
              wild_reels=None, fs_mults=None, wild_rows_visible=None):
    """
    Ritar grid med symboler.
    - win_positions blinkar feint
    - wild_reels (kolumner) markeras
    - wild-reels visas som W / I / L / D-ikon, med drop-animation:
      wild_rows_visible[c] = antal rader (1–4) som ska visas i kolumn c
    - om fs_mults finns: "xN" visas över respektive wild-reel
    """
    if grid is None:
        return

    win_positions = win_positions or set()
    wild_reels = set(wild_reels or [])
    fs_mults = fs_mults or {}
    wild_rows_visible = wild_rows_visible or {}

    blink_phase = (time_ms // 200) % 2  # 0 eller 1

    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            x = GRID_X + c * CELL_SIZE
            y = GRID_Y + r * CELL_SIZE
            cell_rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

            # Hur många wild-rader är aktiva i denna kolumn?
            rows_visible = wild_rows_visible.get(c, None)
            is_wild_col = (rows_visible is not None and c in wild_reels)

            # Bakgrund
            if is_wild_col:
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
            border_color = CYAN if is_wild_col else BLACK
            pygame.draw.rect(surface, border_color, cell_rect, width=2, border_radius=16)

            # Symbol / wild-symbol
            sym_key = None

            if is_wild_col:
                # Bestäm vilken bokstav som ska visas på denna rad, givet hur många rader är aktiva
                if rows_visible >= 1 and r == 0:
                    sym_key = "W1"
                elif rows_visible >= 2 and r == 1:
                    sym_key = "W2"
                elif rows_visible >= 3 and r == 2:
                    sym_key = "W3"
                elif rows_visible >= 4 and r == 3:
                    sym_key = "W4"
                else:
                    sym_key = None  # denna rad har inte "droppat" än → ingen symbol
            else:
                sym_key = grid[r][c]

            inner_rect = cell_rect.inflate(-16, -16)

            # PNG-baserad symbol om tillgänglig
            if sym_key is not None:
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

    # Rita multipel ovanför wild-reels (bara när droppen börjat)
    if wild_reels and fs_mults:
        for c in wild_reels:
            if c not in wild_rows_visible:
                continue
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

    # wild drop state (för bonus-wild-reels)
    wild_drop_start_times = {}   # {reel_index: start_time_ms}
    wild_drop_done_reels = set() # reels som har full WILD (4 rader)

    # bonus state:
    # "none"            – inget pågående
    # "ready_to_start"  – bonus triggad, vänta på klick för att starta autospins
    # "running"         – free spins snurrar
    # "finished_waiting"– bonus klar, vänta på klick för att återgå till base
    bonus_state = "none"

    # autospin för free spins
    fs_next_spin_time = None

    # bonus slut-info
    last_bonus_total = 0.0

    message = ""

    # ------------------- KNAPP-POSITIONER / LAYOUT -------------------

    # SPIN-knapp – rund nere i höger hörn
    spin_radius = 70
    spin_center = (WINDOW_WIDTH - 140, WINDOW_HEIGHT - 140)
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
    bet_minus_rect = pygame.Rect(
        spin_center[0] - 90,
        spin_center[1] + spin_radius + 10,
        60,
        50,
    )
    bet_plus_rect = pygame.Rect(
        spin_center[0] + 30,
        spin_center[1] + spin_radius + 10,
        60,
        50,
    )

    # Köp FS-knapp: vänster om slot-grid
    buy_button_rect = pygame.Rect(
        GRID_X - 220,
        GRID_Y + GRID_HEIGHT // 2 - 35,
        180,
        70,
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

                # Hantera bonus-overlay klick först
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
                    wild_drop_done_reels = set()
                    message = ""
                    continue

                # Om vi är i bonus_running eller base utan overlay -> vanliga klick
                # Klick på bet minus/plus – endast i base-läge och när vi inte snurrar & ingen big win overlay
                if (bonus_state == "none" and not is_spinning
                        and game_mode == "base" and not big_win_active):
                    if bet_minus_rect.collidepoint(mx, my):
                        if bet_index > 0:
                            bet_index -= 1
                            bet = BET_LEVELS[bet_index]
                            message = f"Bet ändrad till {bet}"
                    elif bet_plus_rect.collidepoint(mx, my):
                        if bet_index < len(BET_LEVELS) - 1:
                            bet_index += 1
                            bet = BET_LEVELS[bet_index]
                            message = f"Bet ändrad till {bet}"

                # Köp free spins (bara i base, inte under spin eller big win eller overlay)
                if (bonus_state == "none" and not is_spinning and game_mode == "base"
                        and not big_win_active and buy_button_rect.collidepoint(mx, my)):
                    cost = FS_BUY_MULT * bet
                    if balance >= cost:
                        balance -= cost
                        # initiera free spins-bonus men starta inte direkt
                        game_mode = "fs"
                        fs_spins_left = N_FREE_SPINS
                        fs_total_win = 0.0
                        fs_total_mult = 0.0
                        current_wild_reels = []
                        current_wild_mults = {}
                        wild_drop_start_times = {}
                        wild_drop_done_reels = set()
                        last_win_positions = set()
                        message = f"Köpte free spins för {cost:.2f}"
                        bonus_state = "ready_to_start"
                        fs_next_spin_time = None
                    else:
                        message = "För lite saldo för att köpa free spins!"

                # Spin-knapp – i base-läge; i FS autospin endast via bonus_state=="running"
                if (bonus_state == "none"
                        and spin_button_rect.collidepoint(mx, my)
                        and not is_spinning and not big_win_active):
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
                            message = ""

                            # base game: inga wild-reels
                            current_wild_reels = []
                            current_wild_mults = {}
                            wild_drop_start_times = {}
                            wild_drop_done_reels = set()

                            # initiera spin-animationsgrid
                            spin_anim_grid = [
                                [random.choice(SPIN_SYMBOLS) for _ in range(GRID_COLS)]
                                for _ in range(GRID_ROWS)
                            ]
                            last_spin_anim_update = now

                    # game_mode == "fs": ignoreras (FS sköts med autospin när bonus_state=="running")

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

                # bestäm wild reels för detta FS-spin (synkad med slot_math)
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
                    for r in current_wild_reels:
                        m = random.choices(FS_MULTIPLIERS, weights=FS_MULT_WEIGHTS, k=1)[0]
                        current_wild_mults[r] = m

                # reset wild-drop state för detta spin
                wild_drop_start_times = {}
                wild_drop_done_reels = set()

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

            # Uppdatera wild-drop state under snurr (endast i FS)
            if game_mode == "fs" and current_wild_reels:
                for c in current_wild_reels:
                    # wild-droppen får inte börja förrän hjulet faktiskt stannat
                    if now >= reel_stop_times[c]:
                        if c not in wild_drop_start_times:
                            wild_drop_start_times[c] = now
                        t = now - wild_drop_start_times[c]
                        if t >= 4 * WILD_DROP_STEP_MS:
                            wild_drop_done_reels.add(c)

            # kolla om alla hjul har stannat, och om vi FÅR applicera resultatet
            if all(now >= t for t in reel_stop_times):
                can_apply = False
                if not current_wild_reels or game_mode != "fs":
                    # Inga wild-reels (eller inte i bonus) → kan applicera direkt
                    can_apply = True
                else:
                    # I bonus: vänta tills alla wild-reels är färdigdroppade
                    if all(c in wild_drop_done_reels for c in current_wild_reels):
                        can_apply = True

                if can_apply and not spin_result_applied:
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
                            wild_drop_done_reels = set()
                            last_win_positions = set()
                            message = "FREE SPINS triggat!"
                            bonus_state = "ready_to_start"
                            fs_next_spin_time = None
                        else:
                            if win_amount > 0:
                                message = f"Vinst: {win_amount:.2f}"
                            else:
                                # skriv inget vid nollvinst
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
                            # vi stannar kvar i game_mode="fs" tills spelaren klickar vidare
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
                            # längre paus om spinnet vann något ELLER retriggade,
                            # så både vinst-blink och retrigger-overlay hinner synas
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
                    reels_str = ", ".join(f"{r+1}:x{current_wild_mults.get(r, 1)}" for r in current_wild_reels)
                    draw_text(
                        screen,
                        f"Wild reels (hjul:mult): {reels_str}",
                        left_x,
                        base_y + 120,
                        FONT_SMALL,
                        ORANGE,
                    )

        # Beräkna hur många wild-rader som är synliga per kolumn (för animation)
        now_ms = pygame.time.get_ticks()
        wild_rows_visible = {}
        if game_mode == "fs" and current_wild_reels:
            for c in current_wild_reels:
                # Droppen får börja först när den reelen faktiskt har stannat
                if is_spinning and now_ms < reel_stop_times[c]:
                    continue

                # sätt starttid om inte redan
                if c not in wild_drop_start_times:
                    wild_drop_start_times[c] = now_ms
                    t = 0
                else:
                    t = now_ms - wild_drop_start_times[c]

                steps = int(t // WILD_DROP_STEP_MS)
                rows_visible = max(0, min(4, steps + 1))
                if rows_visible > 0:
                    wild_rows_visible[c] = rows_visible
                if rows_visible >= 4:
                    wild_drop_done_reels.add(c)

        # Grid
        if is_spinning and spin_anim_grid is not None:
            draw_grid(
                screen,
                spin_anim_grid,
                FONT_MEDIUM,
                win_positions=set(),
                time_ms=now_ms,
                wild_reels=current_wild_reels if game_mode == "fs" and bonus_state == "running" else None,
                fs_mults=current_wild_mults if game_mode == "fs" and bonus_state == "running" else None,
                wild_rows_visible=wild_rows_visible if bonus_state == "running" else None,
            )
        else:
            draw_grid(
                screen,
                current_grid,
                FONT_MEDIUM,
                win_positions=last_win_positions,
                time_ms=now_ms,
                wild_reels=current_wild_reels if game_mode == "fs" and bonus_state == "running" else None,
                fs_mults=current_wild_mults if game_mode == "fs" and bonus_state == "running" else None,
                wild_rows_visible=wild_rows_visible if bonus_state == "running" else None,
            )

        # Bet-belopp ovanför spin-knappen
        draw_text(screen, f"Bet: {bet:.2f}", bet_label_pos[0], bet_label_pos[1], FONT_MEDIUM, WHITE, center=True)

        # Bet-knappar under spin-knapp
        hover_minus = bet_minus_rect.collidepoint(pygame.mouse.get_pos())
        hover_plus = bet_plus_rect.collidepoint(pygame.mouse.get_pos())
        bet_buttons_disabled = (game_mode != "base"
                                or big_win_active
                                or is_spinning
                                or bonus_state != "none")
        draw_button(
            screen,
            bet_minus_rect,
            "",                      # ingen text, PNG:en har symbolen
            FONT_LARGE,
            RED,
            hover_minus,
            disabled=bet_buttons_disabled,
            img=BET_MINUS_IMG,
            img_disabled=BET_MINUS_IMG_DISABLED,
        )

        draw_button(
            screen,
            bet_plus_rect,
            "",                      # ingen text, PNG:en har symbolen
            FONT_LARGE,
            GREEN,
            hover_plus,
            disabled=bet_buttons_disabled,
            img=BET_PLUS_IMG,
            img_disabled=BET_PLUS_IMG_DISABLED,
        )

        # SPIN-knapp (rund, nere till höger)
        mouse_pos = pygame.mouse.get_pos()
        hover_spin = spin_button_rect.collidepoint(mouse_pos)
        spin_label = "SPIN" if game_mode == "base" else "FS"
        spin_disabled = (is_spinning or big_win_active
                         or (game_mode == "fs")  # inga manuella spins i bonus
                         or bonus_state != "none")
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
        hover_buy = buy_button_rect.collidepoint(pygame.mouse.get_pos())
        buy_disabled = (game_mode != "base"
                        or big_win_active
                        or is_spinning
                        or bonus_state != "none")
        draw_button(
            screen,
            buy_button_rect,
            "",
            FONT_SMALL,
            YELLOW,
            hover_buy,
            disabled=buy_disabled,
            img=BUY_BUTTON_IMG,
            img_disabled=BUY_BUTTON_IMG_DISABLED,
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
