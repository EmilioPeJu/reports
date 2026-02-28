#!/usr/bin/env python
import argparse
import socket
import time

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('host')
    return parser.parse_args()


def main():
    args = parse_args()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((args.host, 8888))
    for wide in range(8):
        s.sendall(f'LVDSOUT1.OCT_DELAY={wide}\n'.encode())
        assert s.recv(32) == b'OK\n'
        for fine in range(512):
            s.sendall(f'LVDSOUT1.FINE_DELAY={fine}\n'.encode())
            assert s.recv(32) == b'OK\n'
            time.sleep(0.01)

    s.close()


if __name__ == '__main__':
    main()
