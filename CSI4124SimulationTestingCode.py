import numpy as np


def single_server_queue(interArrival, timeService, truckTracker):

    # Calculate arrival times
    for i in range(1, numPacket):
        arrivals[i] = arrivals[i - 1] + interArrival[i]

    # Main simulation for departure and system times
    for i in range(numPacket):
        # Calculate waiting time for each customer
        timeWait[i] = max(0, (depart[i - 1] - arrivals[i]))
        # Calculate departure time for each customer
        depart[i] = arrivals[i] + timeWait[i] + timeService[i]
        # Calculate system time for each customer
        timeSystem[i] = timeWait[i] + timeService[i]

    if truckTracker > 0:
        truckTracker = truckTracker - 1
        newInterArrival = depart + delay
        timeService = np.random.exponential(1 / meanServiceRate, numPacket)
        newDepart = single_server_queue(newInterArrival, timeService, truckTracker)

    # Return the departure times array
    return depart


# Variable Initialization
numTrucks = 5
numPacket = 20
meanArrivalRate = 1
meanServiceRate = 2
delay = 3

# Initialize arrays to store calculated times
arrivals = np.zeros(numPacket)
timeWait = np.zeros(numPacket)
timeSystem = np.zeros(numPacket)
depart = np.zeros(numPacket)

# Generate random interarrival and service times
interArrival = np.random.exponential(1/meanArrivalRate, numPacket)
timeService = np.random.exponential(1/meanServiceRate, numPacket)
# Get initial departure times
finalDepart = single_server_queue(interArrival, timeService, numTrucks)
print("Final departure times:", finalDepart)