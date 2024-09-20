import inspect
from typing import Optional

from framework.commons.apdu_utils import lower_req
from framework.commons.logger import logger
import tracing


def process(app, access_token=None, operation: Optional[str] = None, request=None):
    """
    Process the incoming REST request and return the response in JSON format.

    This function processes the request object (which is the model received from the REST endpoint),
    performs necessary operations or transformations, and returns the response in a JSON-serializable format.

    Args:
        app (object): The Flask or application object that handles the request lifecycle and context.
        access_token (str, optional): The access token for authentication, if required by the endpoint. Defaults to None.
        operation (str, optional): The specific operation to be performed, can be used to route logic within this function.
        request (object): The request object that contains the data sent in the REST API call. Typically, this will be a Flask request object.

    Returns:
        dict: A dictionary containing the processed data, ready to be returned as the JSON response body.

    Example Usage:
        - This function is called when a REST API endpoint is triggered, and it processes the incoming request,
          performs validation or transformation, and returns the output in a JSON format.

    Notes:
        - The request object is expected to contain the necessary payload or parameters sent by the client in the API request.
        - The `lower_req` method, which is invoked within this function, appears to handle some form of data normalization or transformation on the request.
    """
    mx = f'({inspect.currentframe().f_code.co_name})'
    message = lower_req(request, mx=mx)
    message['language'] = 'romanian'
    return message

