import numpy as np
import simpy

# Parameters (mean and standard deviation are tied in the exponential distribution)
INTERARRIVAL_TIME_RATE = 1  # Mean packet arrival rate (packets/second)
SERVICE_TIME_RATE = 1000  # Mean service time (milliseconds)
NUMBER_OF_TRUCKS = 5        # Number of trucks in the platoon
PACKETS_TO_SEND = 50        # Number of packets to be sent
MAX_QUEUE_LENGTH = 10       # Maximum number of packets in a queue


# Exponential distribution for inter-arrival time (mean = 1/lambda)
def inter_arrival_time():
    return np.random.exponential(1 / INTERARRIVAL_TIME_RATE)


# Exponential distribution for service time (mean = 1/lambda)
def service_time():
    return np.random.exponential(1 / SERVICE_TIME_RATE)


# Customer (packet) process for each truck
def packet(env, name, server, truck_num, next_queue):
    arrival_time = env.now
    print(f'{name} arrived at Truck {truck_num} queue at {arrival_time:.2f}ms')

    with server.request() as request:
        yield request  # Wait for a server (queue slot)
        wait_time = env.now - arrival_time
        print(f'{name} starts service at Truck {truck_num} after waiting {wait_time:.2f}ms')
        
        service_duration = service_time()
        yield env.timeout(service_duration)  # Service time
        total_time_in_system = env.now - arrival_time
        
        print(f'{name} leaves Truck {truck_num} after {total_time_in_system:.2f}ms')
        
        if next_queue is not None:  # Pass to the next truck (queue)
            env.process(packet(env, name, next_queue, truck_num + 1, None if truck_num == NUMBER_OF_TRUCKS - 1 else next_queue))


# Set up each truck's server and start processing packets
def setup(env, servers):
    for i in range(PACKETS_TO_SEND):
        env.process(packet(env, f'Packet {i + 1}', servers[0], 1, servers[1] if NUMBER_OF_TRUCKS > 1 else None))
        yield env.timeout(inter_arrival_time() * 1000)  # Interarrival time (in ms)


if __name__ == "__main__":
    # Simulation environment
    env = simpy.Environment()

    # Create a queue (server) for each truck
    servers = [simpy.Resource(env, capacity=MAX_QUEUE_LENGTH) for _ in range(NUMBER_OF_TRUCKS)]

    # Start the simulation
    env.process(setup(env, servers))
    env.run()
