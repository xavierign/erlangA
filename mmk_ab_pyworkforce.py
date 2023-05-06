from pyworkforce.queuing import ErlangC

erlang = ErlangC(transactions=120, asa=20, aht=60/4, interval=60, shrinkage=0.0)

positions_requirements = erlang.required_positions(service_level=0.956, max_occupancy=1)
print("positions_requirements: ", positions_requirements)