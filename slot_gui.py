import pygame
import sys
import random

# Importera allt vi behöver från din matematikfil (byt namn om din fil heter något annat)
from slot_math import (
    VISIBLE_ROWS,
    NUM_REELS,
    SYMBOLS,
    spin_grid_same_probs,
    evaluate_megaways_win,
    run_free_spins,
    paytable,
)

# --- KONFIG --- #

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FPS = 60

# Grid-layout
CELL_SIZE = 100
CELL_MARGIN = 10

grid_width = NUM_REELS * CELL_SIZE + (NUM_REELS - 1) * CELL_MARGIN
grid_height = VISIBLE_ROWS * CELL_SIZE + (VISIBLE_ROWS - 1) * CELL_MARGIN

GRID_LEFT = (WINDOW_WIDTH - grid_width) // 2
GRID_TOP = 140

# Knappar
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 60

# Startvärden
START_BALANCE = 1000.0
START_BET = 1.0
MAX_WIN_MULT = 5000  # ska matcha max_win_mult i run_free_spins

# Spin-animation
BASE_SPIN_TIME = 600   # ms tiden första reelen snurrar
REEL_DELAY = 150       # ms extra delay per reel, så de stannar i turordning


# --- FÄRGER --- #
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (60, 60, 80)
DARK_BG = (15, 15, 35)
GREEN = (50, 200, 90)
RED = (210, 60, 60)
YELLOW = (240, 220, 60)
CYAN = (80, 200, 220)

SYMBOL_COLORS = {
    "A": (255, 80, 80),
    "B": (255, 140, 80),
    "C": (255, 210, 80),
    "D": (170, 255, 80),
    "E": (80, 255, 140),
    "F": (80, 255, 255),
    "G": (100, 180, 255),
    "H": (180, 100, 255),
    "I": (255, 80, 180),
    "S": (255, 255, 255),  # scatter
}


def draw_text(surface, text, x, y, font, color=WHITE, center=False):
    img = font.render(text, True, color)
    rect = img.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surface.blit(img, rect)


def draw_grid(surface, grid, font):
    """Ritar nuvarande grid (4x5) som färgrutor med bokstäver."""
    for r in range(VISIBLE_ROWS):
        for c in range(NUM_REELS):
            x = GRID_LEFT + c * (CELL_SIZE + CELL_MARGIN)
            y = GRID_TOP + r * (CELL_SIZE + CELL_MARGIN)
            sym = grid[r][c]

            color = SYMBOL_COLORS.get(sym, GRAY)
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

            # bakgrund till cell
            pygame.draw.rect(surface, color, rect, border_radius=12)
            # kant
            pygame.draw.rect(surface, BLACK, rect, width=2, border_radius=12)

            # bokstav
            text_color = BLACK if sym != "S" else BLACK
            draw_text(surface, sym, rect.centerx, rect.centery, font, text_color, center=True)

            # extra markering för scatter
            if sym == "S":
                pygame.draw.rect(surface, YELLOW, rect, width=3, border_radius=12)


def make_empty_grid(symbol=" "):
    """Skapar en tom grid (används inte nödvändigtvis nu, men bra hjälpfunktion)."""
    return [[symbol for _ in range(NUM_REELS)] for _ in range(VISIBLE_ROWS)]


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Megaways Slot – GUI")

    clock = pygame.time.Clock()

    font_small = pygame.font.SysFont("arial", 18)
    font_medium = pygame.font.SysFont("arial", 24, bold=True)
    font_big = pygame.font.SysFont("arial", 36, bold=True)
    font_huge = pygame.font.SysFont("arial", 48, bold=True)

    balance = START_BALANCE
    bet = START_BET
    last_win = 0.0
    message = ""
    free_spins_last_trigger = False

    # init grid
    current_grid = spin_grid_same_probs()

    # SPIN-knapp
    spin_button_rect = pygame.Rect(
        WINDOW_WIDTH // 2 - BUTTON_WIDTH // 2,
        WINDOW_HEIGHT - BUTTON_HEIGHT - 40,
        BUTTON_WIDTH,
        BUTTON_HEIGHT,
    )

    # Spin-animation state
    is_spinning = False
    spin_start_time = 0
    reel_stop_times = []
    final_grid = current_grid
    spin_result_applied = False

    running = True
    while running:
        dt = clock.tick(FPS)
        now = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                if spin_button_rect.collidepoint(mouse_pos) and not is_spinning:
                    # Klick på SPIN
                    if balance >= bet:
                        # Ta betalt direkt
                        balance -= bet
                        last_win = 0.0
                        message = ""
                        free_spins_last_trigger = False

                        # Förbereda slutresultat (riktig grid)
                        final_grid = spin_grid_same_probs()

                        # Starta spin-animation
                        spin_start_time = now
                        reel_stop_times = [
                            spin_start_time + BASE_SPIN_TIME + i * REEL_DELAY
                            for i in range(NUM_REELS)
                        ]
                        is_spinning = True
                        spin_result_applied = False
                    else:
                        message = "Inte tillräckligt saldo!"

        # --- LOGIK NÄR SPINNING PÅGÅR --- #
        if is_spinning:
            # Kolla om alla hjul har stannat
            if not spin_result_applied and all(now >= t for t in reel_stop_times):
                # Avsluta spinning
                is_spinning = False
                spin_result_applied = True
                current_grid = final_grid

                # Räkna base win
                win_mult = evaluate_megaways_win(current_grid, paytable)
                base_win = win_mult * bet
                balance += base_win
                last_win = base_win
                message = f"Base win: {win_mult:.2f}x"

                # Kolla om free spins triggas
                scatter_count = sum(1 for row in current_grid for sym in row if sym == "S")
                if scatter_count == 3:
                    fs_win = run_free_spins(
                        num_free_spins=10,
                        bet=bet,
                        verbose=False,
                        max_win_mult=MAX_WIN_MULT,
                    )
                    balance += fs_win
                    last_win += fs_win
                    free_spins_last_trigger = True
                    message = f"FREE SPINS! Total win: {last_win:.2f}"

        # --- RITA --- #
        screen.fill(DARK_BG)

        # Titel
        draw_text(screen, "Megaways Slot", WINDOW_WIDTH // 2, 40, font_huge, CYAN, center=True)

        # Info-panel vänster
        panel_x = 50
        panel_y = 120
        draw_text(screen, f"Saldo: {balance:.2f}", panel_x, panel_y, font_medium, WHITE)
        draw_text(screen, f"Bet:   {bet:.2f}", panel_x, panel_y + 40, font_medium, WHITE)
        draw_text(screen, f"Senaste vinst: {last_win:.2f}", panel_x, panel_y + 80, font_medium, YELLOW)

        # meddelande
        if message:
            draw_text(screen, message, panel_x, panel_y + 130, font_small, WHITE)

        if free_spins_last_trigger:
            draw_text(screen, "BONUS!", panel_x, panel_y + 160, font_big, YELLOW)

        # rita grid
        if is_spinning:
            # Rita “falsk” snurrande grid: varje reel som inte stannat visar random symboler
            temp_grid = []
            for r in range(VISIBLE_ROWS):
                row_syms = []
                for c in range(NUM_REELS):
                    if now < reel_stop_times[c]:
                        # fortfarande snurr: slumpa symbol
                        row_syms.append(random.choice(SYMBOLS))
                    else:
                        # reel stoppad: visa slutgiltig symbol
                        row_syms.append(final_grid[r][c])
                temp_grid.append(row_syms)
            draw_grid(screen, temp_grid, font_medium)
        else:
            draw_grid(screen, current_grid, font_medium)

        # SPIN-knapp (disable-look när snurrar)
        if is_spinning:
            btn_color = GRAY
            text_color = (180, 180, 180)
        else:
            btn_color = GREEN
            text_color = BLACK

        pygame.draw.rect(screen, btn_color, spin_button_rect, border_radius=15)
        pygame.draw.rect(screen, BLACK, spin_button_rect, width=2, border_radius=15)
        draw_text(screen, "SPIN", spin_button_rect.centerx, spin_button_rect.centery,
                  font_medium, text_color, center=True)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
