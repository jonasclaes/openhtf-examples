import base64
import json
import logging
import httplib2

from openhtf.output.callbacks.json_factory import OutputToJSON
from openhtf import util
from openhtf.util import data
import six


class UploadFailedError(Exception):
    """Raised when an upload to file transfer API fails."""


class FileTransferAPI(object):
    """
    Return an output callback that writes JSON Test Records to the file transfer API.
    """

    def __init__(self, server_address="http://nw-db-04:46102", **kwargs):
        self.endpoint = f"{server_address}/api/logging/LogAdditionalDataRaw"
    
        self.inline_attachments = True

        # Conform strictly to the JSON spec by default.
        kwargs.setdefault('allow_nan', False)
        self.allow_nan = kwargs['allow_nan']
        self.json_encoder = json.JSONEncoder(**kwargs)

    def serialize_test_record(self, test_record):
        return self.json_encoder.encode(self.convert_to_dict(test_record))

    def convert_to_dict(self, test_record):
        as_dict = data.convert_to_base_types(test_record,
                                             json_safe=(not self.allow_nan))
        if self.inline_attachments:
            for phase, original_phase in zip(as_dict['phases'], test_record.phases):
                for name, attachment in six.iteritems(phase['attachments']):
                    original_data = original_phase.attachments[name].data
                    attachment['data'] = base64.standard_b64encode(
                        original_data).decode('utf-8')
        return as_dict

    def save_to_disk(self, filename_pattern=None):
        """Returns a callback to convert test record and save to disk."""

        if not filename_pattern:
            raise RuntimeError('Must specify a filename_pattern.')

        self._output_to_json = OutputToJSON(
            filename_pattern, inline_attachments=self.inline_attachments, indent=2)

        def save_to_disk_callback(test_record):
            with self._output_to_json.open_output_file(test_record) as outfile:
                outfile.write(
                    self._output_to_json.serialize_test_record(test_record))

        return save_to_disk_callback

    def upload(self, path_pattern=None):
        """Returns a callback to convert test record and save to disk."""

        if not path_pattern:
            raise RuntimeError('Must specify a filepath.')

        def upload_callback(test_record):
            logging.info('Uploading result...')
            http = httplib2.Http()

            # Ignore keys for the log filename to not convert larger data structures.
            record_dict = data.convert_to_base_types(
                test_record, ignore_keys=('code_info', 'phases', 'log_records'))
            pattern = path_pattern
            filepath = util.format_string(pattern, record_dict)

            newline_data = self.serialize_test_record(test_record)

            body_data = {
                'filepath': filepath,
                'newline': newline_data
            }
            body = json.dumps(body_data)

            headers = {
                'User-Agent': 'OpenHTFTestFileTransferAPIClient / v1.0.0',
                'Content-Type': 'application/json',
                'Accept': '*/*'
            }

            resp, content = http.request(
                uri=self.endpoint, method='POST', body=body, headers=headers)

            if resp.status != 200:
                logging.debug('Upload failed: %s', content)
                raise UploadFailedError(content)

        return upload_callback
