from math import exp
import numpy as np

#System parameters 
capacity = 32
lambd = 120
mu = 4
patience = 0.00001

#This is the maximum system lenght. 
#Beyond that the customer does not enter the system
#8 customers waiting for each agent.
n_states = capacity*8

# Create a zero matrix of size 256x256
A = np.zeros((n_states, n_states))

# Set the diagonal elements to lambda (120)
np.fill_diagonal(A, lambd)

# Set the last column elements to 1
A[:, -1] = 1

b = np.zeros(n_states)
b[-1] = 1

for i in range(1,n_states):
	if i <= capacity:
		A[i, i-1] = -i*mu
	else:
		A[i, i-1] = -capacity*mu

print("Matrix A:")
print(A)

# Solve the linear system A^Tp^T = b
pT = np.linalg.solve(A.transpose(), b)

# Transpose the result back to obtain p
probs_best = pT.reshape(1, -1)[0]
#print("Solution p:",probs_best )

#calculate metrcis with probs_best
#print(probs_best)

#buffer_length, average size of the queue
buffer_length = sum([(i-capacity)*probs_best[i] for i in range(capacity+1,n_states)])
print(buffer_length)

#waitig probability
waiting_prob = 	sum([probs_best[i] for i in range(capacity,n_states)])	
print(waiting_prob)

#service level / formula from Erlang-A
intensity = lambd / mu
asa = 1/3*60 #20 minutes
exponential = exp(-(capacity - intensity) * (asa / (60/mu)))
service_level = max(0, 1 - (waiting_prob * exponential))
print(service_level)

#achieved occupancy
H = sum([i*probs_best[i] for i in range(capacity+1)]) + sum([capacity*probs_best[i] for i in range(capacity+1,n_states)]) 
occupancy = H/capacity
print(occupancy)



