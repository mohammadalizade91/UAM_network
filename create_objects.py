import os
import pandas as pd
import numpy as np
import json
from objects import Vertiport, Pad, Aircraft, Demand
from copy import deepcopy
# from classes.objects import pad
def create_vertiport(file_name: str, aircraft_info: dict) -> (list, int):
    """
    This function creates vertiport objects alongside their aircraft and pads.

    Args:
        file_name (str): vertiport file name that contains its location, pads and number of stands.
        aircraft_info (dict): aircraft info dict that contains its capacity, cruise speed and etc. .

    Returns:
        vertiport_objects (list): list of built vertiport objects.
        last_id (int): last objects id, to be used for creating other objects.

    """
    i = 1
    root_path = os.getcwd() + f"\\{file_name}.xlsx"
    excel_data = pd.ExcelFile(root_path)
    sheet_names = excel_data.sheet_names
    excel_data = pd.read_excel(root_path, sheet_name=sheet_names[0])
    # excel_data = excel_data.replace(np.nan, 'None')
    data_dict = excel_data.to_dict(orient='dict')
    vertiport_objects = []
    vertiport_created = False
    
    for index in data_dict['Name']:
        
        if type(data_dict['Name'][index]) == str: # row contains new vertiport info
            
            if vertiport_created: # finalizing last airport object
                vertiport_obj.aircrafts = aircrafts
                vertiport_obj.pads = pads
                vertiport_objects.append(deepcopy(vertiport_obj))
            # building a raw vertiport with no pad and no aircraft
            vertiport_obj = Vertiport(i, [], [], json.loads(data_dict['Position'][index]), data_dict['Name'][index], data_dict['Capacity'][index])
            vertiport_created = True
            pads = []
            aircrafts = []
            i += 1
            if not np.isnan(data_dict['PadDirection'][index]):
                pad_obj = Pad(i, data_dict['Pad'][index] if type(data_dict['Pad'][index]) == str else 'pad with no name')
                pads.append(pad_obj)
                i += 1
            if not np.isnan(data_dict['AircraftNumber'][index]):
                for n in range(int(data_dict['AircraftNumber'][index])):
                    aircrafts.append(Aircraft(i, data_dict['AircraftID'][index], None, 'ready', [], aircraft_info[int(data_dict['AircraftID'][index])]['capacity']))
                    i += 1
        elif np.isnan(data_dict['Name'][index]):
            if not np.isnan(data_dict['PadDirection'][index]):
                pad_obj = Pad(i, data_dict['Pad'][index] if type(data_dict['Pad'][index]) == str else 'pad with no name')
                pads.append(pad_obj)
                i += 1
            if not np.isnan(data_dict['AircraftNumber'][index]):
                for n in range(data_dict['AircraftNumber'][index]):
                    aircrafts.append(Aircraft(i, int(data_dict['AircraftID'][index]), None, 'ready', [], aircraft_info[int(data_dict['AircraftID'][index])]['capacity']))
                    i += 1
    
    vertiport_obj.pads = pads
    vertiport_obj.aircrafts = aircrafts
    vertiport_objects.append(deepcopy(vertiport_obj))
    last_id = i
    
    return vertiport_objects, last_id


def create_demands(demand_schedule_data: dict, last_id: int) -> (list, int):
    """
    This function creates demand objects demand_schedule_data

    Args:
        demand_schedule_data (dict): a dictionary that contains every damand's 
            start time and its origin and destination.
        last_id (int): previous last objects id, to be used for creating other objects.

    Returns:
        demands (list): list of built demand objects.
        last_id (int): last objects id, to be used for creating other objects.

    """
    demands = []
    
    for i in range(len(demand_schedule_data['demand_start_time'])):
        demands.append(Demand(last_id, demand_schedule_data['origin_id'][i], demand_schedule_data['destination_id'][i], 
                              demand_schedule_data['demand_start_time'][i]))
        last_id += 1
    
    return demands, last_id