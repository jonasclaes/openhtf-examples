import time

# OpenHTF
# Import OpenHTF as htf since we will be using it a lot.
import openhtf as htf

# Output callbacks
from openhtf.output.callbacks.console_summary import ConsoleSummary
from openhtf.output.callbacks.json_factory import OutputToJSON

# Plugs
from openhtf.plugs import BasePlug
from openhtf.plugs import user_input

# Utils
from openhtf.util import validators
from openhtf.util import units

# InstrumentPy devices
from instrumentpy.common.tcpip_device import TCPIPDevice
from instrumentpy.psu.aimtti.mx100tp import MX100TP


class MX100TPPlug(BasePlug, MX100TP):
    ip_address = None

    def __init__(self) -> None:
        assert self.ip_address is not None

        tcp_ip_device = TCPIPDevice(self.ip_address, 9221)

        # Clever trick in Python:
        # Multiple inheritance, so specifying device will pass it on to MX100TP.
        super().__init__(device=tcp_ip_device)


class PSU1(MX100TPPlug):
    ip_address = "192.168.0.102"


DELAY_POWER = 0.5


@htf.measures(
    htf.Measurement("CHANNEL_1_VOLTAGE")
    .with_units(units.VOLT_DC)
    .with_validator(validators.InRange(2.9, 3.1))
)
@htf.plug(psu=MX100TPPlug.placeholder)
def test_1(test: htf.TestApi, psu: MX100TPPlug):
    psu.set_channel_voltage(1, 3.0)
    psu.set_channel(1, 1)
    time.sleep(DELAY_POWER)
    test.measurements["CHANNEL_1_VOLTAGE"] = psu.get_channel_voltage(1)
    psu.disable_channel(1)
    time.sleep(DELAY_POWER)


@htf.measures(
    htf.Measurement("CHANNEL_1_VOLTAGE")
    .with_units(units.VOLT_DC)
    .with_validator(validators.InRange(4.9, 5.1))
)
@htf.plug(psu=MX100TPPlug.placeholder)
def test_2(test: htf.TestApi, psu: MX100TPPlug):
    psu.set_channel_voltage(1, 5.0)
    psu.set_channel(1, 1)
    time.sleep(DELAY_POWER)
    test.measurements["CHANNEL_1_VOLTAGE"] = psu.get_channel_voltage(1)
    psu.disable_channel(1)
    time.sleep(DELAY_POWER)


@htf.measures(
    htf.Measurement("CHANNEL_1_VOLTAGE")
    .with_units(units.VOLT_DC)
    .with_validator(validators.InRange(8.9, 9.1))
)
@htf.plug(psu=MX100TPPlug.placeholder)
def test_3(test: htf.TestApi, psu: MX100TPPlug):
    psu.set_channel_voltage(1, 9.0)
    psu.set_channel(1, 1)
    time.sleep(DELAY_POWER)
    test.measurements["CHANNEL_1_VOLTAGE"] = psu.get_channel_voltage(1)
    psu.disable_channel(1)
    time.sleep(DELAY_POWER)


@htf.measures(
    htf.Measurement("CHANNEL_1_VOLTAGE")
    .with_units(units.VOLT_DC)
    .with_validator(validators.InRange(11.9, 12.1))
)
@htf.plug(psu=MX100TPPlug.placeholder)
def test_4(test: htf.TestApi, psu: MX100TPPlug):
    psu.set_channel_voltage(1, 12.0)
    psu.set_channel(1, 1)
    time.sleep(DELAY_POWER)
    test.measurements["CHANNEL_1_VOLTAGE"] = psu.get_channel_voltage(1)
    psu.disable_channel(1)
    time.sleep(DELAY_POWER)


@htf.measures(
    htf.Measurement("CHANNEL_1_VOLTAGE")
    .with_units(units.VOLT_DC)
    .with_validator(validators.InRange(23.9, 24.1))
)
@htf.plug(psu=MX100TPPlug.placeholder)
def test_5(test: htf.TestApi, psu: MX100TPPlug):
    psu.set_channel_voltage(1, 24.0)
    psu.set_channel(1, 1)
    time.sleep(DELAY_POWER)
    test.measurements["CHANNEL_1_VOLTAGE"] = psu.get_channel_voltage(1)
    psu.disable_channel(1)
    time.sleep(DELAY_POWER)


@htf.measures(
    htf.Measurement("CHANNEL_1_VOLTAGES")
    .with_units(units.VOLT_DC)
    .with_dimensions('V')
)
@htf.plug(psu=MX100TPPlug.placeholder)
def test_6(test: htf.TestApi, psu: MX100TPPlug):
    for voltage in range(25, 120, 5):
        voltage = voltage / 10
        psu.set_channel_voltage(1, voltage)
        psu.set_channel(1, 1)
        time.sleep(DELAY_POWER)
        test.measurements["CHANNEL_1_VOLTAGES"][(
            voltage)] = psu.get_channel_voltage(1)
        psu.disable_channel(1)
        time.sleep(DELAY_POWER)

    print(test.measurements["CHANNEL_1_VOLTAGES"])


@htf.plug(psu=MX100TPPlug.placeholder)
def setup_phase(test, psu: MX100TPPlug):
    pass


@htf.plug(psu=MX100TPPlug.placeholder)
def teardown_phase(test, psu: MX100TPPlug):
    psu.disable_all()


def main():
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
                test_1,
                test_2,
                test_3,
                test_4,
                test_5,
                test_6,
            ],
            # Teardown phase
            # Perform neccessary teardown here
            # For example: turn off power supplies, disconnect connections....
            teardown=[
                teardown_phase
            ]
        ).with_plugs(psu=PSU1),
        test_name='MX100TPTest',
        test_description='MX100TP example test using OpenHTF',
        test_version='1.0.0'
    )

    # Add log outputs to the test.
    test.add_output_callbacks(ConsoleSummary())
    test.add_output_callbacks(OutputToJSON('{dut_id}.json', indent=2))

    # Execute the test
    test.execute(test_start=user_input.prompt_for_test_start(
        validator=lambda sn: None if sn == "" else sn))


if __name__ == "__main__":
    main()
