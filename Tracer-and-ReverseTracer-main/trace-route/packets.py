import struct    

PORT = 33434
PORT_TCP = 80


def criar_pacote_udp():
        udp_header = struct.pack('!HHHH', PORT, PORT, 8, 0)
        udp_packet = udp_header + b'0'

        return udp_header + udp_packet

def criar_pacote_icmp(ttl):
    tipo = 8
    codigo = 0
    checksum = 0
    identificador = 12345
    sequencia = 0

    header = struct.pack('!BBHHH', tipo, codigo, checksum, identificador, sequencia)
    dados = b'Hello, ICMP!'
    pacote_icmp = header + dados

    checksum = calcula_checksum(pacote_icmp)
    header = struct.pack('!BBHHH', tipo, codigo, checksum, identificador, sequencia)
    pacote_icmp = header + dados

    return pacote_icmp

def calcula_checksum(data):
    length = len(data)
    sum_ = 0
    count_to = (length // 2) * 2
    count = 0

    while count < count_to:
        this_val = data[count + 1] * 256 + data[count]
        sum_ += this_val
        sum_ &= 0xffffffff
        count += 2

    if count_to < length:
        sum_ += data[length - 1]
        sum_ &= 0xffffffff

    sum_ = (sum_ >> 16) + (sum_ & 0xffff)
    sum_ += (sum_ >> 16)
    result = ~sum_ & 0xffff
    result = result >> 8 | ((result & 0xff) << 8)
    return result



