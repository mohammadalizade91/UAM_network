import pickle as pk

from create_objects import create_vertiport, create_demands
from create_schedule import create_schedule
from run_simulation import run_simulation
from utility import cost_calculator, calc_satisfied_percent, calc_mean_flight_delay, calc_mean_flight_hours, calc_number_of_flights

def run_main(mode: str, cruise_speed: (int, float), capacity: int, vertiport_file_name: str, start_demand: int, 
             end_demand: int, demand_step: int, maximum_wait_time: (float, int)) -> None:
    """
    This function will run a series of simulations for 16 hours for given "mode", "cruise_speed", 
    aircraft "capacity" and "maximum_flight_delay". This simulations will be based on certain 
    number of demands between "start_demand" and "end_demand" by increment in the start demand
    by "demand_step". All simulations' data will be stored in a file with this file name:
        mode + '_speed_' + str(cruise_speed) + '_wait_' + str(maximum_fligh_delay) + '_capacity_' + str(capacity) + '.p'
    othe types of data could be changed in the body of this function:
        1- climb_speed: total speed of aircraft in climb phase in knots.
        2- descent_speed: total speed of aircraft in descent phase in knots.
        3- aircraft_climb_rate:  rate of increase in altitude in climb phase in fpm.
        4- aircraft_descent_rate:  rate of decrease in altitude in descent phase in fpm.
        5- cruise_altitude: cruise altitude of aircraft in ft. (AGL)
        6- start_time: start of simulation and first interval of demand production in epoch.
        7- end_time: last interval of demand production in epoch (simulation will continue for one 
                                                         hour after the end_time).
        8- landing_occupation_time: required time for an aircraft to descent, land and to leave a 
                                    landing pad in seconds.
        9- takeoff_occupation_time: required time for an aircraft to finish its takeoff sequences 
                                    and leave the landing pad in seconds.
        10- holding_duration: maximum time for holding (before landing) in seconds.
        11- battery_swap_time: required time to change an aircraft's battery in seconds.
        12- board_time_per_passenger: required time to board a passenger in seconds.
        13- deboard_time_per_passenger: required time to deboard a passenger in seconds.

    Args:
        mode (str): is one of these four modes to determine when an aircraft should leave the vertiport:
            1- capacity method: "capacity"
            2- capacity method with max time on station: "capacity_station"
            3- wait time method: "wait"
            4- wait time method with max time on station: "station_wait"
        cruise_speed ((int, float)): cruise speed in knots.
        capacity (int): aircraft capacity.
        vertiport_file_name (str): vertiport file that contains its location, pads and number of stands.
        start_demand (int): first demand number to simulate.
        end_demand (int): maximum demand number to simulate.
        demand_step (int): amount of increment in demand number in each step.
        maximum_wait_time ((float, int)): Max wait time for passengers for an aircraft.

    Returns:
        None.

    """
    climb_speed = 113 #knots
    descent_speed = 113
    aircraft_climb_rate = 1000 # ft/min
    aircraft_descent_rate = 1000 # ft/min
    cruise_altitude = 1500 # ft
    # creating aircraft info dict
    aircraft_info = {1:{'climb_speed':climb_speed, 'climb_rate':aircraft_climb_rate, 
                    'cruise_altitude':cruise_altitude, 'cruise_speed':cruise_speed,
                    'descent_speed':descent_speed, 'descent_rate':aircraft_descent_rate, 'capacity':capacity}}
    start_time = 1668832200 # epoch
    end_time = 1668886200 # epoch
    landing_occupation_time = 180 #seconds
    takeoff_occupation_time = 120 #seconds
    holding_duration = 600 #seconds
    # Loading max station time data
    max_station_time_data = pk.load(open('max_station_time.p', 'rb'))
    battery_swap_time = 300 
    board_time_per_passenger = 60 
    deboard_time_per_passenger = 60
    
    out_data = {}
    out_file_name = mode + '_speed_' + str(cruise_speed) + '_wait_' + str(maximum_wait_time) + '_capacity_' + str(capacity) + '.p'
    
    while start_demand <= end_demand:
        # creating vertiport objects
        vertiports, last_id = create_vertiport(vertiport_file_name, aircraft_info)
        # creating demand schedule info
        demand_schedule_data = create_schedule(vertiports, start_demand, start_time, end_time)
        # creating demand objects
        demands, last_id = create_demands(demand_schedule_data, last_id)
        # running simultion
        vertiports, demands, msg_list, current_epoch = run_simulation(mode, vertiports, demands, landing_occupation_time, takeoff_occupation_time, battery_swap_time, board_time_per_passenger, deboard_time_per_passenger, \
                                                                      holding_duration, aircraft_info, max_station_time_data, maximum_wait_time, start_time, end_time + 3600)
        # storing data
        if msg_list:
            out_data[start_demand] = {'total_demands':None, 'demands':None, 'vertiports':None, 'satisfied_demands': None,
                                    'cost':None, 'cost_per_demand':None, 'cost_per_aircraft':None, 'mean_flight_delay': None,
                                    'mean_flight_hours':None, 'passenger_per_flight':None}
        else:
            cost, cost_per_demand, cost_per_aircraft = cost_calculator(vertiports, demands, capacity)
            satisfied_demands_percent, satisfied_demands = calc_satisfied_percent(demands)
            mean_flight_delay = calc_mean_flight_delay(demands)
            mean_flight_hours = calc_mean_flight_hours(vertiports)
            number_of_flights = calc_number_of_flights(vertiports)
            passenger_per_flight = satisfied_demands / number_of_flights
            out_data[start_demand] = {'total_demands':len(demands), 'demands':demands, 'vertiports':vertiports, 'satisfied_demands':satisfied_demands_percent,
                                       'cost':cost, 'cost_per_demand':cost_per_demand, 'cost_per_aircraft':cost_per_aircraft,
                                       'mean_flight_delay': mean_flight_delay, 'mean_flight_hours':mean_flight_hours,
                                       'passenger_per_flight':passenger_per_flight}
        # increment in demand
        start_demand += demand_step
        # drop data in the form of a pickle file
        pk.dump(out_data,open(out_file_name,'wb'))
