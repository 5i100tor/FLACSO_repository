import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt


# --------------------------
# Strategy Classes
# --------------------------

class AlwaysCooperate:
    def move(self, own_history, opp_history):
        return "C"


class AlwaysDefect:
    def move(self, own_history, opp_history):
        return "D"


class TitForTat:
    def move(self, own_history, opp_history):
        if len(opp_history) == 0:
            return "C"
        return opp_history[-1]


STRATEGIES = {
    "Always Cooperate": AlwaysCooperate,
    "Always Defect": AlwaysDefect,
    "Tit For Tat": TitForTat
}


# --------------------------
# Payoff Matrix
# --------------------------

def get_payoff_matrix():
    return {
        ("C", "C"): (int(cc_p1.get()), int(cc_p2.get())),
        ("C", "D"): (int(cd_p1.get()), int(cd_p2.get())),
        ("D", "C"): (int(dc_p1.get()), int(dc_p2.get())),
        ("D", "D"): (int(dd_p1.get()), int(dd_p2.get()))
    }


# --------------------------
# Match Simulation
# --------------------------

def play_match(strategy1_name, strategy2_name, payoff_matrix, rounds=10): #change here 
    s1 = STRATEGIES[strategy1_name]()
    s2 = STRATEGIES[strategy2_name]()

    h1 = []
    h2 = []

    score1 = 0
    score2 = 0

    round_data = []

    for r in range(1, rounds + 1):
        m1 = s1.move(h1, h2)
        m2 = s2.move(h2, h1)

        p1, p2 = payoff_matrix[(m1, m2)]

        score1 += p1
        score2 += p2

        h1.append(m1)
        h2.append(m2)

        round_data.append((r, m1, m2, p1, p2))

    return score1, score2, round_data


# --------------------------
# Strategy Payoff Matrix
# --------------------------

def build_strategy_payoff_matrix(payoff_matrix, rounds=10):
    names = list(STRATEGIES.keys())
    matrix = {}

    for s1 in names:
        for s2 in names:
            score1, score2, _ = play_match(
                s1, s2, payoff_matrix, rounds
            )
            matrix[(s1, s2)] = (score1, score2)

    return matrix


# --------------------------
# Nash Equilibria
# --------------------------

def find_nash_equilibria(strategy_matrix):
    names = list(STRATEGIES.keys())
    equilibria = []

    for s1 in names:
        for s2 in names:
            p1_payoff = strategy_matrix[(s1, s2)][0]
            p2_payoff = strategy_matrix[(s1, s2)][1]

            p1_best = True
            for alt1 in names:
                if strategy_matrix[(alt1, s2)][0] > p1_payoff:
                    p1_best = False

            p2_best = True
            for alt2 in names:
                if strategy_matrix[(s1, alt2)][1] > p2_payoff:
                    p2_best = False

            if p1_best and p2_best:
                equilibria.append((s1, s2))

    return equilibria


# --------------------------
# ESS
# --------------------------

def find_ess(strategy_matrix):
    names = list(STRATEGIES.keys())
    ess_list = []

    for resident in names:
        stable = True

        for mutant in names:
            if resident == mutant:
                continue

            E_res_res = strategy_matrix[(resident, resident)][0]
            E_mut_res = strategy_matrix[(mutant, resident)][0]

            if E_mut_res > E_res_res:
                stable = False

            elif E_mut_res == E_res_res:
                E_res_mut = strategy_matrix[(resident, mutant)][0]
                E_mut_mut = strategy_matrix[(mutant, mutant)][0]

                if E_mut_mut >= E_res_mut:
                    stable = False

        if stable:
            ess_list.append(resident)

    return ess_list


# --------------------------
# Replicator Dynamics
# --------------------------

def run_replicator_dynamics(strategy_matrix, steps=50):
    names = list(STRATEGIES.keys())
    n = len(names)

    shares = [1 / n for _ in range(n)]
    history = [shares.copy()]

    payoff_only_p1 = [
        [strategy_matrix[(i, j)][0] for j in names]
        for i in names
    ]

    for _ in range(steps):
        fitness = []

        for i in range(n):
            f_i = sum(
                payoff_only_p1[i][j] * shares[j]
                for j in range(n)
            )
            fitness.append(f_i)

        avg_fitness = sum(
            shares[i] * fitness[i]
            for i in range(n)
        )

        if avg_fitness == 0:
            break

        new_shares = [
            shares[i] * fitness[i] / avg_fitness
            for i in range(n)
        ]

        shares = new_shares
        history.append(shares.copy())

    return history


def plot_replicator_dynamics(history):
    names = list(STRATEGIES.keys())

    for i, name in enumerate(names):
        plt.plot(
            [row[i] for row in history],
            label=name
        )

    plt.title("Replicator Dynamics")
    plt.xlabel("Time Step")
    plt.ylabel("Population Share")
    plt.ylim(0, 1)
    plt.legend()
    plt.show()


# --------------------------
# Main Run Function
# --------------------------

def run_tournament():
    output.delete("1.0", tk.END)

    payoff_matrix = get_payoff_matrix()

    p1_name = player1_var.get()
    p2_name = player2_var.get()

    p1_score, p2_score, round_data = play_match(
        p1_name,
        p2_name,
        payoff_matrix,
        rounds=10
    )

    strategy_matrix = build_strategy_payoff_matrix(
        payoff_matrix,
        rounds=10
    )

    nash = find_nash_equilibria(strategy_matrix)
    ess = find_ess(strategy_matrix)
    replicator_history = run_replicator_dynamics(strategy_matrix)

    output.insert(tk.END, "============================\n")
    output.insert(tk.END, "Selected Match\n")
    output.insert(tk.END, "============================\n\n")

    output.insert(tk.END, f"Player 1: {p1_name}\n")
    output.insert(tk.END, f"Player 2: {p2_name}\n\n")

    for r, m1, m2, p1, p2 in round_data:
        output.insert(
            tk.END,
            f"Round {r}: P1={m1}  P2={m2}  Payoff=({p1},{p2})\n"
        )

    output.insert(tk.END, "\n")
    output.insert(tk.END, f"Player 1 Total: {p1_score}\n")
    output.insert(tk.END, f"Player 2 Total: {p2_score}\n\n")

    if p1_score > p2_score:
        output.insert(tk.END, "Winner: Player 1\n\n")
    elif p2_score > p1_score:
        output.insert(tk.END, "Winner: Player 2\n\n")
    else:
        output.insert(tk.END, "Result: Tie\n\n")

    output.insert(tk.END, "============================\n")
    output.insert(tk.END, "Strategy-vs-Strategy Matrix\n")
    output.insert(tk.END, "============================\n\n")

    for s1 in STRATEGIES.keys():
        for s2 in STRATEGIES.keys():
            payoff = strategy_matrix[(s1, s2)]
            output.insert(
                tk.END,
                f"{s1} vs {s2}: {payoff}\n"
            )
        output.insert(tk.END, "\n")

    output.insert(tk.END, "============================\n")
    output.insert(tk.END, "Nash Equilibria\n")
    output.insert(tk.END, "============================\n\n")

    if nash:
        for eq in nash:
            output.insert(tk.END, f"{eq}\n")
    else:
        output.insert(tk.END, "No pure-strategy Nash equilibrium found.\n")

    output.insert(tk.END, "\n")

    output.insert(tk.END, "============================\n")
    output.insert(tk.END, "Evolutionarily Stable Strategies\n")
    output.insert(tk.END, "============================\n\n")

    if ess:
        for e in ess:
            output.insert(tk.END, f"{e}\n")
    else:
        output.insert(tk.END, "No ESS found.\n")

    output.insert(tk.END, "\n")

    output.insert(tk.END, "============================\n")
    output.insert(tk.END, "Final Replicator Shares\n")
    output.insert(tk.END, "============================\n\n")

    final_shares = replicator_history[-1]

    for name, share in zip(STRATEGIES.keys(), final_shares):
        output.insert(
            tk.END,
            f"{name}: {share:.4f}\n"
        )

    plot_replicator_dynamics(replicator_history)


# --------------------------
# Reset Function
# --------------------------

def reset_game():
    player1_box.current(0)
    player2_box.current(1)

    defaults = {
        cc_p1: "3",
        cc_p2: "3",
        cd_p1: "0",
        cd_p2: "5",
        dc_p1: "5",
        dc_p2: "0",
        dd_p1: "1",
        dd_p2: "1"
    }

    for box, value in defaults.items():
        box.delete(0, tk.END)
        box.insert(0, value)

    output.delete("1.0", tk.END)


# --------------------------
# GUI
# --------------------------

root = tk.Tk()
root.title("Axelrod Evolutionary Game Theory Lab")
root.geometry("1000x750")

main = ttk.Frame(root, padding=10)
main.pack(fill="both", expand=True)


# --------------------------
# Strategy Selection
# --------------------------

ttk.Label(main, text="Player 1 Strategy").grid(
    row=0, column=0, sticky="w"
)

player1_var = tk.StringVar()

player1_box = ttk.Combobox(
    main,
    textvariable=player1_var,
    values=list(STRATEGIES.keys()),
    state="readonly",
    width=25
)

player1_box.grid(row=0, column=1)
player1_box.current(0)

ttk.Label(main, text="Player 2 Strategy").grid(
    row=1, column=0, sticky="w"
)

player2_var = tk.StringVar()

player2_box = ttk.Combobox(
    main,
    textvariable=player2_var,
    values=list(STRATEGIES.keys()),
    state="readonly",
    width=25
)

player2_box.grid(row=1, column=1)
player2_box.current(1)


# --------------------------
# Payoff Matrix
# --------------------------

ttk.Label(
    main,
    text="Editable Payoff Matrix (P1, P2)"
).grid(
    row=3,
    column=0,
    columnspan=6,
    pady=15
)

headers = ["Outcome", "P1", "P2"]

for i, h in enumerate(headers):
    ttk.Label(main, text=h).grid(row=4, column=i)

ttk.Label(main, text="C,C").grid(row=5, column=0)

cc_p1 = ttk.Entry(main, width=8)
cc_p1.insert(0, "3")
cc_p1.grid(row=5, column=1)

cc_p2 = ttk.Entry(main, width=8)
cc_p2.insert(0, "3")
cc_p2.grid(row=5, column=2)

ttk.Label(main, text="C,D").grid(row=6, column=0)

cd_p1 = ttk.Entry(main, width=8)
cd_p1.insert(0, "0")
cd_p1.grid(row=6, column=1)

cd_p2 = ttk.Entry(main, width=8)
cd_p2.insert(0, "5")
cd_p2.grid(row=6, column=2)

ttk.Label(main, text="D,C").grid(row=7, column=0)

dc_p1 = ttk.Entry(main, width=8)
dc_p1.insert(0, "5")
dc_p1.grid(row=7, column=1)

dc_p2 = ttk.Entry(main, width=8)
dc_p2.insert(0, "0")
dc_p2.grid(row=7, column=2)

ttk.Label(main, text="D,D").grid(row=8, column=0)

dd_p1 = ttk.Entry(main, width=8)
dd_p1.insert(0, "1")
dd_p1.grid(row=8, column=1)

dd_p2 = ttk.Entry(main, width=8)
dd_p2.insert(0, "1")
dd_p2.grid(row=8, column=2)


# --------------------------
# Buttons
# --------------------------

run_button = ttk.Button(
    main,
    text="Start",
    command=run_tournament
)

run_button.grid(
    row=10,
    column=0,
    pady=20
)

reset_button = ttk.Button(
    main,
    text="Reset Game",
    command=reset_game
)

reset_button.grid(
    row=10,
    column=1,
    pady=20
)


# --------------------------
# Output Window
# --------------------------

output = tk.Text(
    main,
    width=115,
    height=28
)

output.grid(
    row=11,
    column=0,
    columnspan=6,
    pady=10
)


root.mainloop()