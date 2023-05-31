import os
import pandas as pd
import pickle as pk

out_data = {}
root_path = os.getcwd() + "\\new_data.xlsx"
excel_data = pd.ExcelFile(root_path)
sheet_names = excel_data.sheet_names
# excel_data = pd.read_excel(root_path, sheet_name=sheet_names[0])
# data_dict = excel_data.to_dict(orient='dict')
for sheet_name in sheet_names:
    out_data[int(sheet_name)] = {}
    excel_data = pd.read_excel(root_path, sheet_name=sheet_name)
    data_dict = excel_data.to_dict(orient='dict')
    aircraft_numbers = data_dict['aircraft_number']
    turnaround_times = data_dict['turnaround_time']
    for i in turnaround_times:
        out_data[int(sheet_name)][aircraft_numbers[i]] = turnaround_times[i]
        # out_data[int(sheet_name)]['turnaround_time'].append(turnaround_times[i])
pk.dump(out_data,open('max_station_time.p','wb'))