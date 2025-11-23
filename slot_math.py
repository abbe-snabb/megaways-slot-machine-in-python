from math import sqrt, comb
import random

VISIBLE_ROWS = 4
NUM_REELS = 5

# Nu med scatter S
SYMBOLS = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "S"]

# Ursprungliga A–I (summerar till 1.0), skalar ner för att ge plats åt S
base_probs = {
    # godly 8%
    "A": 0.01,
    "B": 0.02,
    "C": 0.05,
    # good 22 %
    "D": 0.10,
    "E": 0.12,
    # bad 34 %
    "F": 0.17,
    "G": 0.17,
    # very bad 36%
    "H": 0.18,
    "I": 0.18,
}

pS = 0.013
scale = 1.0 - pS        # så att A–I skalar ned och totalen blir 1.0

symbol_probs = {s: p * scale for s, p in base_probs.items()}
symbol_probs["S"] = pS

paytable = {
    ("A", 3): 5,
    ("A", 4): 25,
    ("A", 5): 50,

    ("B", 3): 2.5,
    ("B", 4): 7.5,
    ("B", 5): 10,

    ("C", 3): 1,
    ("C", 4): 3.5,
    ("C", 5): 5,

    ("D", 3): 0.4,
    ("D", 4): 0.6,
    ("D", 5): 1.5,

    ("E", 3): 0.4,
    ("E", 4): 0.6,
    ("E", 5): 1.5,

    ("F", 3): 0.25,
    ("F", 4): 0.4,
    ("F", 5): 1,

    ("G", 3): 0.25,
    ("G", 4): 0.4,
    ("G", 5): 1,

    ("H", 4): 0.1,
    ("H", 5): 0.4,

    ("I", 4): 0.1,
    ("I", 5): 0.4,
}

# vikter till random.choices
weights = [symbol_probs[s] for s in SYMBOLS]


def spin_grid_same_probs():
    """
    Spin:
    - använder SYMBOLS + symbol_probs
    - ser till att antal scatters 'S' aldrig blir > 3
    """
    while True:
        grid = []
        for _ in range(VISIBLE_ROWS):
            row_syms = random.choices(SYMBOLS, weights=weights, k=NUM_REELS)
            grid.append(row_syms)

        # räkna scatters
        scatter_count = sum(sym == "S" for row in grid for sym in row)

        # kravet: MER än 3 ska vara omöjligt -> re-spinna om >3
        if scatter_count <= 3:
            return grid


def print_grid(grid):
    for row in grid:
        print(" ".join(row))
    print()


def print_grid_with_wilds(grid, wild_reels):
    """
    Visuell hjälp i free spins:
    - alla wild-reels markeras som 'W' istället för sin riktiga symbol
    """
    wild_reels = set(wild_reels or [])
    for row in range(len(grid)):
        row_syms = []
        for col in range(len(grid[0])):
            if col in wild_reels:
                row_syms.append("W")
            else:
                row_syms.append(grid[row][col])
        print(" ".join(row_syms))
    print()


def evaluate_megaways_win(grid, paytable, wild_reels=None):
    """
    Beräknar line-vinst (i bet-multiplar).
    wild_reels:
        - None eller tom => ingen wild reel (base game)
        - iterable med kolumner (0–4) som är wild reels
          (hela hjul = wild, räknas som 4 träffar av valfri symbol)
    """
    num_rows = len(grid)
    num_reels = len(grid[0])
    total_win = 0.0

    if wild_reels is None:
        wild_reels = set()
    else:
        wild_reels = set(wild_reels)

    paying_symbols = set(sym for (sym, _) in paytable.keys())

    for sym in paying_symbols:
        counts_per_reel = []
        for col in range(num_reels):
            if col in wild_reels:
                # wild reel: kan alltid representera symbolen, 4 positioner
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
            if key in paytable:
                ways = 1
                for c in counts_per_reel[:consec_reels]:
                    ways *= c
                total_win += ways * paytable[key]

    return total_win


def theoretical_rtp(symbol_probs, paytable, visible_rows=VISIBLE_ROWS):
    """
    OBS: bara base game (A–I), räknar inte värdet av free spins + wilds.
    """
    rtp = 0.0
    for s, p in symbol_probs.items():
        if s == "S":
            continue  # scatter är ingen line-vinst

        alpha = visible_rows * p          # α_s = 4 * p_s
        q = (1 - p) ** visible_rows       # q_s = (1 - p_s)^4

        # 3-of-a-kind
        a3 = paytable.get((s, 3), 0.0)
        if a3 != 0:
            rtp += a3 * (alpha ** 3) * q

        # 4-of-a-kind
        a4 = paytable.get((s, 4), 0.0)
        if a4 != 0:
            rtp += a4 * (alpha ** 4) * q

        # 5-of-a-kind
        a5 = paytable.get((s, 5), 0.0)
        if a5 != 0:
            rtp += a5 * (alpha ** 5)

    return rtp


# --- FREE SPINS MED FLERA WILD REELS --- #

# fördelning för antal wild reels per free spin
WILD_REEL_COUNTS = [0, 1, 2, 3, 4, 5]
WILD_REEL_COUNT_WEIGHTS = [64, 30, 5, 0.89, 0.1, 0.01]  # procent-vikter

# multiplikator-fördelning per free spin
FS_MULTIPLIERS = [1, 2, 5, 8]
FS_MULT_WEIGHTS = [66, 28, 4, 2]


def sample_wild_reels():
    """
    Slumpa antal wild reels enligt given distribution
    och välj så många distinkta hjul bland de 5.
    """
    k = random.choices(WILD_REEL_COUNTS, weights=WILD_REEL_COUNT_WEIGHTS, k=1)[0]
    if k <= 0:
        return []
    k = min(k, NUM_REELS)
    # välj k distinkta reelser
    return random.sample(range(NUM_REELS), k)


def run_free_spins(num_free_spins, bet, verbose=True, max_win_mult=None):
    """
    Kör en free-spins-runda:
    - startar med num_free_spins
    - 2 scatters i bonus => +1 extra spin
    - 3 scatters i bonus => +3 extra spins
    - varje spin: slumpa wild reels + multiplikator
    - beräkna line win med wild reels och multiplikator
    - om max_win_mult sätts (t.ex. 5000), capsas vinstmultipeln där
      och bonusen avslutas direkt.
    """
    total_win_mult = 0.0     # vinst i bet-multiplar
    spins_played = 0
    total_spins = num_free_spins

    while spins_played < total_spins:
        spins_played += 1

        # välj wild reels
        wild_reels = sample_wild_reels()

        # välj multiplikator per free spin
        mult = random.choices(FS_MULTIPLIERS, weights=FS_MULT_WEIGHTS, k=1)[0]

        # i bonusen får S förekomma igen (för retriggers)
        grid = spin_grid_same_probs()

        base_mult = evaluate_megaways_win(grid, paytable, wild_reels=wild_reels)
        spin_mult = base_mult * mult
        total_win_mult += spin_mult

        # räkna scatters i free spin → extra spins
        scatter_count = sum(sym == "S" for row in grid for sym in row)
        extra_spins = 0
        if scatter_count == 2:
            extra_spins = 1
        elif scatter_count == 3:
            extra_spins = 3

        if extra_spins > 0:
            total_spins += extra_spins
            if verbose:
                print(f"--> {scatter_count} scatters i bonus! +{extra_spins} extra free spin(s).")
                print(f"    Nya totalt antal free spins: {total_spins}")

        if verbose:
            print(f"\nFree Spin {spins_played}/{total_spins} | Wild reels: {[r+1 for r in wild_reels]} | Mult: {mult}x")
            print_grid_with_wilds(grid, wild_reels)
            print(f"Free spin vinstmultipel (före mult): {base_mult:.2f}x")
            print(f"Free spin vinstmultipel (efter mult): {spin_mult:.2f}x")
            print(f"Ackumulerad vinstmultipel i FS:      {total_win_mult:.2f}x")

        # kolla cap
        if max_win_mult is not None and total_win_mult >= max_win_mult:
            total_win_mult = max_win_mult
            if verbose:
                print(f"\n*** MAX WIN REACHED: {max_win_mult}x! Bonus avslutas. ***")
            break

    total_win_amount = total_win_mult * bet

    if verbose:
        print(f"\nTotal vinst från free spins: {total_win_amount:.2f}")

    return total_win_amount


def estimate_fs_round_ev(num_free_spins=10, n_rounds=200_000, bet=1.0, max_win_mult=None):
    total = 0.0
    for _ in range(n_rounds):
        total += run_free_spins(num_free_spins=num_free_spins,
                                bet=bet,
                                verbose=False,
                                max_win_mult=max_win_mult)
    return total / n_rounds


def simulate_rtp(paytable, n_spins=1_000_000, bet=1.0):
    """
    Simulerar RTP inkl. free spins:
    - base game + triggers (3 scatters) + free spins med (0–5) wild reels
    """
    total_win = 0.0
    hit_count = 0
    fs_triggers = 0

    for _ in range(n_spins):
        grid = spin_grid_same_probs()
        base_mult = evaluate_megaways_win(grid, paytable)
        win = base_mult * bet
        total_win += win
        if win > 0:
            hit_count += 1

        # räkna scatters
        scatter_count = sum(sym == "S" for row in grid for sym in row)
        if scatter_count == 3:
            fs_triggers += 1
            fs_win = run_free_spins(num_free_spins=10, bet=bet, verbose=False, max_win_mult=5000)
            total_win += fs_win

    avg_win = total_win / (n_spins * bet)  # RTP per satsad 1
    hit_freq = hit_count / n_spins
    trig_freq = fs_triggers / n_spins
    return avg_win, hit_freq, trig_freq


def play_game():
    print("Välkommen till din Megaways-slot!")
    print(f"Teoretisk RTP (base game utan free spins): {theoretical_rtp(symbol_probs, paytable):.4f}")
    print("Symboler:", ", ".join(SYMBOLS))
    print("S = scatter (3 st triggar 10 free spins).")
    print("Tryck Enter för att spinna, 'q' för att avsluta, 'b' för att ändra insats.\n")

    # Startsaldo och standardinsats
    while True:
        try:
            balance = float(input("Ange startsaldo (t.ex. 100): "))
            if balance <= 0:
                print("Saldo måste vara > 0.")
                continue
            break
        except ValueError:
            print("Skriv ett tal, t.ex. 100.")

    while True:
        try:
            bet = float(input("Ange insats per spin (t.ex. 1): "))
            if bet <= 0:
                print("Insats måste vara > 0.")
                continue
            break
        except ValueError:
            print("Skriv ett tal, t.ex. 1.")

    total_spins = 0
    total_bet = 0.0
    total_win = 0.0

    while True:
        print(f"\nSaldo: {balance:.2f} | Insats: {bet:.2f}")
        cmd = input("[Enter]=spinn, 'b'=ändra insats, 'q'=avsluta: ").strip().lower()

        if cmd == "q":
            break
        elif cmd == "b":
            # ändra insats
            try:
                new_bet = float(input("Ny insats: "))
                if new_bet > 0:
                    bet = new_bet
                else:
                    print("Insats måste vara > 0.")
            except ValueError:
                print("Ogiltig insats.")
            continue

        # kolla om spelaren har råd
        if balance < bet:
            print("Du har inte råd med ett spin. Avslutar spelet.")
            break

        # ta betalt för spinnet
        balance -= bet
        total_bet += bet
        total_spins += 1

        # gör ett base-spinn
        grid = spin_grid_same_probs()
        print("\nGrid:")
        print_grid(grid)

        # base game-vinst (line wins)
        win_mult = evaluate_megaways_win(grid, paytable)
        win_amount = win_mult * bet
        balance += win_amount
        total_win += win_amount

        print(f"Base vinstmultipel: {win_mult:.2f}x")
        print(f"Base vinst i pengar: {win_amount:.2f}")
        print(f"Nytt saldo:         {balance:.2f}")

        # kolla scatters för free spins
        scatter_count = sum(sym == "S" for row in grid for sym in row)
        if scatter_count == 3:
            print("\n*** FREE SPINS TRIGGADE! 10 FREE SPINS! ***")
            fs_win = run_free_spins(num_free_spins=10, bet=bet, verbose=True, max_win_mult=5000)
            balance += fs_win
            total_win += fs_win
            print(f"Saldo efter free spins: {balance:.2f}")

        if balance <= 0:
            print("Saldo är 0. Spelet är slut.")
            break

    # sammanfattning
    print("\n--- Sammanfattning ---")
    print(f"Totalt antal spins (base): {total_spins}")
    print(f"Totalt satsat:             {total_bet:.2f}")
    print(f"Totalt vunnit:             {total_win:.2f}")
    if total_bet > 0:
        empirical_rtp = total_win / total_bet
        print(f"Empirisk RTP (inkl free spins): {empirical_rtp:.4f}")
    print("Tack för att du spelade!")


def theoretical_total_rtp_with_fs(symbol_probs, paytable, visible_rows=VISIBLE_ROWS):
    """
    Teoretisk total-RTP:
    - base game (exakt analytiskt)
    - free spins (EV uppskattad via simulering av free-spins-rundor)
    """
    # 1) Base-RTP analytiskt
    rtp_base = theoretical_rtp(symbol_probs, paytable, visible_rows=visible_rows)

    # 2) Trigger-sannolikhet q = P(exakt 3 S) (Binomial(20,pS)) – approx pga truncation
    pS_local = symbol_probs.get("S", 0.0)
    cells = visible_rows * NUM_REELS  # 4 * 5 = 20
    q_trig = comb(cells, 3) * (pS_local**3) * ((1 - pS_local)**(cells - 3))

    # 3) EV per free-spins-runda (10 FS) via riktad simulering
    N_FS = 10
    EV_fs_round = estimate_fs_round_ev(num_free_spins=N_FS,
                                       n_rounds=20_000,
                                       bet=1.0,
                                       max_win_mult=5000)

    # 4) RTP-bidrag från free spins per base spin
    rtp_fs = q_trig * EV_fs_round  # bet=1 => denna är i RTP-enheter

    rtp_total = rtp_base + rtp_fs
    return rtp_total, rtp_base, rtp_fs, q_trig, EV_fs_round


def theoretical_variance(symbol_probs, paytable, visible_rows=VISIBLE_ROWS):
    """
    OBS: bara base game (utan scatters / free spins).
    """
    EX = theoretical_rtp(symbol_probs, paytable)  # E[X]

    EX2 = 0.0
    for s, p in symbol_probs.items():
        if s == "S":
            continue

        m = visible_rows * p                         # E[N]
        v = 4 * p * (1 - p) + (4 * p)**2             # E[N^2]
        q = (1 - p)**visible_rows                    # P(no symbol on a reel)

        # 3-of-a-kind
        a3 = paytable.get((s, 3), 0.0)
        if a3 != 0:
            EX2 += (a3**2) * (v**3) * q

        # 4-of-a-kind
        a4 = paytable.get((s, 4), 0.0)
        if a4 != 0:
            EX2 += (a4**2) * (v**4) * q

        # 5-of-a-kind
        a5 = paytable.get((s, 5), 0.0)
        if a5 != 0:
            EX2 += (a5**2) * (v**5)

    variance = EX2 - (EX ** 2)
    sigma = sqrt(variance)
    return variance, sigma


def simulate_variance(paytable, n_spins=200_000, bet=1.0):
    """
    Simulerar varians för totalvinst per base spin inkl free spins.
    """
    wins = []
    for _ in range(n_spins):
        grid = spin_grid_same_probs()
        base_mult = evaluate_megaways_win(grid, paytable)
        win = base_mult * bet

        scatter_count = sum(sym == "S" for row in grid for sym in row)
        if scatter_count == 3:
            win += run_free_spins(num_free_spins=10, bet=bet, verbose=False, max_win_mult=5000)

        wins.append(win)

    EX = sum(wins) / len(wins)
    EX2 = sum(w*w for w in wins) / len(wins)
    variance = EX2 - EX**2
    sigma = sqrt(variance)
    return variance, sigma


if __name__ == "__main__":
    mode = input("Skriv 'play' för att spela, 'sim' för att köra RTP-simulering: ").strip().lower()
    if mode == "sim":
        rtp_base = theoretical_rtp(symbol_probs, paytable)
        print(f"Teoretisk RTP (endast base game): {rtp_base:.6f}")

        rtp_total, rtp_base2, rtp_fs, q_trig, EV_fs_round = theoretical_total_rtp_with_fs(symbol_probs, paytable)
        print(f"Teoretisk total-RTP (inkl free spins, FS EV simulerad): {rtp_total:.6f}")
        print(f"  - Trigger-sannolikhet q:         {q_trig:.6f}")
        print(f"  - EV per FS-runda (10 FS):       {EV_fs_round:.6f}")
        print(f"  - RTP-bidrag från free spins:    {rtp_fs:.6f}")

        avg_win, hit_freq, trig_freq = simulate_rtp(paytable, n_spins=100_000, bet=1.0)
        print(f"\nSimulerad total-RTP (fullt spel):  {avg_win:.6f}")
        print(f"Simulerad hit-frekvens (base):     {hit_freq:.6f}")
        print(f"Simulerad FS-trigger-frekvens:     {trig_freq:.6f}")

        var_sim, sigma_sim = simulate_variance(paytable, n_spins=100_000, bet=1.0)
        print(f"\nSimulerad Varians (inkl FS):       {var_sim:.6f}")
        print(f"Simulerad Sigma (inkl FS):         {sigma_sim:.6f}")

    else:
        play_game()
