import numpy as np
from math import sqrt
from copy import deepcopy
from objects import Vertiport, Aircraft


def object_finder(objects: list, attribute_dict: dict):
    """
    This function finds an object with the attributes in the attribute_dict.

    Args:
        objects (list)
        attribute_dict (dict): a dict to find objects in this form:
            {attribute: attribute value that we want}

    Returns:
        out_obj : found object.

    """
    out_obj = []
    for obj in objects:
        for attribute in attribute_dict:
            if getattr(obj, attribute) == attribute_dict[attribute]:
                out_obj = [obj]
            else:
                out_obj = []
                break
        if out_obj:
            break
    if not out_obj:
        out_obj = ['object not found']
    return out_obj


def distnace_calculator(point1: list, point2: list) -> float:
    """
    This function calc distance between two points. These point have coordinates in nmi.

    Args:
        point1 (list): a position in this form: [x in nmi, y in nmi].
        point2 (list): a position in this form: [x in nmi, y in nmi].

    Returns:
        distance (float): 2D distance between point1 and point2.

    """
    distance = sqrt((point1[0]-point2[0])**2 + (point1[1]-point2[1])**2)
    return distance
    

def create_flight_schedule_for_starting_aircraft(aircraft: Aircraft, aircraft_info: dict, 
                                                 start_time: int, 
                                                 takeoff_occupation_time: int, 
                                                 airports: list) -> list:
    """
    This function creates a schedule list for a starting aircraft and total
    """
    schedule_list = []
    climb_speed = aircraft_info[aircraft.db_id]['climb_speed'] # knots
    aircraft_climb_rate = aircraft_info[aircraft.db_id]['climb_rate'] # ft/min
    cruise_altitude = aircraft_info[aircraft.db_id]['cruise_altitude'] # ft
    cruise_speed = aircraft_info[aircraft.db_id]['cruise_speed'] # knots
    # takeoff section
    origin_airport = object_finder(airports, {'id_':aircraft.origin_id})[0]
    schedule_list.append({'t_0':start_time, 't_f': start_time + takeoff_occupation_time, 'type':'takeoff',
                          'distance':0})
    # climb section
    start_time += takeoff_occupation_time
    climb_duration = (cruise_altitude/aircraft_climb_rate) * 60 # seconds
    climb_ground_speed =  sqrt(climb_speed**2 - (aircraft_climb_rate*0.00987473)**2) # knots
    climb_distance = (climb_duration/3600)*climb_ground_speed # nautical mile
    schedule_list.append({'t_0':start_time, 't_f': start_time + climb_duration, 'type':'climb', 'distance':climb_distance})
    # cruise section
    start_time += climb_duration
    destination_airport = object_finder(airports, {'id_':aircraft.destination_id})[0]
    total_distance = distnace_calculator(origin_airport.position, destination_airport.position)
    cruise_distance = total_distance - 2*climb_distance
    cruise_duration = (cruise_distance/cruise_speed)*3600
    schedule_list.append({'t_0':start_time, 't_f': start_time + cruise_duration, 'type':'cruise', 'distance':cruise_distance})
    return schedule_list


def create_flight_schedule_for_landing_aircraft(aircraft: Aircraft, current_time: int, 
                                                aircraft_info: dict, 
                                                landing_occupation_time: int, 
                                                airports: list) -> list:
    """
    This function creates a schedule list for a landing aircraft.
    """
    schedule_list = []
    holding_schedule = find_object_schedule_by_type(aircraft, 'holding')
    cruise_schedule = find_object_schedule_by_type(aircraft, 'cruise')
    if not holding_schedule:
        start_time = cruise_schedule['t_f']
    else:
        start_time = current_time
    schedule_list.append({'t_0':start_time, 't_f': start_time + landing_occupation_time, 'type':'landing',
                          'distance':0})
    return schedule_list
    

def find_object_schedule_by_type(obj: Aircraft, schedule_type: str) -> dict:
    """
    This function finds schedule info of schedule type in objects (mostly aircraft).
    """
    for time_schedule in obj.schedule_list:
        if time_schedule['type'].lower() == schedule_type:
            return time_schedule
    return {}


def move_aircaft_obj_to_destination_airport(aircraft_obj: Aircraft, vertiports: list) -> list:
    """
    This function moves an aircraft obj from its origin object to destination object.
    """
    origin_vertiport = object_finder(vertiports, {'id_':aircraft_obj.origin_id})[0]
    destination_vertiport = object_finder(vertiports, {'id_':aircraft_obj.destination_id})[0]
    for i in range(len(origin_vertiport.aircrafts)):
        if aircraft_obj.id_ == origin_vertiport.aircrafts[i].id_:
            to_be_deleted_index = i
            break
    destination_vertiport.aircrafts.append(deepcopy(origin_vertiport.aircrafts[to_be_deleted_index]))
    del origin_vertiport.aircrafts[to_be_deleted_index]
    return vertiports


def find_empty_pad(vertiport: Vertiport) -> (None, int):
    """
    This function finds id_ of an empty pad in a vertiport.
    """
    for pad in vertiport.pads:
        if pad.status.lower() == 'ready':
            return pad.id_
    return None


def demand_status_change_in_aircraft(status: str, aircraft: Aircraft, demands: list) -> list:
    """
    This function change status of all demands in an aircraft.
    """
    for demand_id in aircraft.demands:
        demand_obj = object_finder(demands, {'id_':demand_id})[0]
        demand_obj.status = status
    return demands


def find_maximum_flight_delay_in_aircraft_demands(aircraft: Aircraft, demands: list) -> int:
    """
    This function finds max flight delay in passengers on an aircraft.
    """
    temp = []
    for demand_id in aircraft.demands:
        demand_obj = object_finder(demands, {'id_':demand_id})[0]
        temp.append(demand_obj.delayed_at['flight_delay'])
    if not temp:
        return 0
    return max(temp)


def calc_occupied_capacity(vertiport: Vertiport) -> int:
    """
    This function calculates occupied capacity of vertiport
    """
    occupied_capacity = 0
    for aircraft_obj in vertiport.aircrafts:
        if aircraft_obj.status.lower() in ['ready', 'occupied', 'turnaround', 'landing']:
            occupied_capacity += 1
    return occupied_capacity


def check_vertiport_capacity(aircraft: Aircraft, destination: Vertiport) -> bool:
    """
    This function checks if destination vertiport have enough capacity for aircraft.
    """
    occupied_capacity = calc_occupied_capacity(destination)
    first_come_first_serve_flag = True
    if destination.holding_aircrafts:
        if aircraft.id_ in destination.holding_aircrafts:
            first_come_first_serve_flag = destination.holding_aircrafts.index(aircraft.id_) == 0
        else:
            first_come_first_serve_flag = False
    if occupied_capacity < destination.capacity and first_come_first_serve_flag:
        return True
    else:
        return False


def get_vertiport_max_station_time(max_station_time_data: dict, vertiport: Vertiport, 
                                   aircraft_rate_per_hour: float):
    """
    This function calculates max time on station for aircraft.

    Args:
        max_station_time_data (dict): DESCRIPTION.
        vertiport (Vertiport): DESCRIPTION.
        aircraft_rate_per_hour (float): DESCRIPTION.

    Returns:
        max_station_time (TYPE): DESCRIPTION.

    """
    occupied_capacity = calc_occupied_capacity(vertiport)
    considered_capacity = int(vertiport.capacity - occupied_capacity +1)
    max_station_times = list(max_station_time_data[considered_capacity].values())
    aircraft_rates = list(max_station_time_data[considered_capacity].keys())
    max_station_time = np.interp(aircraft_rate_per_hour, aircraft_rates, max_station_times)
    return max_station_time


def calc_aircraft_arrive_rate_for_vertiport(start_epoch: int, current_epoch: int, 
                                            vertiport: Vertiport, period: int) -> float:
    """
    This funtion calculates aircraft arrive rate to the vertiport in a period 
    before the current epoch.

    Args:
        period (int): period of time that will be the basis to calc rate in seconds.
    """
    
    arriving_spochs = vertiport.arriving_spochs
    temp_epochs = [i for i in arriving_spochs if current_epoch - period < i < current_epoch]
    if current_epoch == start_epoch:
        return 0
    if current_epoch - period < start_epoch:
        rate = (period / (current_epoch - start_epoch))*len(temp_epochs)
    else:
        rate = len(temp_epochs)
    return rate


def determine_time_to_go(mode: str, aircraft: Aircraft, maximum_flight_delay_in_aircraft: int, 
                         maximum_wait_time: int, max_station_time: int) -> bool:
    """
    This function determine that aircraft should leave the vertiport or not (base on mode).
    """
    if aircraft.boarding_time:
        return False
    capacity_flag = aircraft.capacity == len(aircraft.demands)
    wait_flag = maximum_flight_delay_in_aircraft >= maximum_wait_time
    station_time_flag = aircraft.time_on_vertiport > max_station_time
    if aircraft.status.lower() in ['occupied', 'ready']:
        if mode.lower() == 'wait':
            if wait_flag or capacity_flag:
                return True
        elif mode.lower() == 'capacity':
            if capacity_flag:
                return True
        elif mode.lower() == 'capacity_station':
            if capacity_flag or station_time_flag:
                return True
        elif mode.lower() == 'station_wait':
            if capacity_flag or station_time_flag or wait_flag:
                return True
    return False


def determine_suitable_destination(vertiports: list, origin_vertiport: Vertiport) -> (int, None):
    """
    This function finds another vertiport for an aircraft with no destination to 
    with maximum empty capacity.
    """
    empty_capacity_temp = 0
    temp_id_ = None
    for vertiport in vertiports:
        if vertiport.id_ == origin_vertiport.id_:
            continue
        else:
            occupied_capacity = calc_occupied_capacity(vertiport)
            if vertiport.capacity - occupied_capacity > empty_capacity_temp:
                temp_id_ = vertiport.id_
                empty_capacity_temp = vertiport.capacity - occupied_capacity
    return temp_id_


def calc_aircraft_turnaround_time(aircraft: Aircraft, battery_swap_time: int, 
                                  deboard_time_per_passenger: int) -> int:
    """
    This function calculates aircraft turnaround time after landing based on deboard 
    time per passernger, aircraft occupied capacity, and and battery swap time
    """
    time_to_deboard = deboard_time_per_passenger * len(aircraft.demands)
    return max(battery_swap_time, time_to_deboard)


def physics_module(mode: str, time_step: int, vertiports: list, demands: list, 
                   current_epoch: int, landing_occupation_time: int, 
                   takeoff_occupation_time: int, battery_swap_time: int, 
                   board_time_per_passenger: int, deboard_time_per_passenger: int, 
                   holding_duration: int, aircraft_info: dict, max_station_time_data: dict, 
                   maximum_wait_time: int, start_epoch: int) -> (list, list, int):
    """
    This function acts as a manager fot objects. This function moves aircrafts, 
    manage demands, and collect simulation's data.
    All Arguments' description is available in run_simulation module in this file.
    """
    msg_list = []
    super_holding_violation = False
    for demand in demands:
        if demand.status.lower() == 'scheduled':
            if 'wait' in mode.lower() and demand.delayed_at['flight_delay'] > maximum_wait_time:
                demand.status = 'unsuccessful'
            if current_epoch > demand.start_time:
                vertiport_obj = object_finder(vertiports, {'id_':demand.origin_id})[0]
                find_aircraft = False
                for aircraft in vertiport_obj.aircrafts:
                    if aircraft.destination_id == demand.destination_id and len(aircraft.demands) < aircraft.capacity and aircraft.status.lower() in ['ready', 'occupied']:
                        aircraft.demands.append(demand.id_)
                        aircraft.boarding_time += board_time_per_passenger
                        find_aircraft = True
                        break
                if not find_aircraft:
                    for aircraft in vertiport_obj.aircrafts:
                        if aircraft.status == 'ready':
                            aircraft.origin_id = demand.origin_id
                            aircraft.destination_id = demand.destination_id
                            aircraft.demands.append(demand.id_)
                            aircraft.status = 'occupied'
                            aircraft.boarding_time += board_time_per_passenger
                            find_aircraft = True
                            break
                if find_aircraft:
                    demand.status = 'in aircraft'
                    demand.carrier_kind = 'aircraft'
                    demand.carrier_id = aircraft.id_
                else:
                    demand.delayed_at['finding_aircraft'] += 1
        if demand.status.lower() in ['scheduled', 'in aircraft']:
            demand.delayed_at['flight_delay'] = max(0, current_epoch - demand.start_time)
    number_of_aircrafts = 0
    holding_violations = 0
    for vertiport in vertiports:
        occupied_capacity = calc_occupied_capacity(vertiport)
        aircraft_rate_per_hour = calc_aircraft_arrive_rate_for_vertiport(start_epoch, current_epoch, vertiport, 3600)
        if aircraft_rate_per_hour > vertiport.capacity - occupied_capacity:
            max_station_time = get_vertiport_max_station_time(max_station_time_data, vertiport, aircraft_rate_per_hour)
        else:
            max_station_time = np.inf
        number_of_aircrafts += len(vertiport.aircrafts)
        for aircraft in vertiport.aircrafts:
            if aircraft.boarding_time:
                aircraft.boarding_time -= time_step
            if aircraft.holding_violation:
                holding_violations += 1
            if aircraft.status.lower() in ['ready', 'occupied', 'turnaround']:
                aircraft.time_on_vertiport += 1
            maximum_flight_delay_in_aircraft = find_maximum_flight_delay_in_aircraft_demands(aircraft, demands)
            time_to_go_flag = determine_time_to_go(mode, aircraft, maximum_flight_delay_in_aircraft, maximum_wait_time, max_station_time)
            if not time_to_go_flag and maximum_flight_delay_in_aircraft > 2* maximum_wait_time:
                time_to_go_flag = determine_time_to_go(mode, aircraft, maximum_flight_delay_in_aircraft, maximum_wait_time, max_station_time)
            if time_to_go_flag:
                pad_id = find_empty_pad(vertiport)
                if pad_id is not None:
                    if aircraft.destination_id is None:
                        aircraft.origin_id = vertiport.id_
                        aircraft.destination_id = determine_suitable_destination(vertiports, vertiport)
                    aircraft.pad_id = pad_id
                    pad_obj = object_finder(vertiport.pads, {'id_':pad_id})[0]
                    flight_schedule = create_flight_schedule_for_starting_aircraft(aircraft, aircraft_info, \
                                                                                   current_epoch, takeoff_occupation_time, vertiports)
                    aircraft.schedule_list += flight_schedule
                    aircraft.status = pad_obj.status = 'takeoff'
                    demands = demand_status_change_in_aircraft('airborne', aircraft, demands)
                    takeoff_schedule = find_object_schedule_by_type(aircraft, 'takeoff')
                else:
                    for demand_id in aircraft.demands:
                        demand_obj = object_finder(demands, {'id_':demand_id})[0]
                        demand_obj.delayed_at['before_takeoff'] += 1
            elif aircraft.status.lower() == 'takeoff':
                aircraft.time_on_vertiport = 0
                takeoff_schedule = find_object_schedule_by_type(aircraft, 'takeoff')
                if current_epoch >= takeoff_schedule['t_f']:
                    pad_obj = object_finder(vertiport.pads, {'id_':aircraft.pad_id})[0]
                    aircraft.status = 'climb'
                    pad_obj.status = 'ready'
                    aircraft.pad_id = None
            elif aircraft.status.lower() == 'climb':
                climb_schedule = find_object_schedule_by_type(aircraft, 'climb')
                if current_epoch >= climb_schedule['t_f']:
                    aircraft.status = 'cruise'
            elif aircraft.status.lower() == 'cruise':
                cruise_schedule = find_object_schedule_by_type(aircraft, 'cruise')
                if current_epoch >= cruise_schedule['t_f']:
                    destination_obj = object_finder(vertiports, {'id_':aircraft.destination_id})[0]
                    destination_obj.arriving_aircrafts.append({'time':current_epoch, 'id_':aircraft.id_})
                    destination_obj.arriving_spochs.append(current_epoch)
                    pad_id = find_empty_pad(destination_obj)
                    vertiport_state = check_vertiport_capacity(aircraft, destination_obj) 
                    if pad_id is not None and vertiport_state:
                        aircraft.pad_id = pad_id
                        new_schedule = create_flight_schedule_for_landing_aircraft(aircraft, current_epoch, aircraft_info, landing_occupation_time, vertiports)
                        aircraft.schedule_list += new_schedule
                        pad_obj = object_finder(destination_obj.pads, {'id_':pad_id})[0]
                        pad_obj.status = aircraft.status = 'landing'
                        vertiports = move_aircaft_obj_to_destination_airport(aircraft, vertiports)
                    else:
                        destination_obj.holding_aircrafts.append(aircraft.id_)
                        aircraft.schedule_list += [{'t_0':current_epoch, 't_f': current_epoch + holding_duration, 
                                                      'type':'holding', 'distance':0}]
                        aircraft.status = 'holding'
            elif aircraft.status.lower() == 'holding':
                holding_schedule = find_object_schedule_by_type(aircraft, 'holding')
                if current_epoch >= holding_schedule['t_f']:
                    aircraft.holding_violation = True
                    if (current_epoch - holding_schedule['t_f']) > 2 * (holding_schedule['t_f'] -  holding_schedule['t_0']):
                        super_holding_violation = True
                for demand_id in aircraft.demands:
                    demand_obj = object_finder(demands, {'id_':demand_id})[0]
                    demand_obj.delayed_at['before_landing'] += 1
                destination_obj = object_finder(vertiports, {'id_':aircraft.destination_id})[0]
                vertiport_state = check_vertiport_capacity(aircraft, destination_obj) 
                pad_id = find_empty_pad(destination_obj)
                if pad_id is not None and vertiport_state:
                    del destination_obj.holding_aircrafts[destination_obj.holding_aircrafts.index(aircraft.id_)]
                    aircraft.pad_id = pad_id
                    holding_schedule['t_f'] = current_epoch
                    new_schedule = create_flight_schedule_for_landing_aircraft(aircraft, current_epoch, aircraft_info, landing_occupation_time, vertiports)
                    aircraft.schedule_list += new_schedule
                    pad_obj = object_finder(destination_obj.pads, {'id_':pad_id})[0]
                    pad_obj.status = aircraft.status = 'landing'
                    vertiports = move_aircaft_obj_to_destination_airport(aircraft, vertiports)
            elif aircraft.status.lower() == 'landing':
                landing_schedule = find_object_schedule_by_type(aircraft, 'landing')
                if current_epoch >= landing_schedule['t_f']:
                    destination_obj = object_finder(vertiports, {'id_':aircraft.destination_id})[0]
                    pad_obj = object_finder(destination_obj.pads, {'id_':aircraft.pad_id})[0]
                    aircraft.pad_id = None
                    pad_obj.status = 'ready'
                    aircraft.status = 'turnaround'
                    turnaround_time = calc_aircraft_turnaround_time(aircraft, battery_swap_time, deboard_time_per_passenger)
                    aircraft.schedule_list += [{'t_0':current_epoch, 't_f': current_epoch + turnaround_time, 
                                                'type':'turnaround', 'distance':0}]
                    demands = demand_status_change_in_aircraft('satisfied', aircraft, demands)
            elif aircraft.status.lower() == 'turnaround':
                turnaround_schedule = find_object_schedule_by_type(aircraft, 'turnaround')
                if current_epoch >= turnaround_schedule['t_f']:
                    takeoff_schedule = find_object_schedule_by_type(aircraft, 'takeoff')
                    aircraft.flight_hours += (turnaround_schedule['t_0'] - takeoff_schedule['t_0'])/3600
                    aircraft.status = 'ready'
                    aircraft.schedule_list = []
                    aircraft.demands = []
                    aircraft.destination_id = None
                    aircraft.origin_id = None
                    
    if holding_violations >= 0.1 * number_of_aircrafts:
        msg_list.append('too much holding violations')
    if super_holding_violation:
        msg_list.append("Too long holding violation")
    return vertiports, demands, msg_list
        
                    

def run_simulation(mode: str, vertiports: list, demands: list, landing_occupation_time: int, 
                   takeoff_occupation_time: int, battery_swap_time: int, 
                   board_time_per_passenger: int, deboard_time_per_passenger: int, \
                   holding_duration: int, aircraft_info: dict, max_station_time_data: dict, 
                   maximum_wait_time: int, start_time: int, end_time: int) -> (list, list, list, int):
    """
    This function runs a simulation for a vertiport network between "start_time" and "end_time".
    Having a list of demand that is based on vertiport objects and their arrival time is between 
    start_time and end_time is necessary for this function to work properly.
    Time step of simulation can be changed in the body of this function.
    
    Args:
        mode (str): is one of these four modes to determine when an aircraft should leave the vertiport:
                        1- capacity method: "capacity"
                        2- capacity method with max time on station: "capacity_station"
                        3- wait time method: "wait"
                        4- wait time method with max time on station: "station_wait"
        vertiports (list): list of vertiport objects.
        demands (list): list of demand objects.
        landing_occupation_time (int): required time for an aircraft to descent, land and to leave a 
                                       landing pad in seconds.
        takeoff_occupation_time (int): required time for an aircraft to finish its takeoff sequences 
                                        and leave the landing pad in seconds.
        battery_swap_time (int): required time to change an aircraft's battery in seconds.
        board_time_per_passenger (int): required time to board a passenger in seconds.
        deboard_time_per_passenger (int): required time to deboard a passenger in seconds.
        holding_duration (int): maximum time for holding (before landing) in seconds.
        aircraft_info (dict): aircraft info dict that contains its capacity, cruise speed and etc. .
        max_station_time_data (dict): data .
        maximum_wait_time (int):  Max wait time for passengers for an aircraft.
        start_time (int): start time of simulation.
        end_time (int): end time of simulation.

    Returns:
        vertiports (dict): list of vertiport objects after simulation.
        demands (int):  list of demand objects after simulation.
        msg_list (int): list of messages. if there is an error in the simulation, 
                        a message will appear in this list.
        current_epoch (int): last epoch of simulation.

    """
    
    
    current_epoch = start_time
    time_step = 30
    while current_epoch <= end_time:
        vertiports, demands, msg_list = physics_module(mode, time_step, vertiports, demands, current_epoch, landing_occupation_time, takeoff_occupation_time, battery_swap_time, board_time_per_passenger, deboard_time_per_passenger, \
                                                           holding_duration, aircraft_info, max_station_time_data, maximum_wait_time, start_time)
          
        if msg_list:
            break
        current_epoch += time_step
    return vertiports, demands, msg_list, current_epoch
        