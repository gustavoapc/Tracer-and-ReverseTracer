import argparse
from collections import OrderedDict
import json
import socket
import tabulate
import maps
import packets
import struct
import requests
import tracer_reverso

MAX_TTL = 32
PORT = 33434
PORT_TCP = 80
TIMEOUT = 2

def main():
    parser = argparse.ArgumentParser(description='Documentação trace')
    parser.add_argument('destino')
    parser.add_argument('--ttl', type=int, default=MAX_TTL, help=f'Definir um número de TTL diferente do padrão ({MAX_TTL})')
    parser.add_argument('--mapa', action='store_true', help='Gerar mapa exibindo a rota realizada')
    parser.add_argument('--ouvinte', action='store_true', help='Deixar o trace ouvindo para receber requisições de um trace reverso')
    parser.add_argument('--reverso', action='store_true', help='Realizar um trace reverso')
    args = parser.parse_args()

    if args.ouvinte:
        tracer_reverso.iniciar_reverso()

    elif args.reverso:
        enviar_ping(args.destino)
        dados_reverso = receber_dados_reverso()
        ip = list(dados_reverso.keys())[0]
        print(f'Iniciando trace para {ip}')
        trace_route(ip, args.ttl, args.mapa, True, dados_reverso)

    else:
        trace_route(args.destino, args.ttl, args.mapa)

def trace_route(destino, time_to_live=MAX_TTL, mapa=False, reverso=False, dados_reverso=None):
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
    if mapa:
        localizacao.criar_mapa()
    if reverso:
        print(dados_reverso)
        localizacao.criar_mapa(True, dados_reverso)

def enviar_ping(destino):
    meu_ip = requests.get("http://ipv4.icanhazip.com").text.strip()
    envia_ip_reverso = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    envia_ip_reverso.connect((destino, 12345))

    envia_ip_reverso.send(str(meu_ip).encode())

    envia_ip_reverso.close()


def receber_dados_reverso():
    recebe_ip_reverso = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    recebe_ip_reverso.bind(('0.0.0.0', 54321))
    recebe_ip_reverso.listen()

    print('Aguardando conexões para receber dados com trace reverso')

    try:
        recebe_socket, recebe_addr = recebe_ip_reverso.accept()

        dados_recebidos = recebe_socket.recv(1024)
        dados_str = dados_recebidos.decode()

        dados_ord_dict = eval(dados_str)

        if isinstance(dados_ord_dict, OrderedDict):
            print("Dados Recebidos:")
            for key, value in dados_ord_dict.items():
                print(f"{key}: {value}")

            return dados_ord_dict
        else:
            print("Erro nos dados recebidos")

    except Exception as e:
        print(f"Erro ao receber dados: {e}")
    finally:
        recebe_ip_reverso.close()

if __name__ == '__main__':
    main()
