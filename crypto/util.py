import logging
import os
import sys
import datetime

#mimick datetime class function in Python3.7
datetime.fromisoformat = lambda x: datetime.datetime.strptime(x, "%Y-%m-%dT%H:%M:%S.%fZ")

import shrimpy

def timedelta_to_float(t: datetime.timedelta) -> float:
    return float(t.days*86400.00 + t.seconds)

def make_client():
    try:
        c = shrimpy.ShrimpyApiClient(os.environ['SHRIMPY_PUBLIC_KEY'], os.environ['SHRIMPY_SECRET_KEY'])
        return c

    except AttributeError as e:
        _logger.error(
            f"Could not construct Shrimpy API. Public and/or Secret keys not set properly. Error: {e}"
        )
        return None


def set_credential_from_file(filepath) -> bool:
    with open(filepath, "r") as f:
        data = f.read()

    if not data:
        _logger.error(
            f"Unable to load credentials from file. File, {filepath}, contained no data."
        )
        return False

    try:
        keys = data.split("\n")
        os.environ['SHRIMPY_PUBLIC_KEY'] = keys[0]
        os.environ['SHRIMPY_SECRET_KEY'] = keys[1]

    except IndexError:
        _logger.error(
            f"Could not set credentials. Public and Secret key are not \\n separated in the file."
        )
        return False
    return True
