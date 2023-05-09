import simpy
import random
from runstats import Statistics
from math import exp
import csv

def generator(env, stats, q, capacity, lambd, mu, patience):
    while True:
        yield env.timeout(random.expovariate(lambd))
        r = request(env, stats, q, capacity, serviceTime=random.expovariate(mu), patience=random.expovariate(patience))
        env.process(r)

def request(env, stats, q, capacity, serviceTime, patience):
    stats['nArrived'] += 1
    arrTime = env.now

    stats['bufferLen'].push(len(q.queue))
    stats['serviceLen'].push(len(q.users))

    if len(q.users) == capacity:
        stats['nWaited'] += 1

    with q.request() as req:
        results = yield req | env.timeout(patience)
        t = env.now - arrTime
        stats['waitAll'].push(t)

        if req in results:
            stats['wait'].push(t)
            yield env.timeout(serviceTime)
        else:
            stats['waitAbandoned'].push(t)
            stats['nAbandoned'] += 1

def run_simulation(capacity, lambd, mu, patience, sim_time):
    env = simpy.Environment()
    stats = {
        'nArrived': 0,
        'nAbandoned': 0,
        'nWaited': 0,
        'wait': Statistics(),
        'waitAbandoned': Statistics(),
        'waitAll': Statistics(),
        'bufferLen': Statistics(),
        'serviceLen': Statistics()
    }
    q = simpy.Resource(env, capacity=capacity)
    env.process(generator(env, stats, q, capacity, lambd=lambd, mu=mu, patience=patience))
    env.run(until=sim_time)

    return stats

def calculate_metrics(stats, capacity, lambd, mu, patience,asa):  # Added 'patience' to the function arguments
    abandonment_rate = stats['nAbandoned'] / stats['nArrived']
    mean_wait_served = stats['wait'].mean()
    mean_wait_abandoned = stats['waitAbandoned'].mean()
    mean_wait_all = stats['waitAll'].mean()
    mean_buffer_length = stats['bufferLen'].mean()
    waiting_probability = stats['nWaited'] / stats['nArrived']

    intensity = lambd / mu * (1-abandonment_rate)
    
    exponential = exp(-(capacity - intensity) * (asa / (60 / mu)))
    service_level = max(0, 1 - (waiting_probability * exponential))
    occupancy = stats['serviceLen'].mean() / capacity

    return [capacity,lambd, mu, patience, mean_buffer_length, waiting_probability, service_level, occupancy, abandonment_rate]

def write_to_csv(file_name, capacities, results):
    headers = ['capacity', 'lambda', 'mu', 'patience', 'buffer_length', 'waiting_prob', 'service_level', 'occupancy','abandonment_rate']

    with open(file_name, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        for result in results:
            writer.writerow(result)

def main():
    lambd = 120
    mu = 4
    patiences = [0.00001,0.5,1,2,4]
    capacities = [31,32,33,34]
    sim_time = 40000
    asa = 8
    results = []
    for patience in patiences:
        for capacity in capacities:
            print(f"Running simulation for capacity: {capacity}")  # Progress print statement
            stats = run_simulation(capacity, lambd, mu, patience, sim_time)
            metrics = calculate_metrics(stats, capacity, lambd, mu, patience, asa)
            results.append(metrics)

    write_to_csv('call_center_metrics_simulation.csv', capacities, results)

if __name__ == "__main__":
    main()
