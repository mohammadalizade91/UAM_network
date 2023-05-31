import numpy as np


class Vertiport:
    def __init__(self, id_, pads, aircrafts, position, name, capacity):
        self.id_ = id_
        self.pads = pads
        self.position = position
        self.name = name
        self.aircrafts = aircrafts
        self.capacity = capacity
        self.holding_aircrafts = []
        self.arriving_aircrafts = []
        self.arriving_spochs = []
        
        
class Pad:
    def __init__(self, id_, name):
        self.id_ = id_
        self.name = name
        self.status = 'ready'
        self.schedule_list = []
        self.occupied_aircraft = None


class Aircraft:
    def __init__(self, id_, db_id, destination_id, status, schedule_list, capacity):
        self.id_ = id_
        self.destination_id = None
        self.origin_id = None
        self.status = status
        self.schedule_list = schedule_list
        self.db_id = db_id
        self.demands = []
        self.capacity = capacity
        self.pad_id = None
        self.flight_hours = 0
        self.holding_violation = False
        self.time_on_vertiport = 0
        self.boarding_time = 0
        

class Demand:
    def __init__(self, id_, origin_id, destiation_id, start_time):
        self.id_ = id_
        self.origin_id = origin_id
        self.destination_id = destiation_id
        self.start_time = start_time
        self.carrier_kind = None
        self.carrier_id = None
        self.status = 'scheduled'
        self.status_list = []
        self.delayed_at = {'finding_aircraft': 0, 'before_takeoff':0, 'before_turnaround':0, 'before_landing':0, 'flight_delay':0}
        self.takeoff_runway = None
        self.landing_runway = None
        self.total_distance = None