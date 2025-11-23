import pygame
import sys
import random
from math import sqrt

# Importera din matematiska modell
from slot_math import (
    SYMBOLS,
    spin_grid_same_probs,
    evaluate_megaways_win,
    paytable,
    symbol_probs,
    VISIBLE_ROWS,
    NUM_REELS,
)

pygame.init()

# ------------------- KONFIG / KONSTANTER -------------------

# Fönsterstorlek – lite större nu
WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 750

# Grid-layout
CELL_SIZE = 80
GRID_COLS = NUM_REELS
GRID_ROWS = VISIBLE_ROWS
GRID_WIDTH = GRID_COLS * CELL_SIZE
GRID_HEIGHT = GRID_ROWS * CELL_SIZE

GRID_X = (WINDOW_WIDTH - GRID_WIDTH) // 2
GRID_Y = 150

# Färger
BG_BASE = (8, 8, 20)
BG_FS = (15, 10, 35)
WHITE = (255, 255, 255)
GREY = (170, 170, 170)
DARK_GREY = (60, 60, 60)
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
FS_BUY_MULT = 150       # kostar 150x bet att köpa FS
MAX_WIN_MULT = 5000.0   # cap per bonus i bet-multiplar

# Fördelning för antal wild reels per FS
WILD_REEL_COUNTS = [0, 1, 2, 3, 4, 5]
WILD_REEL_COUNT_WEIGHTS = [60, 34, 5, 0.89, 0.1, 0.01]

# Multiplikator-fördelning per FS-spin
FS_MULTIPLIERS = [1, 2, 5, 8]
FS_MULT_WEIGHTS = [62, 30, 5, 3]

# Symbolvisning – byt "S" mot "Scatter"
DISPLAY_NAMES = {
    "S": "Scatter"
}


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


def draw_button(surface, rect, text, font, color, hover=False):
    c = tuple(min(255, int(ch * 1.2)) for ch in color) if hover else color
    pygame.draw.rect(surface, c, rect, border_radius=10)
    pygame.draw.rect(surface, WHITE, rect, width=2, border_radius=10)
    draw_text(surface, text, rect.centerx, rect.centery - 1, font, BLACK, center=True)


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
        # räkna per hjul
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

            # markera alla relevanta celler
            for col in range(consec_reels):
                if col in wild_reels:
                    # hela wildhjulet markeras
                    for row in range(num_rows):
                        win_positions.add((row, col))
                else:
                    for row in range(num_rows):
                        if grid[row][col] == sym:
                            win_positions.add((row, col))

    return win_positions


def draw_grid(surface, grid, font, win_positions=None, time_ms=0, wild_reels=None):
    """
    Ritar grid med symboler.
    - win_positions blinkar feint (blekt)
    - wild_reels (kolumner) markeras med extra kant/ljus bakgrund
    """
    if grid is None:
        return

    win_positions = win_positions or set()
    wild_reels = set(wild_reels or [])

    blink_phase = (time_ms // 200) % 2  # 0 eller 1

    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            x = GRID_X + c * CELL_SIZE
            y = GRID_Y + r * CELL_SIZE
            cell_rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

            # Bakgrundfärg
            if c in wild_reels:
                base_bg = (25, 40, 70)   # annan bakgrund för wild-hjul
            else:
                base_bg = DARK_GREY

            pygame.draw.rect(surface, base_bg, cell_rect, border_radius=8)

            # highlight på vinnande symboler – feint blinking
            if (r, c) in win_positions:
                if blink_phase == 0:
                    overlay_col = (255, 255, 255, 60)  # lite ljusare overlay
                else:
                    overlay_col = (255, 255, 255, 20)

                # eftersom pygame inte har alfa i draw.rect direkt,
                # fuskar vi med en semi-transparent surface
                overlay = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                overlay.fill(overlay_col)
                surface.blit(overlay, (x, y))

            # kant
            border_color = CYAN if c in wild_reels else BLACK
            pygame.draw.rect(surface, border_color, cell_rect, width=2, border_radius=8)

            # symbol
            sym = grid[r][c]
            text = symbol_display(sym)
            draw_text(surface, text, x + CELL_SIZE // 2, y + CELL_SIZE // 2, font, WHITE, center=True)


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

    # animation
    is_spinning = False
    spin_start_time = 0
    reel_stop_times = [0] * GRID_COLS
    spin_result_applied = False
    final_grid = None

    # free spins state
    game_mode = "base"          # "base" eller "fs"
    fs_spins_left = 0
    fs_total_win = 0.0
    fs_total_mult = 0.0
    current_wild_reels = []
    current_fs_mult = 1
    free_spins_active = False

    message = ""

    # knappar
    button_width = 160
    button_height = 60

    spin_button_rect = pygame.Rect(
        (WINDOW_WIDTH - button_width) // 2,
        GRID_Y + GRID_HEIGHT + 40,
        button_width,
        button_height,
    )

    buy_button_rect = pygame.Rect(
        spin_button_rect.right + 20,
        spin_button_rect.top,
        button_width,
        button_height,
    )

    bet_minus_rect = pygame.Rect(
        GRID_X - 220,
        spin_button_rect.top,
        60,
        50,
    )

    bet_plus_rect = pygame.Rect(
        GRID_X - 80,
        spin_button_rect.top,
        60,
        50,
    )

    # bet label-position
    bet_label_x = GRID_X - 200
    bet_label_y = spin_button_rect.top - 40

    # FS-info panel på vänstra sidan
    panel_x = 30
    panel_y = 130

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

                # Klick på bet minus/plus – endast i base-läge och när vi inte snurrar
                if not is_spinning and game_mode == "base":
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

                # Köp free spins
                if not is_spinning and game_mode == "base":
                    if buy_button_rect.collidepoint(mx, my):
                        cost = FS_BUY_MULT * bet
                        if balance >= cost:
                            balance -= cost
                            # initiera free spins-bonus
                            game_mode = "fs"
                            free_spins_active = True
                            fs_spins_left = N_FREE_SPINS
                            fs_total_win = 0.0
                            fs_total_mult = 0.0
                            current_wild_reels = []
                            current_fs_mult = 1
                            last_win_positions = set()
                            message = f"Köpte free spins för {cost:.2f}"
                        else:
                            message = "För lite saldo för att köpa free spins!"

                # Spin-knapp – olika logik i base resp. fs
                if spin_button_rect.collidepoint(mx, my) and not is_spinning:
                    if game_mode == "base":
                        # Base game spin
                        if balance < bet:
                            message = "För lite saldo för att spinna."
                        else:
                            balance -= bet
                            is_spinning = True
                            spin_result_applied = False
                            spin_start_time = now
                            reel_stop_times = [
                                spin_start_time + 300 + 200 * i for i in range(GRID_COLS)
                            ]
                            final_grid = spin_grid_same_probs()
                            last_win = 0.0
                            last_win_positions = set()
                            message = ""

                    elif game_mode == "fs":
                        # Free spins spin – kostar inget extra
                        if fs_spins_left > 0 and fs_total_mult < MAX_WIN_MULT:
                            is_spinning = True
                            spin_result_applied = False
                            spin_start_time = now
                            reel_stop_times = [
                                spin_start_time + 300 + 200 * i for i in range(GRID_COLS)
                            ]
                            final_grid = spin_grid_same_probs()

                            # bestäm wild reels + multiplikator för detta FS-spin
                            # (samma logik som i math-filen)
                            k = random.choices(
                                WILD_REEL_COUNTS, weights=WILD_REEL_COUNT_WEIGHTS, k=1
                            )[0]
                            if k <= 0:
                                current_wild_reels = []
                            else:
                                k = min(k, NUM_REELS)
                                current_wild_reels = random.sample(range(NUM_REELS), k)

                            current_fs_mult = random.choices(
                                FS_MULTIPLIERS, weights=FS_MULT_WEIGHTS, k=1
                            )[0]

                            last_win = 0.0
                            last_win_positions = set()
                            message = ""

            # (event loop slut)

        # ------------- SPINLOGIK -------------
        if is_spinning:
            # kolla om alla hjul har "stannat"
            if all(now >= t for t in reel_stop_times) and not spin_result_applied:
                # spin är färdig – applicera resultat
                is_spinning = False
                spin_result_applied = True
                current_grid = final_grid

                if game_mode == "base":
                    # base game win
                    base_mult = evaluate_megaways_win(current_grid, paytable)
                    win_amount = base_mult * bet
                    balance += win_amount
                    last_win = win_amount
                    last_win_positions = find_winning_positions(
                        current_grid, paytable
                    )

                    # kolla scatter-trigger
                    scatter_count = sum(
                        1
                        for row in current_grid
                        for sym in row
                        if sym == "S"
                    )

                    if scatter_count == 3:
                        # starta bonus
                        game_mode = "fs"
                        free_spins_active = True
                        fs_spins_left = N_FREE_SPINS
                        fs_total_win = 0.0
                        fs_total_mult = 0.0
                        current_wild_reels = []
                        current_fs_mult = 1
                        last_win_positions = set()
                        message = "FREE SPINS triggat!"

                    else:
                        if win_amount > 0:
                            message = f"Vinst: {win_amount:.2f}"
                        else:
                            message = "Ingen vinst."

                elif game_mode == "fs":
                    # free spins-win – använder current_wild_reels och current_fs_mult
                    base_mult = evaluate_megaways_win(
                        current_grid, paytable, wild_reels=current_wild_reels
                    )
                    spin_mult = base_mult * current_fs_mult

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

                    fs_spins_left -= 1

                    if fs_spins_left <= 0 or fs_total_mult >= MAX_WIN_MULT:
                        # avsluta bonus
                        message = f"FREE SPINS över! Total: {fs_total_win:.2f}"
                        game_mode = "base"
                        free_spins_active = False
                        current_wild_reels = []
                    else:
                        message = (
                            f"FS vinst: {spin_win:.2f} | "
                            f"FS total: {fs_total_win:.2f} | "
                            f"Spins kvar: {fs_spins_left}"
                        )

        # ------------- RITNING -------------
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

        # Info-panel vänster
        draw_text(screen, f"Saldo: {balance:.2f}", panel_x, panel_y, FONT_MEDIUM)
        draw_text(screen, f"Bet: {bet:.2f}", panel_x, panel_y + 40, FONT_MEDIUM)
        draw_text(screen, f"Senaste vinst: {last_win:.2f}", panel_x, panel_y + 80, FONT_MEDIUM)

        if game_mode == "fs":
            draw_text(screen, "BONUSLÄGE!", panel_x, panel_y + 130, FONT_MEDIUM, YELLOW)
            draw_text(screen, f"FS spins kvar: {fs_spins_left}", panel_x, panel_y + 170, FONT_MEDIUM, YELLOW)
            draw_text(screen, f"FS total vinst: {fs_total_win:.2f}", panel_x, panel_y + 210, FONT_MEDIUM, YELLOW)
            draw_text(screen, f"Ack. multipel: {fs_total_mult:.1f}x", panel_x, panel_y + 250, FONT_SMALL, CYAN)

            if current_wild_reels:
                reels_str = ", ".join(str(r + 1) for r in current_wild_reels)
                draw_text(
                    screen,
                    f"Wild reels: {reels_str} | Mult: x{current_fs_mult}",
                    panel_x,
                    panel_y + 290,
                    FONT_SMALL,
                    ORANGE,
                )

        # Grid
        if is_spinning:
            # rita snurr – slumpa symboler visuellt
            temp_grid = [
                [
                    random.choice([s for s in SYMBOLS if s != "S"])
                    for _ in range(GRID_COLS)
                ]
                for _ in range(GRID_ROWS)
            ]
            draw_grid(
                screen,
                temp_grid,
                FONT_MEDIUM,
                win_positions=set(),
                time_ms=now,
                wild_reels=current_wild_reels if game_mode == "fs" else None,
            )
        else:
            draw_grid(
                screen,
                current_grid,
                FONT_MEDIUM,
                win_positions=last_win_positions,
                time_ms=now,
                wild_reels=current_wild_reels if game_mode == "fs" else None,
            )

        # Bet-knappar
        hover_minus = bet_minus_rect.collidepoint(pygame.mouse.get_pos())
        hover_plus = bet_plus_rect.collidepoint(pygame.mouse.get_pos())
        draw_button(screen, bet_minus_rect, "-", FONT_LARGE, RED, hover_minus)
        draw_button(screen, bet_plus_rect, "+", FONT_LARGE, GREEN, hover_plus)
        draw_text(screen, "Bet-nivå", bet_label_x, bet_label_y, FONT_SMALL)

        # Spin-knapp
        hover_spin = spin_button_rect.collidepoint(pygame.mouse.get_pos())
        spin_label = "SPIN" if game_mode == "base" else "FS SPIN"
        draw_button(screen, spin_button_rect, spin_label, FONT_MEDIUM, ORANGE, hover_spin)

        # Buy FS-knapp (bara relevant visuellt i base)
        hover_buy = buy_button_rect.collidepoint(pygame.mouse.get_pos())
        buy_text = f"Köp FS ({FS_BUY_MULT}x)"
        draw_button(screen, buy_button_rect, buy_text, FONT_SMALL, YELLOW, hover_buy)

        # Meddelanderad
        if message:
            draw_text(screen, message, WINDOW_WIDTH // 2, WINDOW_HEIGHT - 40, FONT_SMALL, GREY, center=True)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
