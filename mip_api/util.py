import json
import logging
import os
from datetime import date, timedelta

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)


def build_return_json(code, body):
    return {
        "statusCode": code,
        "body": json.dumps(body, indent=2),
    }


def build_return_text(code, body):
    return {
        "statusCode": code,
        "body": body,
    }


def get_os_var(varnam):
    try:
        return os.environ[varnam]
    except KeyError as exc:
        raise Exception(f"The environment variable '{varnam}' must be set")


def parse_codes(codes):
    data = []
    if codes:
        data = codes.split(",")
    return data


def _param_str(params, param):
    if params and param in params:
        return params[param]
    return ""


def _param_bool(params, param):
    if params and param in params:
        if params[param].lower() not in ["false", "no", "off"]:
            return True
    return False


def _param_hide_inactive_bool(params):
    # Default is to hide inactive codes
    return not _param_bool(params, "show_inactive_codes")


def _param_show_other_bool(params):
    # Default is to hide "other" code
    return _param_bool(params, "show_other_code")


def _param_show_no_program_bool(params):
    # Default is to show "no program" code
    return not _param_bool(params, "hide_no_program_code")


def _param_date_str(params):
    # Default is to show "no program" code
    return _param_str(params, "target_date")


def _param_limit_int(params):
    if params and "limit" in params:
        try:
            return int(params["limit"])
        except ValueError as exc:
            err_str = "QueryStringParameter 'limit' must be an Integer"
            raise ValueError(err_str) from exc
    return 0


def _param_priority_list(params):
    if params and "priority_codes" in params:
        return parse_codes(params["priority_codes"])

    return None


def params_dict(event):
    _params = {}
    if "queryStringParameters" in event:
        _params = event["queryStringParameters"]
        LOG.debug(f"Query-string _parameters: {_params}")
    params = {
        "hide_inactive": _param_hide_inactive_bool(_params),
        "limit": _param_limit_int(_params),
        "priority_codes": _param_priority_list(_params),
        "show_no_program": _param_show_no_program_bool(_params),
        "show_other": _param_show_other_bool(_params),
        "date": _param_date_str(_params),
    }
    return params


def target_period(when=None):
    if when is None:
        target_day = date.today()
    else:
        target_day = date.fromisoformat(when)
    LOG.info(f"Processing period for {target_day}")

    if target_day.day <= 7:
        # at the beginning of the month, look at previous month
        _first = target_day.replace(day=1)  # first day of target month
        end = _first - timedelta(days=1)  # last day of previous month
        start = end.replace(day=1)  # first day of previous month

        end_str = end.isoformat()
        start_str = start.isoformat()
    else:
        # otherwise look at month-to-date
        start = target_day.replace(day=1)
        end_str = target_day.isoformat()
        start_str = start.isoformat()

    LOG.info(f"Start day is {start_str}")
    LOG.info(f"End day is {end_str}")

    return start_str, end_str
