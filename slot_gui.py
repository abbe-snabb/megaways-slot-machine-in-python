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

# Bas-upplösning (intern koordinatsystem)
BASE_WIDTH = 1600
BASE_HEIGHT = 900

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
GRID_Y = 170

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

# FS transition (scatter trigger) timings
SCATTER_FLASH_DURATION_MS = 1500   # scatters blinkar
FS_FADEOUT_DURATION_MS = 1000      # används som duration både för fade in och fade out

# Autospin delay i FS
FS_AUTO_SPIN_DELAY_MS = 900

# Extra delay efter en vinnande / retriggad FS
FS_AUTO_SPIN_DELAY_WIN_MS = 2000

# Overlay-tid för retrigger-meddelande
RETRIGGER_OVERLAY_DURATION_MS = 2200

# Spin-timing
SPIN_FIRST_STOP_MS = 800
SPIN_REEL_STEP_MS = 350
SPIN_SYMBOL_CHANGE_MS = 75

# Wild-reel drop-animation
WILD_DROP_STEP_MS = 250

# Symboler som används för spinn-animation (ingen scatter)
SPIN_SYMBOLS = [s for s in SYMBOLS if s != "S"]

# Bonus-slut-transition (FS -> base)
END_FS_FADE_DURATION_MS = 1000

# ------------------- ASSET-LOADING (PNG-stöd) -------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.join(BASE_DIR, "assets")

try:
    print("ASSET_DIR:", ASSET_DIR)
    print("Filer i assets:", os.listdir(ASSET_DIR))
except Exception as e:
    print("Kunde inte läsa assets-mappen:", e)


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

SPIN_BUTTON_IMG = load_image("spin_button.png", (140, 140))
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
                      hover=False, disabled=False, img=None, img_disabled=None):
    cx, cy = center
    if disabled:
        base_col = (90, 90, 90)
    elif hover:
        base_col = tuple(min(255, int(ch * 1.2)) for ch in color)
    else:
        base_col = color

    if img is not None:
        img_to_use = img_disabled if disabled and img_disabled is not None else img
        rect = img_to_use.get_rect(center=center)
        surface.blit(img_to_use, rect)
    else:
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


def draw_grid(surface, grid, font, win_positions=None, time_ms=0,
              wild_reels=None, fs_mults=None,
              wild_drop_start_times=None):
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

            if c in wild_reels and c in wild_drop_start_times:
                elapsed = max(0, time_ms - wild_drop_start_times[c])
                visible_rows = min(4, 1 + elapsed // WILD_DROP_STEP_MS)
                if r < visible_rows:
                    sym_key = f"W{r + 1}"
                else:
                    sym_key = grid[r][c]
            elif c in wild_reels:
                sym_key = grid[r][c]
            else:
                sym_key = grid[r][c]

            inner_rect = cell_rect.inflate(-18, -18)
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


def main():
    screen = pygame.display.set_mode((BASE_WIDTH, BASE_HEIGHT)) #screen = pygame.display.set_mode((BASE_WIDTH, BASE_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Megaways Slot – GUI")

    game_surface = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))
    clock = pygame.time.Clock()

    render_scale = 1.0
    render_offset = (0, 0)

    # ---------- Spelstatus ----------
    balance = 1000.0
    bet_index = 0
    bet = BET_LEVELS[bet_index]

    current_grid = spin_grid_same_probs()
    last_win = 0.0
    last_win_positions = set()

    big_win_active = False
    big_win_end_time = 0

    retrigger_overlay_until = 0
    retrigger_overlay_text = ""

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

    forced_scatter_spin = False

    end_fs_transition_active = False
    end_fs_transition_start = 0
    end_fs_transition_phase = None

    # ------------------- LAYOUT (bas-koords) -------------------

    spin_radius = 70
    spin_center = (WINDOW_WIDTH - 220, WINDOW_HEIGHT - 200)
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
        spin_center[0] - 110,
        spin_center[1] + spin_radius,
        minus_w,
        minus_h,
    )
    bet_plus_rect = pygame.Rect(
        spin_center[0] + 30,
        spin_center[1] + spin_radius,
        plus_w,
        plus_h,
    )

    buy_button_rect = pygame.Rect(
        GRID_X - 70 - buy_w,
        GRID_Y + GRID_HEIGHT // 2 - buy_h // 2,
        buy_w,
        buy_h,
    )

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
        dt = clock.tick(120)
        now = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                wx, wy = event.pos
                offset_x, offset_y = render_offset
                mx = (wx - offset_x) / render_scale
                my = (wy - offset_y) / render_scale

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
                    if game_mode == "base":
                        if balance < bet:
                            message = "För lite saldo för att spinna."
                        else:
                            balance -= bet
                            is_spinning = True
                            spin_result_applied = False
                            spin_start_time = now
                            reel_stop_times = [
                                spin_start_time + SPIN_FIRST_STOP_MS + SPIN_REEL_STEP_MS * i
                                for i in range(GRID_COLS)
                            ]
                            final_grid = spin_grid_same_probs()
                            last_win = 0.0
                            last_win_positions = set()
                            wild_drop_start_times = {}
                            message = ""

                            spin_anim_grid = [
                                [random.choice(SPIN_SYMBOLS) for _ in range(GRID_COLS)]
                                for _ in range(GRID_ROWS)
                            ]
                            last_spin_anim_update = now

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                bet_minus_held = False
                bet_plus_held = False

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
                is_spinning = True
                spin_result_applied = False
                spin_start_time = now
                reel_stop_times = [
                    spin_start_time + SPIN_FIRST_STOP_MS + SPIN_REEL_STEP_MS * i
                    for i in range(GRID_COLS)
                ]
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
                        base_mult = evaluate_megaways_win(current_grid, paytable)

                    win_amount = base_mult * bet
                    balance += win_amount
                    last_win = win_amount

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

                    last_win_positions = find_winning_positions(
                        current_grid, paytable, wild_reels=current_wild_reels
                    )

                    if spin_win >= BIG_WIN_THRESHOLD_MULT * bet:
                        big_win_active = True
                        big_win_end_time = now + BIG_WIN_DURATION_MS

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

                    fs_spins_left -= 1
                    if extra_spins > 0:
                        fs_spins_left += extra_spins
                        retrigger_overlay_text = f"RETRIGGER! +{extra_spins} SPINS"
                        retrigger_overlay_until = now + RETRIGGER_OVERLAY_DURATION_MS

                    if fs_spins_left <= 0 or fs_total_mult >= MAX_WIN_MULT:
                        last_bonus_total = fs_total_win
                        message = f"FREE SPINS över! Total: {fs_total_win:.2f}"
                        bonus_state = "finished_waiting"
                        fs_next_spin_time = None

                        end_fs_transition_active = True
                        end_fs_transition_phase = "fade_in"
                        end_fs_transition_start = now
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
        elif game_mode == "base" and BG_BASE_IMG is not None:
            surface.blit(BG_BASE_IMG, (0, 0))
        else:
            surface.fill(BG_FS if game_mode == "fs" else BG_BASE)

        if game_mode == "fs":
            draw_text(
                surface,
                "MEGAWAYS – FREE SPINS",
                WINDOW_WIDTH // 2,
                50,
                FONT_HUGE,
                YELLOW,
                center=True,
            )
        else:
            draw_text(
                surface,
                "MEGAWAYS SLOT",
                WINDOW_WIDTH // 2,
                50,
                FONT_HUGE,
                CYAN,
                center=True,
            )

        draw_text(
            surface,
            f"Senaste vinst: {last_win:.2f}",
            WINDOW_WIDTH // 2,
            100,
            FONT_MEDIUM,
            WHITE,
            center=True,
        )

        if game_mode == "fs":
            left_x = 40
            base_y = 150
            if bonus_state in ("ready_to_start", "running", "finished_waiting"):
                draw_text(surface, "BONUSLÄGE!", left_x, base_y, FONT_MEDIUM, YELLOW)
                draw_text(surface, f"FS spins kvar: {fs_spins_left}", left_x, base_y + 40, FONT_MEDIUM, YELLOW)
                draw_text(surface, f"FS total vinst: {fs_total_win:.2f}", left_x, base_y + 80, FONT_MEDIUM, YELLOW)
                if current_wild_reels and bonus_state == "running":
                    reels_str = ", ".join(
                        f"{r+1}:x{current_wild_mults.get(r, 1)}" for r in current_wild_reels
                    )
                    draw_text(
                        surface,
                        f"Wild reels (hjul:mult): {reels_str}",
                        left_x,
                        base_y + 120,
                        FONT_SMALL,
                        ORANGE,
                    )

        now_ms = pygame.time.get_ticks()
        active_wild_reels = set(wild_drop_start_times.keys()) if (game_mode == "fs" and bonus_state == "running") else None

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

        draw_grid(
            surface,
            grid_to_draw,
            FONT_MEDIUM,
            win_positions=grid_win_positions,
            time_ms=now_ms,
            wild_reels=active_wild_reels,
            fs_mults=current_wild_mults if game_mode == "fs" and bonus_state == "running" else None,
            wild_drop_start_times=wild_drop_start_times,
        )

        draw_text(surface, f"Bet: {bet:.2f}", bet_label_pos[0], bet_label_pos[1], FONT_MEDIUM, WHITE, center=True)

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
        spin_disabled = (is_spinning or big_win_active
                         or (game_mode == "fs")
                         or bonus_state != "none"
                         or buy_confirm_visible)
        draw_round_button(
            surface,
            spin_center,
            spin_radius,
            spin_label,
            FONT_MEDIUM,
            ORANGE,
            hover=hover_spin and not spin_disabled,
            disabled=spin_disabled,
            img=SPIN_BUTTON_IMG,
            img_disabled=SPIN_BUTTON_IMG_DISABLED,
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

        draw_text(
            surface,
            f"Saldo: {balance:.2f}",
            30,
            WINDOW_HEIGHT - 40,
            FONT_MEDIUM,
            WHITE,
            center=False,
        )

        if message:
            draw_text(
                surface,
                message,
                WINDOW_WIDTH // 2,
                WINDOW_HEIGHT - 40,
                FONT_SMALL,
                GREY,
                center=True,
            )

        if bonus_state == "running" and now < retrigger_overlay_until:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            surface.blit(overlay, (0, 0))
            draw_text(surface, retrigger_overlay_text,
                      WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2,
                      FONT_LARGE, YELLOW, center=True)

        if buy_confirm_visible:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            surface.blit(overlay, (0, 0))

            pygame.draw.rect(surface, (30, 30, 60), confirm_rect, border_radius=16)
            pygame.draw.rect(surface, YELLOW, confirm_rect, width=3, border_radius=16)

            draw_text(surface, "KÖP BONUS?", confirm_rect.centerx, confirm_rect.top + 40,
                      FONT_LARGE, YELLOW, center=True)
            draw_text(
                surface,
                f"Vill du köpa free spins för {buy_confirm_cost:.2f} kr?",
                confirm_rect.centerx,
                confirm_rect.top + 100,
                FONT_MEDIUM,
                WHITE,
                center=True,
            )

            yes_hover = confirm_yes_rect.collidepoint(mouse_pos)
            no_hover = confirm_no_rect.collidepoint(mouse_pos)

            draw_button(surface, confirm_yes_rect, "JA", FONT_MEDIUM, GREEN,
                        hover=yes_hover, disabled=False)
            draw_button(surface, confirm_no_rect, "NEJ", FONT_MEDIUM, RED,
                        hover=no_hover, disabled=False)

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

                    title_surf = FONT_HUGE.render("FREE SPINS TRIGGADE!", True, YELLOW)
                    title_surf.set_alpha(alpha)
                    title_rect = title_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 20))
                    surface.blit(title_surf, title_rect)

                    sub_surf = FONT_MEDIUM.render("Klicka för att fortsätta", True, WHITE)
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
                    current_wild_reels = []
                    current_wild_mults = {}
                    wild_drop_start_times = {}
                    message = ""

            if alpha_end > 0:
                overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, alpha_end))
                surface.blit(overlay, (0, 0))

                title_surf = FONT_HUGE.render("BONUS OVER", True, CYAN)
                title_surf.set_alpha(alpha_end)
                title_rect = title_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 60))
                surface.blit(title_surf, title_rect)

                win_surf = FONT_LARGE.render(f"Du vann: {last_bonus_total:.2f}", True, WHITE)
                win_surf.set_alpha(alpha_end)
                win_rect = win_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
                surface.blit(win_surf, win_rect)

                hint_surf = FONT_MEDIUM.render("Klicka för att fortsätta", True, GREY)
                hint_surf.set_alpha(alpha_end)
                hint_rect = hint_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 60))
                surface.blit(hint_surf, hint_rect)

        if big_win_active:
            if now >= big_win_end_time:
                big_win_active = False
            else:
                overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 200))
                surface.blit(overlay, (0, 0))

                scale_phase = (now // 120) % 2
                big_font = pygame.font.SysFont("arial", 64 + 6 * scale_phase, bold=True)

                draw_text(surface, "BIG WIN!", WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 40,
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

    pygame.quit()
    #sys.exit()


if __name__ == "__main__":
    main()
