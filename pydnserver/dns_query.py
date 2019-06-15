# encoding: utf-8

import sys
import socket
import logging_helper
from ipaddress import IPv4Address, IPv4Network, AddressValueError, ip_address
from ._exceptions import DNSQueryFailed

logging = logging_helper.setup_logging()


def move_address_to_another_network(address,
                                    network,
                                    netmask):

    address = ip_address(unicode(address))
    target_network = IPv4Network(u'{ip}/{netmask}'.format(ip=network,
                                                          netmask=netmask),
                                 strict=False)

    network_bits = int(target_network.network_address)
    interface_bits = int(address) & int(target_network.hostmask)

    target_address = network_bits | interface_bits

    return ip_address(target_address)


class DNSQuery(object):

    def __init__(self,
                 hostlist,
                 data,
                 client_address=None,
                 interface=None):

        self.hostlist = hostlist;
        self.data = data
        self.client_address = client_address
        self.interface = interface if interface is not None else u'default'
        self.message = u''
        self._ip = None
        self.error = u''

    @property
    def ip(self):
        return self._ip

    @ip.setter
    def ip(self,
           ip):
        self._ip = IPv4Address(u'{ip}'.format(ip=ip))

    def resolve(self):

        name = self._decode_query()

        if name[-1] == u'.':
            name = name[:-1]

        self.message = u'DNS ({dns}): {name}: ?.?.?.?. '.format(dns=self.interface,
                                                                name=name)

        # Handle reverse lookups
        if u'.in-addr.arpa.' in name:
            # TODO: Can we not just forward these?  No will return host not IP?
            self.error = u'Cannot handle reverse lookups yet!'
            return self._bad_reply()

        if name in self.hostlist:
            redirect_record = self.hostlist[name]
            self._resolve_request_locally(redirect_record['redirect_host'])
        else:
            return self._bad_reply()

        self.message = self.message.replace(u'?.?.?.?', self.ip.exploded)

        return self._reply()

    def _decode_query(self):

        domain = ''
        if sys.version_info.major == 2:
            optype = (ord(self.data[2]) >> 3) & 15   # Opcode bits

            if optype == 0:                     # Standard query
                ini = 12
                lon = ord(self.data[ini])
                while lon != 0:
                    domain += self.data[ini + 1: ini + lon + 1] + '.'
                    ini += lon + 1
                    lon = ord(self.data[ini])
        else:
            optype = (self.data[2] >> 3) & 15  # Opcode bits

            if optype == 0:  # Standard query
                ini = 12
                lon = self.data[ini]
                while lon != 0:
                    domain += self.data[ini + 1: ini + lon + 1].decode('latin-1') + '.'
                    ini += lon + 1
                    lon = self.data[ini]

        return domain

    def _resolve_request_locally(self,
                                 redirect_host):

        if redirect_host.lower() == u'default':
            if self.interface == u'0.0.0.0':  # This string is the DEFAULT_INTERFACE constant of DNSServer object!
                self.error = u'Cannot resolve default as client interface could not be determined!'
                return self._bad_reply()

            redirect_host = self.interface
            self.message += (u'Redirecting to default address. ({address}) '.format(address=redirect_host))

        elif '/' in redirect_host:
            if self.interface == u'0.0.0.0':  # This string is the DEFAULT_INTERFACE constant of DNSServer object!
                self.error = (u'Cannot resolve {redirection} as client interface could not be determined!'
                              .format(redirection=redirect_host))
                return self._bad_reply()

            address, netmask = redirect_host.split('/')
            redirect_host = move_address_to_another_network(address=address,
                                                          network=self.interface,
                                                          netmask=netmask)
            self.message += (u'Redirecting to {address}. '.format(address=redirect_host))

        # Check whether we already have an IP (A record)
        # Note: For now we only support IPv4
        try:
            IPv4Address(u'{ip}'.format(ip=redirect_host))
        except AddressValueError:
            # Attempt to resolve CNAME
            redirected_address = '0.0.0.0' # self._forward_request(redirection)

        else:
            # We already have the A record
            redirected_address = redirect_host

        self.message += (u'Redirecting to {redirection} '.format(redirection=redirect_host))

        self.ip = redirected_address

    def _reply(self):

        packet = b''
        packet += self.data[:2] + b"\x81\x80"
        packet += self.data[4:6] + b'\x00\x01' + b'\x00\x00' + b'\x00\x00'     # Questions and Answers Counts
        packet += self.data[12:]                                            # Original Domain Name Question
        packet += b'\xc0\x0c'                                               # Pointer to domain name
        packet += b'\x00\x01\x00\x01\x00\x00\x00\x3c\x00\x04'               # Response type, ttl and resource data length -> 4 bytes
        packet += self.ip.packed                                            # 4 bytes of IP

        return packet

    def _bad_reply(self):

        packet = b''
        packet += self.data[:2] + b"\x81\x83"
        packet += self.data[4:6] + b'\x00\x00' + b'\x00\x00' + b'\x00\x00'     # Questions and Answers Counts
        packet += self.data[12:]                                            # Original Domain Name Question

        return packet
