import numpy as np
from datetime import datetime


def create_schedule(vertiports: list, demand_number: int, start_time: (int, float), end_time: (int, float)) -> dict:
    """
    This function creates demand schedule data from "start_time" to "end_time"
    for a number of demands with each of them want to go from a vertiport to another

    Args:
        vertiports (list): a list of vertiport objects.
        demand_number (int): total number of demands.
        start_time: start of simulation and first interval of demand production in epoch.
        end_time: last interval of demand production in epoch (simulation will continue for one 
                                                               hour after the end_time).

    Returns:
        data (dict): demand schedule data.

    """
    duration = end_time-start_time
    demand_start_time_list = []
    origin_id_list = []
    destination_id_list = [] 
    
    for demand in range(demand_number):
        origin_index = int(np.random.rand()*len(vertiports))
        destination_index = int(np.random.rand()*len(vertiports))
        # avoiding equal origin and destination
        while destination_index == origin_index:
            destination_index = int(np.random.rand()*len(vertiports))
        
        origin_id = vertiports[origin_index].id_
        destination_id = vertiports[destination_index].id_
        demand_time = int(np.random.rand() * duration + start_time)
        demand_start_time_list.append(demand_time)
        origin_id_list.append(origin_id)
        destination_id_list.append(destination_id)
    
    origin_id_list = [x for _,x in sorted(zip(demand_start_time_list,origin_id_list))]
    destination_id_list = [x for _,x in sorted(zip(demand_start_time_list,destination_id_list))]
    demand_start_time_list.sort()
    datetime_list = [datetime.fromtimestamp(i).strftime('%Y-%m-%d %H:%M:%S') for i in demand_start_time_list]
    
    data = {'demand_start_time':demand_start_time_list,
            'origin_id': origin_id_list,
            'destination_id': destination_id_list,
            'datetime':datetime_list}
    
    return data