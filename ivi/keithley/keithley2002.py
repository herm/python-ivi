"""

Python Interchangeable Virtual Instrument Library

Copyright (c) 2012-2014 Alex Forencich

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

from .. import scpi
from .. import extra

class keithley2002(scpi.dmm.Base,
                scpi.dmm.SoftwareTrigger,
                scpi.dmm.DisplayString,
                scpi.dmm.ApertureNPLC,
                extra.dmm.VoltageApertureNPLC,
                extra.dmm.CurrentApertureNPLC,
                extra.dmm.TemperatureApertureNPLC,
                extra.dmm.ResistanceApertureNPLC):
    "Keithley 2002 IVI DMM driver"

    def __init__(self, *args, **kwargs):
        self.__dict__.setdefault('_instrument_id', '34401A')

        super(keithley2002, self).__init__(*args, **kwargs)

        self._num_windows = 2
        self._text_clear_supported = False

        self._identity_description = "Keithley 2002 IVI DMM driver"
        self._identity_identifier = ""
        self._identity_revision = ""
        self._identity_vendor = ""
        self._identity_instrument_manufacturer = "Keithley"
        self._identity_instrument_model = ""
        self._identity_instrument_firmware_revision = ""
        self._identity_specification_major_version = 4
        self._identity_specification_minor_version = 1
        self._identity_supported_instrument_models = ['2002']


    def _initialize(self, resource = None, id_query = False, reset = False, **keywargs):
        "Opens an I/O session to the instrument."

        super(keithley2002, self)._initialize(resource, id_query, reset, **keywargs)

        # interface clear
        if not self._driver_operation_simulate:
            self._clear()

        # check ID
        if id_query and not self._driver_operation_simulate:
            id = self.identity.instrument_model
            id_check = self._instrument_id
            id_short = id[:len(id_check)]
            if id_short != id_check:
                raise Exception("Instrument ID mismatch, expecting %s, got %s", id_check, id_short)

        # reset
        if reset:
            self.utility.reset()
        else:
            #Make sure tigger subsystem is in the expected state
            # Single trigger
            self._write("init:cont off")
            self._write(":arm:layer1:count 1")
            self._write(":arm:layer2:count 1")
            self._write(":trig:seq1:count 1")
            self._write(":arm:layer1:source imm")
            self._write(":arm:layer2:source imm")
            self._write(":trig:seq1:source imm")
            self._write("abort")

        # Disable filter
        self._write(":volt:dc:aver 0") #TODO: Other ranges

        # Configure output format so we are able to parse instrument responses
        # Only return reading and no status outputs/timestamps
        self._write("form:elem read")
        # Ascii data...
        self._write("form:data asc")
        # ...with high precision
        self._write("form:exp hpr")


    def _write(self, data):
        print("Writing", data)
        super(keithley2002, self)._write(data)
        print(self._utility_error_query())

    def _ask(self, data):
        result = super(keithley2002, self)._ask(data)
        if "error" not in data:
            print("Querying %s => %s | %s" % (data, result, self._utility_error_query()))
        return result








