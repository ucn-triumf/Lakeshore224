# Frontend to readout the lakeshore224 as a MIDAS equipment 
# Derek Fujimoto
# Sep 2026

import midas
import midas.frontend
from Lakeshore224 import Lakeshore224
import time


class LakeshoreEquipment(midas.frontend.EquipmentBase):
    """
    """
    def __init__(self, client):
        # The name of our equipment. This name will be used on the midas status
        # page, and our info will appear in /Equipment/MyPeriodicEquipment in
        # the ODB.
        equip_name = "GradientLakeshore"

        default_common = midas.frontend.InitialEquipmentCommon()
        default_common.equip_type = midas.EQ_PERIODIC
        default_common.buffer_name = "SYSTEM"
        default_common.trigger_mask = 0
        default_common.event_id = 1
        default_common.period_ms = 1000
        default_common.read_when = midas.RO_RUNNING
        default_common.log_history = 10

        midas.frontend.EquipmentBase.__init__(self, client, equip_name, default_common)

        # connect to lakeshore
        self.lakeshore = Lakeshore224("192.168.0.0") # TODO: fix this

        # set ODB settings
        client.odb_set(f'{self.odb_settings_dir}/channel_names', 
                       ['A', 'B', 
                        'C1', 'C2', 'C3', 'C4', 'C5', 
                        'D1', 'D2', 'D3', 'D4', 'D5'])

        # You can set the status of the equipment (appears in the midas status page)
        self.set_status("Initialized")

    def readout_func(self):

        # read data and record the time - always read all channels
        temp = self.lakeshore.get_tempK('0')

        # set variables
        self.client.odb_set(f'{self.odb_variables_dir}/temp_K', temp)
        
class LakeshoreFrontend(midas.frontend.FrontendBase):
    """
    A frontend contains a collection of equipment.
    You can access self.client to access the ODB etc (see `midas.client.MidasClient`).
    """
    def __init__(self):
        # You must call __init__ from the base class.
        midas.frontend.FrontendBase.__init__(self, "GradientLakeshoreFE")

        # You can add equipment at any time before you call `run()`, but doing
        # it in __init__() seems logical.
        self.add_equipment(LakeshoreEquipment(self.client))

    def __exit__(self, type, value, traceback):

        # close all connections to lakeshore devices
        for equip in self.equipment.values():
            equip.lakeshore.close()

        # continue exiting via base class
        midas.frontend.FrontendBase.__exit__(self, type, value, traceback)

if __name__ == "__main__":
    # The main executable is very simple - just create the frontend object,
    # and call run() on it.
    with LakeshoreFrontend() as fe:
        fe.run()