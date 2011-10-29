#!/usr/bin/python

import logging, socket, struct
from ctypes import *

IP_ADAPTER_NETBIOS_OVER_TCPIP_ENABLED = 0x0040
IP_ADAPTER_IPV4_ENABLED               = 0x0080
IP_ADAPTER_IPV6_ENABLED               = 0x0100

GAA_FLAG_SKIP_UNICAST                 = 0x0001
GAA_FLAG_SKIP_ANYCAST                 = 0x0002
GAA_FLAG_SKIP_MULTICAST               = 0x0004
GAA_FLAG_SKIP_DNS_SERVER              = 0x0008
GAA_FLAG_INCLUDE_PREFIX               = 0x0010
GAA_FLAG_SKIP_FRIENDLY_NAME           = 0x0020
GAA_FLAG_INCLUDE_WINS_INFO            = 0x0040
GAA_FLAG_INCLUDE_GATEWAYS             = 0x0080
GAA_FLAG_INCLUDE_ALL_INTERFACES       = 0x0100
GAA_FLAG_INCLUDE_ALL_COMPARTMENTS     = 0x0200
GAA_FLAG_INCLUDE_TUNNEL_BINDINGORDER  = 0x0400

class SOCKADDR_IN6(Structure):
    _fields_ = [
        ('sin_family', c_ushort),
        ('sin_port', c_ushort),
        ('sin6_flowinfo', c_ulong),
        ('sin6_addr', c_ubyte * 16), # IN6_ADDR
        ('sin6_scope_id', c_ulong)
    ]

class SOCKADDR_IN(Structure):
    _fields_ = [
        ('sin_family', c_ushort),
        ('sin_port', c_ushort),
        ('sin_addr', c_ulong), # IN_ADDR
        ('sin_zero', c_char * 8)
    ]

class SOCKET_ADDRESS(Structure):
    _fields_ = [
        ('lpSockaddr', c_void_p), # POINTER(SOCKADDR)
        ('iSockaddrLength', c_int)
    ]

class GUID(Structure):
    _fields_ = [
        ('Data1', c_ulong),
        ('Data2', c_ushort),
        ('Data3', c_ushort),
        ('Data4', c_ubyte * 8)
    ]

class Info(Structure):
    _fields_ = [
        ('Reserved', c_ulonglong), # :24
        ('NetLuidIndex', c_ulonglong), # :24
        ('IfType', c_ulonglong) # :16
    ]

class NET_LUID(Union):
    _fields_ = [
        ('Value', c_ulonglong)
        # Info is not included because I don't know how to handle struct's
        # bits (for now!).
        #('Info', Info)
    ]

class _S0(Structure):
    _fields_ = [
        ('Length', c_ulong),
        ('IfIndex', c_ulong)
    ]

class _U0(Union):
    _anonymous_ = ('s')
    _fields_ = [
        ('Alignment', c_ulonglong),
        ('s', _S0)
    ]

# Forward decleration.
class IP_ADAPTER_ADDRESSES(Structure):
    pass

# Forward decleration.
class IP_ADAPTER_UNICAST_ADDRESS(Structure):
    pass

IP_ADAPTER_ADDRESSES._anonymous_ = ('u')

IP_ADAPTER_ADDRESSES._fields_ = [
    ('u', _U0),
    ('Next', POINTER(IP_ADAPTER_ADDRESSES)),
    ('AdapterName', c_char_p),
    ('FirstUnicastAddress', POINTER(IP_ADAPTER_UNICAST_ADDRESS)),
    ('FirstAnycastAddress', c_void_p), # POINTER(IP_ADAPTER_ANYCAST_ADDRESS)
    ('FirstMulticastAddress', c_void_p), # POINTER(IP_ADAPTER_MULTICAST_ADDRESS)
    ('FirstDnsServerAddress', c_void_p), # POINTER(IP_ADAPTER_DNS_SERVER_ADDRESS)
    ('DnsSuffix', c_wchar_p),
    ('Description', c_wchar_p),
    ('FriendlyName', c_wchar_p),
    ('PhysicalAddress', c_ubyte * 8), # BYTE[MAX_ADAPTER_ADDRESS_LENGTH]
    ('PhysicalAddressLength', c_ulong),
    ('Flags', c_ulong), # union
    ('Mtu', c_ulong),
    ('IfType', c_ulong),
    ('OperStatus', c_int), # enum IF_OPER_STATUS
    ('Ipv6IfIndex', c_ulong),
    ('ZoneIndices', c_ulong * 16),
    ('FirstPrefix', c_void_p), # POINTER(PIP_ADAPTER_PREFIX)
    ('TransmitLinkSpeed', c_ulonglong),
    ('ReceiveLinkSpeed', c_ulonglong),
    ('FirstWinsServerAddress', c_void_p), # POINTER(IP_ADAPTER_WINS_SERVER_ADDRESS_LH)
    ('FirstGatewayAddress', c_void_p), # POINTER(IP_ADAPTER_GATEWAY_ADDRESS_LH)
    ('Ipv4Metric', c_ulong),
    ('Ipv6Metric', c_ulong),
    ('Luid', NET_LUID),
    ('Dhcpv4Server', SOCKET_ADDRESS),
    ('CompartmentId', c_uint), # NET_IF_COMPARTMENT_ID
    ('NetworkGuid', GUID), # NET_IF_NETWORK_GUID
    ('ConnectionType', c_int), # enum NET_IF_CONNECTION_TYPE
    ('TunnelType', c_int), # enum TUNNEL_TYPE
    ('Dhcpv6Server', SOCKET_ADDRESS),
    ('Dhcpv6ClientDuid', c_byte * 130), # BYTE[MAX_DHCPV6_DUID_LENGTH]
    ('Dhcpv6ClientDuidLength', c_ulong),
    ('Dhcpv6Iaid', c_ulong),
]

IP_ADAPTER_UNICAST_ADDRESS._anonymous_ = ('u')

IP_ADAPTER_UNICAST_ADDRESS._fields_ = [
    ('u', _U0),
    ('Next', POINTER(IP_ADAPTER_UNICAST_ADDRESS)),
    ('Address', SOCKET_ADDRESS),
    ('PrefixOrigin', c_int), # enum IP_PREFIX_ORIGIN
    ('SuffixOrigin', c_int), # enum IP_PREFIX_ORIGIN
    ('DadState', c_int), # enum IP_DAD_STATE
    ('ValidLifetime', c_ulong),
    ('PreferredLifetime', c_ulong),
    ('LeaseLifetime', c_ulong),
    ('OnLinkPrefixLength', c_ubyte)
]

def GetNetworkInterfaces():
    interfaces = list()
    try:
        size = c_ulong()
        flags = GAA_FLAG_SKIP_ANYCAST | GAA_FLAG_SKIP_MULTICAST | GAA_FLAG_SKIP_DNS_SERVER | GAA_FLAG_SKIP_FRIENDLY_NAME
        err = windll.iphlpapi.GetAdaptersAddresses(0, flags, None, None, byref(size))
        if err != 111: # ERROR_BUFFER_OVERFLOW
            raise RuntimeError("First call to GetAdaptersAddresses returned with an error %d" % (err))
        ipaddrs_buf = create_string_buffer(size.value)
        err = windll.iphlpapi.GetAdaptersAddresses(0, flags, None, byref(ipaddrs_buf), byref(size))
        if err != 0:
            raise RuntimeError("Second call to GetAdaptersAddresses returned with an error %d" % (err))
        ipaddr = cast(ipaddrs_buf, POINTER(IP_ADAPTER_ADDRESSES)).contents
        while ipaddr is not None:
            # The IP_ADAPTER_IPV4_ENABLED exist only on Windows Vista and later.
            if ipaddr.Length > 144: # sizeof(IP_ADAPTER_ADDRESSES_XP)
                enabled = ipaddr.Flags & IP_ADAPTER_IPV4_ENABLED
            else:
                enabled = True
            # Include only hardware network interfaces.
            if enabled and (ipaddr.PhysicalAddressLength > 0):
                inet = []
                inet6 = []
                if ipaddr.FirstUnicastAddress:
                    addr = ipaddr.FirstUnicastAddress.contents
                    while addr:
                        if addr.Address.iSockaddrLength == sizeof(SOCKADDR_IN):
                            sock_addr = cast(addr.Address.lpSockaddr, POINTER(SOCKADDR_IN)).contents
                            inet.append(socket.inet_ntoa(struct.pack('L', sock_addr.sin_addr)))
                        elif addr.Address.iSockaddrLength == sizeof(SOCKADDR_IN6):
                            sock_addr = cast(addr.Address.lpSockaddr, POINTER(SOCKADDR_IN6)).contents
                            size_buf = c_ulong(64)
                            addr_buf = create_string_buffer(size.value)
                            windll.ws2_32.WSAAddressToStringA(byref(sock_addr), sizeof(sock_addr), None, byref(addr_buf), byref(size_buf))
                            addr_str = addr_buf.value
                            trim = addr_str.find('%')
                            if trim > 0:
                                addr_str = addr_str[:trim]
                            inet6.append(addr_str)
                        if addr.Next:
                            addr = addr.Next.contents
                        else:
                            addr = None
                if inet or inet6:
                    hw =  '-'.join(map(lambda x: "%02x" % (ipaddr.PhysicalAddress[x]), range(ipaddr.PhysicalAddressLength)))
                    interfaces.append({ 'name' : ipaddr.Description,
                        'inet' : inet, 'inet6' : inet6,
                        'hw' : hw })
            if ipaddr.Next:
                ipaddr = ipaddr.Next.contents
            else:
                ipaddr = None
    except:
        logging.exception("Error retrieving network interfaces.")
    return interfaces

if __name__ == "__main__":
    print GetNetworkInterfaces()
