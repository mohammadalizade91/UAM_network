import numpy as np


def cost_calculator(vertiports: list, demands: list, aircraft_capacity: int) -> (float, float, float):
    """
    This function calculate total cost, cost per each demand (average), and cost per aircraft (average)
    by using interpolation between flight hours and their respected operating cost.

    Args:
        vertiports (list): list of vertiport objects after simulation.
        demands (list): list of demand objects after simulation.
        aircraft_capacity (int)

    Returns:
        cost (float): total flight cost of the network.
        cost_per_demand (float): average flight cost of a successful demand.
        cost (float): average flight cost of an aircraft.

    """
    cost = 0
    number_of_aircraft = 0
    
    flight_hour_list = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6,0.7,0.8,0.9, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
    cost_list_4_pax = [3799, 1960.9, 1348.1, 1041.7, 857.9, 735.4, 647.9, 582.2, 531.1, 490.3, 306.4, 245.1, 214.5, 196.1, 183.9, 175.1, 168.6, 163.5, 159.4, 156, 153.2, 150.9, 148.9, 147.15, 145.6, 144.2, 143]
    cost_list_8_pax = [7381, 3781, 2581, 1981, 1622, 1382, 1210, 1082, 982, 902, 542, 422.1, 362, 326, 302, 285, 272, 262, 254, 247, 242, 237, 233, 230, 227, 224, 222]
    cost_list_12_pax = [10811, 5516, 3751, 2868, 2339, 1986, 1734, 1544, 1397, 1280, 750, 574.1, 486, 433, 397, 372, 353, 339, 327, 317, 309, 302, 297, 291, 287, 283, 280]
    
    if aircraft_capacity == 4:
        cost_list = cost_list_4_pax
    elif aircraft_capacity == 8:
        cost_list = cost_list_8_pax
    elif aircraft_capacity == 12:
        cost_list = cost_list_12_pax
        
    for vertiport in vertiports:
        number_of_aircraft += len(vertiport.aircrafts)
        
        for aircraft in vertiport.aircrafts:
            cost_per_flight_hour = np.interp(aircraft.flight_hours, flight_hour_list, cost_list)
            cost += aircraft.flight_hours * cost_per_flight_hour
    satisfied_demands_percent, satisfied_demands = calc_satisfied_percent(demands)
    if not satisfied_demands or not number_of_aircraft:
        return cost, 0, 0
    cost_per_demand = cost / satisfied_demands
    cost_per_aircraft = cost / number_of_aircraft    
    
    return cost, cost_per_demand, cost_per_aircraft


def calc_satisfied_percent(demands: list) -> (float, int):
    """
    This function calculates number of satisfied demands and its ratio (in percent) to 
    total number of demands.

    Args:
        demands (list): list of demand objects after simulation.

    Returns:
        satisfied_demand_percent (float)
        number_of_satisfied_demands (int)

    """
    satisfied_demands = [i.id_ for i in demands if i.status.lower() == 'satisfied']
    satisfied_demand_percent = (len(satisfied_demands)/len(demands))*100
    number_of_satisfied_demands = len(satisfied_demands)
    return satisfied_demand_percent, number_of_satisfied_demands


def calc_mean_flight_delay(demands: list) -> float:
    """
    This function calculates mean flight delay of each successful mission in hours.

    Args:
        demands (list): list of demand objects after simulation.

    Returns:
        mean_flight_delay (float): average flight delay for a satisfied demand in hours.

    """
    flight_delays = []
    for demand in demands:
        if demand.status.lower() == 'satisfied':
            flight_delays.append(demand.delayed_at['flight_delay'])
    mean_flight_delay = np.mean(flight_delays)/3600
    return mean_flight_delay


def calc_mean_flight_hours(vertiports: list) -> float:
    """
    This function calculates mean flight hours of each aircraft in hours.

    Args:
        vertiports (list): list of vertiport objects after simulation.

    Returns:
        mean_flight_hours (float): average flight hours of each aircraft on hours.

    """
    flight_hours = []
    for vertiport in vertiports:
        for aircraft in vertiport.aircrafts:
            flight_hours.append(aircraft.flight_hours)
    mean_flight_hours = np.mean(flight_hours)
    return mean_flight_hours


def calc_number_of_flights(vertiports: list) -> int:
    """
    This function calculates number of flights in a simulation.

    Args:
        vertiports (list): list of vertiport objects after simulation.

    Returns:
        number_of_flights (int)

    """
    number_of_flights = 0
    for vertiport in vertiports:
        number_of_flights += len(vertiport.arriving_aircrafts)
    return number_of_flights