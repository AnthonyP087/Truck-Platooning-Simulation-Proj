import numpy as np
import pandas as pd
import os
import math

INTER_ARRIVAL_TIME_RATE = 2800  # Mean packet arrival rate (packets/milliseconds)
SERVICE_TIME_RATE = 3000    # Mean service rate (packets/milliseconds)
MAX_QUEUE_LENGTH = 50       # The max length of each queue
PACKET_DELAY = 0.03           # The standard delay length for the packet to be processed by the truck
NUMBER_OF_PACKETS = 10000   # Number of packets to be passed from truck 1 to n
MAX_NUMBER_OF_TRUCKS = 15  # The highest number of trucks to be tested
# The threshold of processing time that a packets departure time must be under
TIME_THRESHOLD = 15*MAX_NUMBER_OF_TRUCKS
NUMBER_OF_TRIALS = 100      # The number of trials to run per number of trucks

packets = []
trucks = []


# Class that represents a packet
class Packet:
    status = True                   # Determines whether the packet has been lost or not
    inter_arrival_time = 0          # The inter-arrival time of the packet in the current truck
    send_time = 0                   # The time that the packet was initially sent at
    arrival_time = 0                # The arrival time of the packet in the current truck
    service_time = 0                # The service time of the packet in the current truck
    waiting_time = 0                # The waiting time of the packet in the current truck
    departure_time = 0
    system_time = 0                 # The departure time of the packet in the current truck


# Class that represents each truck
class Truck:

    # Processes each packet through this queue, resulting in how long the packets took to get through this queue,
    # how long they took to finish upto truck n, and whether the packet was lost or not
    @staticmethod
    def process_packet():

        # Sets up the arrival time for the first value. Random inter-arrival time generated only for first packet
        # if it is not the first truck.
        if packets[0].system_time == 0:
            packets[0].arrival_time = PACKET_DELAY
        else:
            packets[0].arrival_time = PACKET_DELAY + np.random.exponential(1 / INTER_ARRIVAL_TIME_RATE)

        # Sets up values for the first unique packet
        packets[0].service_time = np.random.exponential(1 / SERVICE_TIME_RATE)
        packets[0].waiting_time = 0
        packets[0].departure_time = packets[0].service_time + packets[0].arrival_time
        packets[0].system_time = (packets[0].waiting_time + packets[0].service_time + PACKET_DELAY +
                                  packets[0].inter_arrival_time + packets[0].system_time)

        # A waiting list that keeps track of which packets are waiting to be serviced
        waiting_list = []

        # A packet that gives the ability to compare the current packet to the previous one
        previous_packet = packets[0]

        # Loops through all the packets, determining their service time, waiting time, and departure time
        for packet in packets[1:]:

            # If the state of the packet is false (lost), continue to the next packet
            if not packet.status:
                continue

            # Calculate the inter arrival time and the arrival time using the previous trucks departure time
            packet.inter_arrival_time = np.random.exponential(1 / INTER_ARRIVAL_TIME_RATE)
            packet.arrival_time = packet.inter_arrival_time + PACKET_DELAY + previous_packet.arrival_time

            if packet.system_time == 0:
                packet.send_time = packet.arrival_time - PACKET_DELAY

            # Remove all packets from the waiting list that have finished waiting between the arrival of
            # this packet and the previous packet
            if len(waiting_list) > 0:
                while (waiting_list[-1].arrival_time + waiting_list[-1].waiting_time) <= packet.arrival_time:
                    waiting_list.pop()
                    if len(waiting_list) == 0:
                        break

            # If the length of the waiting list is at its maximum, the packet is lost
            if len(waiting_list) == MAX_QUEUE_LENGTH:
                packet.departure_time = previous_packet.departure_times
                packet.status = False
                continue

            # Calculate the service time, waiting time, and departure time
            packet.service_time = np.random.exponential(1 / SERVICE_TIME_RATE)
            packet.waiting_time = max(previous_packet.departure_time - packet.arrival_time, 0)
            packet.departure_time = packet.arrival_time + packet.service_time + packet.waiting_time
            packet.system_time = (packet.system_time + packet.service_time + packet.waiting_time + PACKET_DELAY +
                                  packet.inter_arrival_time)

            # If the packet has waiting time, track it in the waiting list
            if packet.waiting_time > 0:
                waiting_list.append(packet)

            previous_packet = packet

            # print("Inter-arrival time: " + str(packet.inter_arrival_time))
            # print("Arrival time: " + str(packet.arrival_time))
            # print("Waiting time: " + str(packet.waiting_time))
            # print("Service time: " + str(packet.service_time))
            # print("Departure time: " + str(packet.truck_n_departure_time))
            # print("Waiting list length: " + str(len(waiting_list)))
            # print("System time: " + str(packet.system_time))
            # print("------------")


def main():

    # Setup arrays to hold trial reliabilitiess
    reliabilities = [[0 for _ in range(MAX_NUMBER_OF_TRUCKS)] for _ in range(NUMBER_OF_TRIALS)]
    system_times = [[0 for _ in range(NUMBER_OF_PACKETS)] for _ in range(NUMBER_OF_TRIALS)]

    # Create excel headers
    headers_reliabilities = [str(i + 1) + " TRUCK(s)" for i in range(MAX_NUMBER_OF_TRUCKS)]
    headers_system_times = ["PACKET " + str(i + 1) for i in range(NUMBER_OF_PACKETS)]

    # Perform simulation for each number of trucks NUMBER_OF_TRIALS times
    for i in range(0, NUMBER_OF_TRIALS):
        init()

        # Perform simulation for each number of trucks
        for j in range(0, MAX_NUMBER_OF_TRUCKS):

            # Initialize the values, run the simulation, and add the reliabilities to the array
            trucks[j].process_packet()
            reliabilities[i][j] = reliability(j + 1)

        for k in range(0, NUMBER_OF_PACKETS):

            system_times[i][k] = packets[k].system_time

    print(reliabilities[0])
    # print(system_times[0])

    # Specify the path to the desktop (Windows Example)
    desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop', 'trucks_pandas.xlsx')

    # Create excel data frame with headers as the headers and export it to excel
    df_reliabilities = pd.DataFrame(data=reliabilities, columns=headers_reliabilities)
    df_system_times = pd.DataFrame(data=system_times, columns=headers_system_times)

    with pd.ExcelWriter(desktop_path) as writer:
        df_reliabilities.to_excel(writer, sheet_name='Reliabilities', index=False)
        df_system_times.to_excel(writer, sheet_name='System Times', index=False)

    return


# Initialize the packets and trucks
def init():

    # Clear the packets and trucks from previous iterations
    packets.clear()
    trucks.clear()

    # Set up the list of packets
    for i in range(NUMBER_OF_PACKETS):
        packets.append(Packet())

    # Set up the list of trucks
    for i in range(MAX_NUMBER_OF_TRUCKS):
        trucks.append(Truck())

    return


# Returns the reliability of a list of packets
def reliability(truck_number):

    reliability_metric = 0

    # Assigns 0 to any packet lost, or taking longer than the time threshold
    for packet in packets:
        if packet.status:
            reliability_metric += 1

    # Returns the average of the above indicator functions
    return ((reliability_metric/len(packets)) * math.pow(0.999, truck_number)
            * math.pow(0.999, truck_number - 1))


main()
