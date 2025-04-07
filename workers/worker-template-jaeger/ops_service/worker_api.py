import inspect
from typing import Optional

from framework.commons.apdu_utils import lower_req


def process(app, access_token=None, operation: Optional[str] = None, request=None):
    global topic, type
    mx = f'({inspect.currentframe().f_code.co_name})'
    message = lower_req(request, mx=mx)
    return message