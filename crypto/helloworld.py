import logging
import sys

from util import make_client, set_credential_from_file


_logger = logging.getLogger()
logging.getLogger().setLevel(logging.DEBUG)


def main(argv, argc) -> int:
    if argc < 1:
        _logger.error(
            f"Did not specify a Shrimpy credentials file."
        )
        return 1
    if not set_credential_from_file(argv[1]):
        _logger.error(
            f"UNable to set Shrimpy API credentials from file. No credential file specified."
        )
        return 1
    c = make_client()
    print(c.get_supported_exchanges())
    return 0

if __name__ == '__main__':
    main(sys.argv, len(sys.argv))

    