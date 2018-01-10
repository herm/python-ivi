"""

Python Interchangeable Virtual Instrument Library

Copyright (c) 2017 Hermann Kraus & Tobias Grünbaum

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""

from .. import ivi
from .. import dcpwr

class easydriver0520(dcpwr.Base, dcpwr.Measurement, ivi.Driver):
    """CAENels Easy-Driver constant current power supply driver."""
    #NOTE: Currently all writes have to include the termination character because ivi ignores it while writing 
    # (incorrectly uses write_raw() for write() calls. 
    def __init__(self, *args, **kwargs):
        self.__dict__.setdefault('_instrument_id', '0520')
        super(easydriver0520, self).__init__(*args, **kwargs)

        self._output_count = 1

        self._output_spec = [
            {
                'range': {
                    'P5I': (20, 5.1),
                },
                'ovp_max': 0,
                'voltage_max': 20,
                'current_max': 5.1
            }
        ]

        self._identity_description = "Easy-Driver 0520 driver"
        self._identity_identifier = ""
        self._identity_revision = ""
        self._identity_vendor = "CAENels"
        self._identity_instrument_manufacturer = "CAENels"
        self._identity_instrument_model = "Easy-Driver 0520"
        self._identity_instrument_firmware_revision = ""
        self._identity_specification_major_version = 3
        self._identity_specification_minor_version = 0
        self._identity_supported_instrument_models = ['PSU']

        self._init_outputs()

    def _initialize(self, resource = None, id_query = False, reset = False, **keywargs):
        "Opens an I/O session to the instrument."

        super(easydriver0520, self)._initialize(resource, id_query, reset, **keywargs)

        if self._interface:
            self._interface.instrument.read_termination = '\r'
            self._interface.instrument.write_termination = '\r'
        
        # interface clear
        if not self._driver_operation_simulate:
            try:
                return self._interface.clear()
            except (AttributeError, NotImplementedError):
                pass

        # check ID
        if id_query and not self._driver_operation_simulate:
            id = self.identity.instrument_model
            id_check = self._instrument_id
            id_short = id[:len(id_check)]
            if id_short != id_check:
                raise Exception("Instrument ID mismatch, expecting %s, got %s", id_check, id_short)
        # reset
        if reset:
            self.utility_reset()

    def _utility_disable(self):
        pass

    def _utility_lock_object(self):
        pass

    def _utility_unlock_object(self):
        pass

    def _init_outputs(self):
        try:
            super(easydriver0520, self)._init_outputs()
        except AttributeError:
            pass

        self._output_current_limit = list()
        self._output_current_limit_behavior = list()
        self._output_enabled = list()
        self._output_ovp_enabled = list()
        self._output_ovp_limit = list()
        self._output_voltage_level = list()
        self._output_trigger_source = list()
        self._output_trigger_delay = list()
        self._output_mode = list()
        for i in range(self._output_count):
            self._output_current_limit.append(0)
            self._output_current_limit_behavior.append('regulate')
            self._output_enabled.append(False)
            self._output_ovp_enabled.append(True)
            self._output_ovp_limit.append(0)
            self._output_voltage_level.append(0)
            self._output_trigger_source.append('bus')
            self._output_trigger_delay.append(0)
            self._output_mode.append('current')
    
    def _ask_with_ak(self, value, ak_value='#AK'):
        print("Ask: {!r}".format(value))
        response = self._ask(value)
        if not response.startswith(ak_value):
            raise ivi.UnexpectedResponseException(
                "In repsonse to command {!r}: Expected to receive {!r} got {!r}".format(
                    value, ak_value, response)
                )
        return response

    def _get_output_current_limit(self, index):
        index = ivi.get_index(self._output_name, index)
        if not self._driver_operation_simulate and not self._get_cache_valid(index=index):
            # bit 7: bypass
            response = self._ask_with_ak('FDB:80:0\r', '#FDB')
            #Response: #FDB:status:setpoint:actual
            self._output_current_limit[index] = float(response.split(':')[2])
            self._set_cache_valid(index=index)
        return self._output_current_limit[index]

    def _set_output_current_limit(self, index, value):
        index = ivi.get_index(self._output_name, index)
        value = float(value)
        if abs(value) > self._output_spec[index]['current_max']:
            raise ivi.OutOfRangeException()
        if not self._driver_operation_simulate and self._get_output_enabled(index):
            self._ask_with_ak('MWI:%e\r' % value)
        self._output_current_limit[index] = value
        self._set_cache_valid(index=index)


    def _get_output_voltage_level(self, index):
        index = ivi.get_index(self._output_name, index)
        self._output_voltage_level[index] = self._output_spec[index]['voltage_max']
        return self._output_voltage_level[index]

    def _set_output_voltage_level(self, index, value):
        if value > self._output_spec[index]['voltage_max']:
            raise ivi.OperationNotSupportedException("Device does not support setting voltage")

    def _set_output_current_limit_behavior(self, index, value):
        if value != 'regulate':
            raise ivi.ValueNotSupportedException()

    def _get_output_enabled(self, index):
        index = ivi.get_index(self._output_name, index)
        if not self._driver_operation_simulate and not self._get_cache_valid(index=index):
            self._output_enabled[index] = bool(int(self._ask_with_ak("MST\r", '#MST').split(':')[1]) & 1)
            self._set_cache_valid(index=index)
        return self._output_enabled[index]

    def _set_output_enabled(self, index, value):
        index = ivi.get_index(self._output_name, index)
        value = bool(value)
        if not self._driver_operation_simulate:
            if value:
                self._ask_with_ak("MON\r")
                self._output_enabled[index] = value
                self._set_output_current_limit(index, self._output_current_limit[index])
            else:
                self._ask_with_ak("MOFF\r")
        self._output_enabled[index] = value
        self._set_cache_valid(index=index)

    def _output_query_current_limit_max(self, index, voltage_level):
        index = ivi.get_index(self._output_name, index)
        if abs(voltage_level) > self._output_spec[index]['voltage_max']:
            raise ivi.OutOfRangeException()
        return self._output_spec[index]['current_max']

    def _output_query_voltage_level_max(self, index, current_limit):
        index = ivi.get_index(self._output_name, index)
        if abs(current_limit) > self._output_spec[index]['current_max']:
            raise ivi.OutOfRangeException()
        return self._output_spec[index]['voltage_max']

    def _output_measure(self, index, type):
        index = ivi.get_index(self._output_name, index)
        if type == 'voltage':
            if not self._driver_operation_simulate:
                return float(self._ask_with_ak('MRV\r', '#MRV').split(':')[1])
        elif type == 'current':
            if not self._driver_operation_simulate:
                return float(self._ask_with_ak('MRI\r', '#MRI').split(':')[1])
        raise ivi.ValueNotSupportedException()

    def _output_query_output_state(self, index, state):
        raise ivi.ValueNotSupportedException()

    def _load_id_string(self):
        if self._driver_operation_simulate:
            self._identity_instrument_model = "Not available while simulating"
            self._identity_instrument_firmware_revision = "Not available while simulating"
        else:
            raw = self._ask("MVER\r").split(':')
            self._identity_instrument_model = raw[2]
            self._identity_instrument_firmware_revision = raw[3]
            self._set_cache_valid(True, 'identity_instrument_model')
            self._set_cache_valid(True, 'identity_instrument_firmware_revision')

    def _get_identity_instrument_model(self):
        if not self._get_cache_valid():
            self._load_id_string()
        return self._identity_instrument_model

    def _get_identity_instrument_serial_number(self):
        if not self._get_cache_valid():
            self._load_id_string()
        return self._identity_instrument_serial_number

    def _get_identity_instrument_firmware_revision(self):
        if not self._get_cache_valid():
            self._load_id_string()
        return self._identity_instrument_firmware_revision

    def _utility_reset(self):
        if not self._driver_operation_simulate:
            self._ask_with_ak("MRESET\r")
            self._clear()
            self.driver_operation.invalidate_all_attributes()