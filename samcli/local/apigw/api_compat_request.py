import base64
import logging

from flask.wrappers import Request


LOG = logging.getLogger(__name__)


class ApiGatewayRequest(Request):

    @property
    def query_string_params(self):
        """
        Constructs an APIGW equivalent query string dictionary

        Parameters
        ----------
        flask_request request
            Request from Flask

        Returns dict (str: str)
        -------
            Empty dict if no query params where in the request otherwise returns a dictionary of key to value

        """
        query_string_dict = {}

        # Flask returns an ImmutableMultiDict so convert to a dictionary that becomes
        # a dict(str: list) then iterate over
        for query_string_key, query_string_list in dict(self.args).items():
            query_string_value_length = len(query_string_list)

            # if the list is empty, default to empty string
            if not query_string_value_length:
                query_string_dict[query_string_key] = ""
            else:
                # APIGW doesn't handle duplicate query string keys, picking the last one in the list
                query_string_dict[query_string_key] = query_string_list[-1]

        return query_string_dict

    # @property
    # def data(self):
    #     request_data = self.get_data(parse_form_data=True)
    #
    #     request_mimetype = self.mimetype
    #
    #     is_base_64 = ApiGatewayRequest._should_base64_encode(binary_types, request_mimetype)
    #
    #     if is_base_64:
    #         LOG.debug("Incoming Request seems to be binary. Base64 encoding the request data before sending to Lambda.")
    #         request_data = base64.b64encode(request_data)
    #     elif request_data:
    #         # Flask does not parse/decode the request data. We should do it ourselves
    #         request_data = request_data.decode('utf-8')
    #
    #     return request_data

    # @property
    # def headers(self):
    #     headers = self.environ
    #
    #     event_headers = dict(headers)
    #     event_headers["X-Forwarded-Proto"] = self.scheme
    #     # event_headers["X-Forwarded-Port"] = str(port)

    @staticmethod
    def _should_base64_encode(binary_types, request_mimetype):
        """
        Whether or not to encode the data from the request to Base64

        Parameters
        ----------
        binary_types list(basestring)
            Corresponds to self.binary_types (aka. what is parsed from SAM Template
        request_mimetype str
            Mimetype for the request

        Returns
        -------
            True if the data should be encoded to Base64 otherwise False

        """
        return request_mimetype in binary_types or "*/*" in binary_types
