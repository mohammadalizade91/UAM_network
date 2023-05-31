from run_main import run_main
mode = 'station_wait'
cruise_speed = 120
capacity = 12
vertiport_file_name = 'vertiport_info_144_12'
start_demand = 800
end_demand = 820
demand_step = 20
maximum_fligh_delay = 1200

run_main(mode, cruise_speed, capacity, vertiport_file_name, start_demand, end_demand, demand_step, maximum_fligh_delay)