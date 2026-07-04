import matplotlib.pyplot as plt
import numpy as np

####################################################################################################
############################################ unified model #########################################
####################################################################################################

def run_unified_simulation(
    payoff_matrix,
    population,
    tokenB_vault,
    USDC_vault,
    tokenB_price_USDC,
    tokenB_supply_circ,
    comission,
    floor_increase_factor,
    risk_lambda,
    risk_impact_matrix,
    iterations
):
    payoff_matrix = np.array(payoff_matrix, dtype=float)
    risk_impact_matrix = np.array(risk_impact_matrix, dtype=float)
    population = np.array(population, dtype=float)

    vault = tokenB_price_USDC * tokenB_vault + USDC_vault
    tokenB_total_supply = tokenB_supply_circ + tokenB_vault
    floor_price_B = vault / tokenB_total_supply

    vault_history = []
    risk_history = []
    price_history = []
    floor_history = []
    price_to_floor_history = []

    population_A_history = [population_shareA] # change here
    population_B_history = [population_shareB]

    payoff_A_history = []
    payoff_B_history = []

    cumulative_payoff_A_history = []
    cumulative_payoff_B_history = []

    cumulative_payoff_A = 0
    cumulative_payoff_B = 0

    for _ in range(iterations):

        # -----------------------------------------------------------------------------------
        # Protocol update
        # -----------------------------------------------------------------------------------

        vault += comission
        floor_price_B = vault / tokenB_total_supply

        if floor_price_B > tokenB_price_USDC:
            tokenB_price_USDC *= floor_increase_factor

        risk = (tokenB_price_USDC / vault) * 10000 #change here
        tokenB_to_floor = tokenB_price_USDC / floor_price_B

        # -----------------------------------------------------------------------------------
        # Risk-adjusted payoff matrix
        # -----------------------------------------------------------------------------------

        adjusted_payoff_matrix = payoff_matrix - (risk * risk_impact_matrix) #* risk_lambda

        # -----------------------------------------------------------------------------------
        # EGT fitness calculation
        # -----------------------------------------------------------------------------------

        fitness = adjusted_payoff_matrix @ population

        payoff_A = fitness[0]
        payoff_B = fitness[1]
      
        average_fitness = population @ fitness

        x_dot = population * (fitness - average_fitness)

        population = population + x_dot

        # Avoid negative population shares
        population = np.maximum(population, 0)

        # Normalize population so x_A + x_B = 1
        population = population / np.sum(population)

        # -----------------------------------------------------------------------------------
        # Cumulated payoffs
        # -----------------------------------------------------------------------------------

        cumulative_payoff_A += payoff_A
        cumulative_payoff_B += payoff_B

        # -----------------------------------------------------------------------------------
        # Store histories
        # -----------------------------------------------------------------------------------

        vault_history.append(vault)
        risk_history.append(risk)
        price_history.append(tokenB_price_USDC)
        floor_history.append(floor_price_B)
        price_to_floor_history.append(tokenB_to_floor)

        population_A_history.append(population[0])
        population_B_history.append(population[1])

        payoff_A_history.append(payoff_A)
        payoff_B_history.append(payoff_B)

        cumulative_payoff_A_history.append(cumulative_payoff_A)
        cumulative_payoff_B_history.append(cumulative_payoff_B)

    return {
        "vault": vault,
        "tokenB_price_USDC": tokenB_price_USDC,
        "floor_price_B": floor_price_B,
        "risk": risk,
        "tokenB_to_floor": tokenB_to_floor,

        "vault_history": vault_history,
        "risk_history": risk_history,
        "price_history": price_history,
        "floor_history": floor_history,
        "price_to_floor_history": price_to_floor_history,

        "population_A_history": population_A_history,
        "population_B_history": population_B_history,

        "payoff_A_history": payoff_A_history,
        "payoff_B_history": payoff_B_history,

        "cumulative_payoff_A_history": cumulative_payoff_A_history,
        "cumulative_payoff_B_history": cumulative_payoff_B_history,
    }


####################################################################################################
############################################ parameters ############################################
####################################################################################################

#[2.5, 2],[4, 3]
payoff_matrix = [
    [2.5, 2],
    [4, 3]
]

# If A sees A, that means there is a lot of As around which is a positive signal for growth, but expected because A = incumbant, so the payoff is lower than for B seeing B
# If A sees B, that should be rather unusual, could mean something is wrong with protocol A for that reason there starts being more Bs
# If B sees A, that means there is a lot of room for growth so that is the best position B can be in
# If B sees B, that means there is a lot of Bs around which is a positive signal for growth

population_shareA = 0.9
population_shareB = 0.1
population = [population_shareA, population_shareB]

risk_impact_matrix = [
    [0, -1],
    [1, 2]
] 
# the risk impact matrix is designed to reflect risk on B, so when A sees A or A sees B there is no risk impact for B
# when B sees A, that is normal and even positive for B because it means B is not too oversaturated yet
# when B sees B, that is a strong indicator that there are too many B's around and risk is soo goin

tokenB_vault = 200
USDC_vault = 9800
tokenB_price_USDC = 1
tokenB_supply_circ = 10000  #10000

iterations = 150000 # 1000000
comission = 0.02
floor_increase_factor = 1.2
risk_lambda = 1

initial_risk = (tokenB_price_USDC / (tokenB_price_USDC * tokenB_vault + USDC_vault)) * 10000
print('initial risk: ', initial_risk )
tokenB_total_supply = tokenB_supply_circ + tokenB_vault
print('initial floor price: ', (tokenB_price_USDC * tokenB_vault + USDC_vault) / tokenB_total_supply)

####################################################################################################
############################################ execution #############################################
####################################################################################################

results = run_unified_simulation(
    payoff_matrix=payoff_matrix,
    population=population,
    tokenB_vault=tokenB_vault,
    USDC_vault=USDC_vault,
    tokenB_price_USDC=tokenB_price_USDC,
    tokenB_supply_circ=tokenB_supply_circ,
    comission=comission,
    floor_increase_factor=floor_increase_factor,
    risk_lambda=risk_lambda,
    risk_impact_matrix=risk_impact_matrix,
    iterations=iterations
)

####################################################################################################
############################################ results ###############################################
####################################################################################################

print("\nresults after", iterations, "iterations:")
print("vault:", results["vault"])
print("tokenB_price_USDC:", results["tokenB_price_USDC"])
print("floor_price_B:", results["floor_price_B"])
print("risk:", results["risk"])
print("tokenB_to_floor:", results["tokenB_to_floor"])
print("final population A:", results["population_A_history"][-1])
print("final population B:", results["population_B_history"][-1])
print("cumulated payoff A:", results["cumulative_payoff_A_history"][-1])
print("cumulated payoff B:", results["cumulative_payoff_B_history"][-1])

ranked_popA = sorted(results['population_A_history'], reverse=True)[1:-1]
ranked_popB = sorted(results['population_B_history'], reverse=True)[1:-1]

print('PopA share min (excl. initial value): ',min(ranked_popA))
print('PopA share max (excl. initial value): ',max(ranked_popA))
print('PopB share min (excl. initial value): ',min(ranked_popB))
print('PopB share max: ',max(ranked_popB))

print('This is the average cumulative payoff for population A:', results['cumulative_payoff_A_history'][-1]/iterations)
print('This is the average cumulative payoff for population B:', results['cumulative_payoff_B_history'][-1]/iterations)

####################################################################################################
############################################ graphs ################################################
####################################################################################################

x_axis = range(iterations)

fig, axs = plt.subplots(4, 2, figsize=(10, 6))

# Vault
axs[0, 0].plot(x_axis, results["vault_history"])
axs[0, 0].set_title("Vault Value")
axs[0, 0].set_xlabel("Iterations")
axs[0, 0].set_ylabel("Vault")
axs[0, 0].grid(True)

# Risk
axs[0, 1].plot(x_axis, results["risk_history"])
axs[0, 1].set_title("Risk")
axs[0, 1].set_xlabel("Iterations")
axs[0, 1].set_ylabel("Risk")
axs[0, 1].grid(True)

# Token Price
axs[1, 0].plot(x_axis, results["price_history"])
axs[1, 0].set_title("Token B Price")
axs[1, 0].set_xlabel("Iterations")
axs[1, 0].set_ylabel("Price")
axs[1, 0].grid(True)

# Price / Floor Ratio
axs[1, 1].plot(x_axis, results["price_to_floor_history"])
axs[1, 1].set_title("Price / Floor Ratio")
axs[1, 1].set_xlabel("Iterations")
axs[1, 1].set_ylabel("Price / Floor")
axs[1, 1].grid(True)

axs[2, 0].plot(x_axis, results["population_A_history"][0:-1], label="A")
axs[2, 0].plot(x_axis, results["population_B_history"][0:-1], label="B")
axs[2, 0].set_title("Population Shares")
axs[2, 0].set_xlabel("Iterations")
axs[2, 0].set_ylabel("Share")
axs[2, 0].legend()
axs[2, 0].grid(True)

# Payoff per Iteration
axs[2, 1].plot(x_axis, results["payoff_A_history"], label="A")
axs[2, 1].plot(x_axis, results["payoff_B_history"], label="B")
axs[2, 1].set_title("Payoff per Iteration")
axs[2, 1].set_xlabel("Iterations")
axs[2, 1].set_ylabel("Payoff")
axs[2, 1].legend()
axs[2, 1].grid(True)

# Cumulative Payoff
axs[3, 0].plot(x_axis, results["cumulative_payoff_A_history"], label="A")
axs[3, 0].plot(x_axis, results["cumulative_payoff_B_history"], label="B")
axs[3, 0].set_title("Cumulative Payoff")
axs[3, 0].set_xlabel("Iterations")
axs[3, 0].set_ylabel("Cumulative Payoff")
axs[3, 0].legend()
axs[3, 0].grid(True)

# Floor Price
axs[3, 1].plot(x_axis, results["floor_history"])
axs[3, 1].set_title("Floor Price B")
axs[3, 1].set_xlabel("Iterations")
axs[3, 1].set_ylabel("Floor Price")
axs[3, 1].grid(True)

plt.tight_layout()
plt.show()
