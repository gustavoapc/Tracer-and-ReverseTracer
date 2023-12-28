import socket
import tabulate
import maps
import packets
import struct

MAX_TTL = 32
PORT = 33434
PORT_TCP = 80
TIMEOUT = 2

def iniciar_reverso():
    resultado = ouvindo()
    ip_legivel = resultado[0]
    addr = resultado[1]
    trace_reverso_dados = trace_route_reverso(ip_legivel)

    responder_com_reverso(addr[0], trace_reverso_dados)

def ouvindo():
    print('Aguardando conexões')

    socRecebe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socRecebe.bind(('0.0.0.0', 12345))
    socRecebe.listen()

    while True:
        conn, addr = socRecebe.accept()
        with conn:
            buffer = conn.recv(1024)

            ip_legivel = buffer.decode('utf-8')

            print(f"Recebido pacote de {addr} com IP: {ip_legivel}")

            return ip_legivel, addr

def trace_route_reverso(destino, time_to_live=MAX_TTL, mapa=False):
    socEnvio = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
    socRecebe = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    socRecebe.bind(('', PORT))
    socRecebe.settimeout(TIMEOUT)

    localizacao = maps.maps()

    for TTL in range(1, time_to_live + 1):
        socEnvio.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, TTL)

        udp_packet = packets.criar_pacote_udp()
        
        socEnvio.sendto(udp_packet, (destino, PORT))

        ip = socket.gethostbyname(destino)

        try:
            buffer, addr = socRecebe.recvfrom(1024)
            if addr[0] == ip:
                break
            
            print(tabulate.tabulate([['IP', 'TTL', 'PROTOCOLO', 'LOCALIZAÇÃO'], [addr[0], TTL, 'UDP', localizacao.cidade((addr[0]))]], tablefmt='heavy_grid'))
            

        except socket.timeout:

            socEnvioICMP = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
            socEnvioICMP.bind(('0.0.0.0', 0))
            socEnvioICMP.settimeout(TIMEOUT)
            
            pacote_icmp = packets.criar_pacote_icmp(TTL)
            socEnvioICMP.sendto(pacote_icmp, (destino, 0))

            try:
                buffer, addr = socRecebe.recvfrom(1024)
                print(tabulate.tabulate([['IP', 'TTL', 'PROTOCOLO', 'LOCALIZAÇÃO'], [addr[0], TTL, 'ICMP', localizacao.cidade(addr[0])]], tablefmt='heavy_grid')) 

                if addr[0] == ip:
                    break
            except socket.timeout:
                print(tabulate.tabulate([['IP', 'TTL', 'PROTOCOLO', 'LOCALIZAÇÃO'], ['DESCONHECIDO', TTL, 'ICMP', 'Silent Hill']], tablefmt='heavy_grid'))

                if addr[0] == ip:
                    break
    
    return localizacao.servidores

def responder_com_reverso(destino, dados):
    envia_ip_reverso = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    envia_ip_reverso.connect((destino, 54321))

    envia_ip_reverso.send(str(dados).encode())

    envia_ip_reverso.close()

