import time

# OpenHTF
# Import OpenHTF as htf since we will be using it a lot.
import openhtf as htf

# Outputs
from openhtf.output.callbacks.console_summary import ConsoleSummary
from openhtf.output.callbacks.json_factory import OutputToJSON
from openhtf.output.servers.station_server import StationServer
from openhtf.output.web_gui import web_launcher

# Plugs
from openhtf.plugs import BasePlug
from openhtf.plugs import user_input

# Utils
from openhtf.util import validators
from openhtf.util import units
from openhtf.util import conf

# InstrumentPy devices
from instrumentpy.common.tcpip_device import TCPIPDevice
from instrumentpy.platform.next import TS3


class TS3Plug(BasePlug, TS3):
    ip_address = None

    def __init__(self) -> None:
        assert self.ip_address is not None

        tcp_ip_device = TCPIPDevice(self.ip_address, 50020)

        # Clever trick in Python:
        # Multiple inheritance, so specifying device will pass it on to TS3.
        super().__init__(device=tcp_ip_device)


class TS3Interface(TS3Plug):
    ip_address = "192.168.0.101"


@htf.measures(
    htf.Measurement("DIGITAL_OUT_1")
    .with_validator(validators.Equals(True))
)
@htf.plug(ts3=TS3Plug.placeholder)
def digital_out_test(test: htf.TestApi, ts3: TS3Plug):
    ts3.set_dig_output_pin(module=0, pin=1, value=True)
    time.sleep(1)

    test.measurements["DIGITAL_OUT_1"] = True

    ts3.set_dig_output_pin(module=0, pin=1, value=False)
    time.sleep(1)


@htf.measures(
    htf.Measurement("ANALOG_3V3")
    .with_units(units.VOLT_DC)
    .with_validator(validators.InRange(3.2, 3.4)),
    htf.Measurement("ANALOG_5V")
    .with_units(units.VOLT_DC)
    .with_validator(validators.InRange(4.8, 5.2)),
    htf.Measurement("ANALOG_12VA")
    .with_units(units.VOLT_DC)
    .with_validator(validators.InRange(10, 14)),
    htf.Measurement("ANALOG_3V3A")
    .with_units(units.VOLT_DC)
    .with_validator(validators.InRange(3.2, 3.4))
)
@htf.plug(ts3=TS3Plug.placeholder)
def analog_test_3V3(test: htf.TestApi, ts3: TS3Plug):
    test.measurements["ANALOG_3V3"] = ts3.get_ana_input_pin(module=15, pin=18)
    test.measurements["ANALOG_5V"] = ts3.get_ana_input_pin(module=15, pin=19)
    test.measurements["ANALOG_12VA"] = ts3.get_ana_input_pin(module=15, pin=20)
    test.measurements["ANALOG_3V3A"] = ts3.get_ana_input_pin(module=15, pin=22)


@htf.measures(
    htf.Measurement("ANALOG_IN_1")
    .with_units(units.VOLT_DC)
    .with_validator(validators.InRange(5.15, 5.25)),
    htf.Measurement("ANALOG_IN_2")
    .with_units(units.VOLT_DC)
    .with_validator(validators.InRange(2.45, 2.55))
)
@htf.plug(ts3=TS3Plug.placeholder)
def analog_test(test: htf.TestApi, ts3: TS3Plug):
    # TODO: connect analog module
    ts3.set_ana_output_pin(module=4, pin=1, value=5.2)
    test.measurements["ANALOG_IN_1"] = ts3.get_ana_input_pin(module=4, pin=1, input_range=4)
    test.measurements["ANALOG_IN_2"] = ts3.get_ana_input_pin(module=4, pin=2, input_range=4)


@htf.plug(ts3=TS3Plug.placeholder)
def setup_phase(test, ts3: TS3Plug):
    print("Detected modules:")

    i = 0
    for module in ts3.get_external_modules():
        print(f"\t{i} -> {module}")
        i += 1
    ts3.set_dut_power(True, True)


@htf.plug(ts3=TS3Plug.placeholder)
def teardown_phase(test, ts3: TS3Plug):
    ts3.set_dut_power(False, False)


def main():
    conf.load(station_server_port=4444)

    with StationServer() as server:
        web_launcher.launch('http://localhost:4444')

        # Setup the test.
        test = htf.Test(
            htf.PhaseGroup(
                # Setup phases
                # Perform neccessary setup here
                # For example: turn on power supplies, connect programmers....
                setup=[
                    setup_phase
                ],
                # Main phases
                # Perform all main steps here
                # For example: measure R1, program D1, measure switching frequency of Q1....
                main=[
                    # digital_out_test,
                    analog_test_3V3,
                    analog_test
                ],
                # Teardown phase
                # Perform neccessary teardown here
                # For example: turn off power supplies, disconnect connections....
                teardown=[
                    teardown_phase
                ]
            ).with_plugs(ts3=TS3Interface),
            test_name='TS3Test',
            test_description='TS3 example test using OpenHTF',
            test_version='1.0.0'
        )

        # Add log outputs to the test.
        test.add_output_callbacks(server.publish_final_state)
        test.add_output_callbacks(ConsoleSummary())
        test.add_output_callbacks(OutputToJSON('{dut_id}.json', indent=2))

        # Execute the test
        test.execute(test_start=user_input.prompt_for_test_start(validator=lambda sn: None if sn == "" else sn))


if __name__ == "__main__":
    main()
