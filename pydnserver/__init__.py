# encoding: utf-8

# Get module version
from ._metadata import __version__, __authorshort__, __module_name__

# Import key items from module
from .dns_server import DNSServer
from .dns_query import DNSQuery

from ._exceptions import (DNSQueryFailed,
                          NoActiveRecordForHost,
                          NoForwardersConfigured,
                          MultipleForwardersForInterface)

# Set default logging handler to avoid "No handler found" warnings.
from logging import NullHandler, getLogger
getLogger(__name__).addHandler(NullHandler())
