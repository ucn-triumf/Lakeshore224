# Frontend to readout the lakeshore224 as a MIDAS equipment 
# Derek Fujimoto
# Sep 2026

import midas
import midas.frontend
import midas.event
import time
from Lakeshore224 import Lakeshore224

class LakeshoreEquipment(midas.frontend.EquipmentBase):
    """Periodic equipment which reads all 12 Lakeshore224 inputs into one bank.

    Attributes:
        lakeshore (Lakeshore224): open connection to the temperature monitor.
        read_failed (bool): whether the last readout raised, used to avoid
            rewriting the equipment status to the ODB on every cycle.
    """

    BANK_NAME = 'GRDT'

    def __init__(self, client):
        # The name of our equipment. This name will be used on the midas status
        # page, and our info will appear in /Equipment/MyPeriodicEquipment in
        # the ODB.
        equip_name = "GradientTemps"

        default_common = midas.frontend.InitialEquipmentCommon()
        default_common.equip_type = midas.EQ_PERIODIC
        default_common.read_when = midas.RO_ALWAYS
        default_common.buffer_name = "SYSTEM"
        default_common.trigger_mask = 0
        default_common.event_id = 1
        default_common.period_ms = 1000
        default_common.log_history = 10

        # Defaults for /Equipment/<name>/Settings. The base class applies these
        # with update_structure_only=True, so values edited in the ODB survive a
        # restart. mlogger labels the history tags of the variable <var> using
        # the key "Names <var>", hence the bank name TEMP below.
        default_settings = {'ip_address': 'lakeshore01.ucn.triumf.ca',
                            f'Names {self.BANK_NAME}': ['A', 'B',
                                                        'C1', 'C2', 'C3', 'C4', 'C5',
                                                        'D1', 'D2', 'D3', 'D4', 'D5'],
                            }

        midas.frontend.EquipmentBase.__init__(self, client, equip_name,
                                             default_common, default_settings)

        # connect to lakeshore - self.settings is populated by the base class
        try:
            self.lakeshore = Lakeshore224(self.settings['ip_address'])
        except Exception as err:
            self.client.msg(f'{equip_name}: unable to connect to Lakeshore', is_error=True)
            raise err from None
        self.read_failed = False
        self.tlast = time.monotonic()

        # You can set the status of the equipment (appears in the midas status page)
        self.set_status("Running")

    def readout_func(self):
        """Read every channel and package the temperatures as a midas event.

        Returns:
            midas.event.Event|None: event with a single TID_DOUBLE bank holding
                the 12 channel temperatures in K, or None if the read failed.
        """

        # read data - always read all channels ('0' is the read-all input)
        try:
            temp = self.lakeshore.get_tempK('0')

        # OSError covers socket failures; ValueError covers an unparseable
        # response. Neither may propagate: FrontendBase.run() has no error
        # handling, so an exception here kills the frontend.
        except (OSError, ValueError, ConnectionError) as err:
            if not self.read_failed:
                self.read_failed = True
                self.set_status(f"Read failed: {err}", "redLight")
                self.client.msg(f"Read failed: {err}", is_error=True)
            return None

        # recovered from an earlier failure
        else:
            if self.read_failed:
                self.read_failed = False
                self.set_status("Running")

        # bank names must be exactly 4 characters
        event = midas.event.Event()
        event.create_bank(self.BANK_NAME, midas.TID_DOUBLE, temp)

        return event

class LakeshoreFrontend(midas.frontend.FrontendBase):
    """
    A frontend contains a collection of equipment.
    You can access self.client to access the ODB etc (see `midas.client.MidasClient`).
    """
    def __init__(self):
        # You must call __init__ from the base class.
        midas.frontend.FrontendBase.__init__(self, "GradientTempsFE")

        # You can add equipment at any time before you call `run()`, but doing
        # it in __init__() seems logical.
        self.add_equipment(LakeshoreEquipment(self.client))

    def frontend_exit(self):
        """Close all connections to lakeshore devices on the way out."""
        for equip in self.equipment.values():
            equip.lakeshore.close()

if __name__ == "__main__":
    # The main executable is very simple - just create the frontend object,
    # and call run() on it.
    with LakeshoreFrontend() as fe:
        fe.run()
