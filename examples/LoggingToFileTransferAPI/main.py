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

from file_transfer_api_factory import FileTransferAPI


@htf.measures(
    htf.Measurement("DIGITAL_TEST_1")
    .with_validator(validators.Equals(True))
)
def digital_test(test: htf.TestApi):
    test.measurements["DIGITAL_TEST_1"] = True


def main():
    # Setup the test.
    test = htf.Test(
        htf.PhaseGroup(
            # Main phases
            # Perform all main steps here
            # For example: measure R1, program D1, measure switching frequency of Q1....
            main=[
                digital_test,
            ],
        ),
        test_name='FileTransferAPILogTest',
        test_description='Simple example test using OpenHTF and the File Transfer API for logging.',
        test_version='1.0.0'
    )

    # Add log outputs to the test.
    test.add_output_callbacks(ConsoleSummary())
    
    file_transfer_api = FileTransferAPI("http://nw-db-04.neways.local:46102")
    test.add_output_callbacks(file_transfer_api.upload('\\\\newsonfps01\\Prddata\\NIS\\Drawingitems_datalog\\JCS\\601686500\\{dut_id}_{start_time_millis}_{outcome}.json'))

    test.add_output_callbacks(OutputToJSON('{dut_id}.json', indent=2))

    # Execute the test
    test.execute(test_start=user_input.prompt_for_test_start(
        validator=lambda sn: None if sn == "" else sn))


if __name__ == "__main__":
    main()
