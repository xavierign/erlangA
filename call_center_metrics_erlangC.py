import csv
from pyworkforce.queuing import ErlangC

def write_to_csv(file_name, service_levels, results):
    headers = ['service_level_req', 'raw_positions', 'positions', 'occupancy', 'waiting_probability','service_level']

    with open(file_name, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        for service_level, result in zip(service_levels, results):
            writer.writerow([service_level] + result)

def main():
    lambd = 120
    mu = 4
    patience = 0.00001
    asa = 8
    aht = 60 / mu
    interval = 60
    shrinkage = 0.0
    upp_lim = 0.98
    low_lim = 0.53
    service_levels = [round(low_lim + i * (upp_lim - low_lim) / 9, 3) for i in range(10)]

    results = []
    for service_level in service_levels:
        erlang = ErlangC(transactions=lambd, asa=asa, aht=aht, interval=interval, shrinkage=shrinkage)
        positions_requirements = erlang.required_positions(service_level=service_level, max_occupancy=1)
        print(f"Running ErlangC for service_level: {service_level}")
        print("positions_requirements: ", positions_requirements)
        results.append([positions_requirements['raw_positions'], positions_requirements['positions'],
                        positions_requirements['occupancy'], positions_requirements['waiting_probability'],
                         positions_requirements['service_level']])

    write_to_csv('call_center_metrics_erlangC.csv', service_levels, results)

if __name__ == "__main__":
    main()
