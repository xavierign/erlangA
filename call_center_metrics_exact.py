import numpy as np
from math import exp
import csv

def calculate_probs_best(capacity, lambd, mu, patience, n_states):
    A = np.zeros((n_states, n_states))
    np.fill_diagonal(A, lambd)
    A[:, -1] = 1

    b = np.zeros(n_states)
    b[-1] = 1

    for i in range(1, n_states):
        if i <= capacity:
            A[i, i-1] = -i * mu
        else:
            A[i, i-1] = -(capacity * mu + patience*(i-capacity))

    pT = np.linalg.solve(A.transpose(), b)
    return pT.reshape(1, -1)[0]

def buffer_length(capacity, n_states, probs_best):
    return sum([(i-capacity)*probs_best[i] for i in range(capacity+1, n_states)])

def waiting_prob(capacity, n_states, probs_best):
    return sum([probs_best[i] for i in range(capacity, n_states)])

def service_level(lambd, mu, capacity, waiting_prob_value, asa,abandon_prob_value):
    #review this formula with patience >0
    intensity = lambd / mu *(1-abandon_prob_value)
    exponential = exp(-(capacity - intensity) * (asa / (60 / mu)))
    return max(0, 1 - (waiting_prob_value * exponential))

def occupancy(capacity, n_states, probs_best):
    H = sum([i * probs_best[i] for i in range(capacity + 1)]) + sum(
        [capacity * probs_best[i] for i in range(capacity + 1, n_states)])
    return H / capacity

def abandon_prob(lambd, mu, capacity, occupancy_value):
    mu_raya = occupancy_value*capacity*mu
    return 1 - mu_raya/lambd

def write_to_csv(file_name, results):
    headers = ['capacity', 'lambda', 'mu', 'patience', 'buffer_length', 'waiting_prob', 'service_level', 'occupancy','abandonment_rate']

    with open(file_name, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        for result in results:
            writer.writerow(result)

def calculate_metrics(capacity, lambd, mu, patience = 10, n_states=None):
    if n_states is None:
        n_states = capacity * 32
    asa = 6 # 10 minutes service level
    #patience = 15 # 4 = 60/15 minutes is the average wait time until abandon
    probs_best = calculate_probs_best(capacity, lambd, mu, patience, n_states)           
    buffer_len = buffer_length(capacity, n_states, probs_best)
    waiting_prob_value = waiting_prob(capacity, n_states, probs_best)
    occupancy_value = occupancy(capacity, n_states, probs_best) 
    abandon_prob_value = abandon_prob(lambd, mu, capacity, occupancy_value)
    service_level_value = service_level(lambd, mu, capacity, waiting_prob_value, asa,abandon_prob_value)
    return service_level_value, abandon_prob_value,occupancy_value


def main():
    lambd = 16.06#customer / hour
    mu = 60/13.5 # customer / hour
    patiences = [6,8,10,12,14] #lost calls per hour
    capacities = [2, 3, 4, 5, 6] # number of agents
    asa = 10  # service requirement for wait times in minutes (service level)
    results = []
    for patience in patiences:
        for capacity in capacities:
            n_states = capacity * 16
            probs_best = calculate_probs_best(capacity, lambd, mu, patience, n_states)           
            buffer_len = buffer_length(capacity, n_states, probs_best)
            waiting_prob_value = waiting_prob(capacity, n_states, probs_best)
            occupancy_value = occupancy(capacity, n_states, probs_best) 
            abandon_prob_value = abandon_prob(lambd, mu, capacity, occupancy_value)
            service_level_value = service_level(lambd, mu, capacity, waiting_prob_value, asa,abandon_prob_value)

            results.append([capacity,lambd, mu, patience, buffer_len, waiting_prob_value, service_level_value, 
                                occupancy_value, abandon_prob_value])

    write_to_csv('call_center_metrics_exact.csv', results)
    print(calculate_metrics(6, 16.064927733086996, 60/13.5))

if __name__ == "__main__":
    main()

