#!/usr/bin/env python
import argparse
import logging
import math
import numpy as np
import time

from panda import PandaClient

log = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--clock-period-us', type=float, default=0.4)
    parser.add_argument('--fpga-freq', type=int, default=125000000)
    parser.add_argument('--n-samples', type=int, default=125)
    parser.add_argument('host')
    args = parser.parse_args()
    return args


def configure_layout(client, args):
    period_ticks = math.floor(args.clock_period_us * 1e-6 * args.fpga_freq)
    pcap = client.PCAP
    clock_name = client.get_first_instance_name('CLOCK')
    clock = client[clock_name]
    clock.ENABLE.put('PCAP.ACTIVE')
    clock.ENABLE.DELAY.put(0)
    clock.PERIOD.RAW.put(period_ticks)
    clock.WIDTH.put(0)
    counter_name = client.get_first_instance_name('COUNTER')
    counter = client[counter_name]
    counter.TRIG_EDGE.put('Rising')
    counter.TRIG.put(f'{clock_name}.OUT')
    counter.TRIG.DELAY.put(5)
    counter.ENABLE.put('ONE')
    pcap.ENABLE.put('ONE')
    pcap.TRIG.put(f'{clock_name}.OUT')
    pcap.TRIG_EDGE.put('Rising')
    pcap.GATE.put('ONE')
    pcap.TS_TRIG.CAPTURE.put('No')


def handle_pcap(client, args):
    n_samples = args.n_samples
    client.disable_captures()
    pcap = client.PCAP
    counter_name = client.get_first_instance_name('COUNTER')
    counter = client[counter_name]
    counter.OUT.CAPTURE.put('Value')
    client.arm()
    last_time = 0
    PRINT_PERIOD = 3
    i = 0
    for data in client.collect():
        adata = np.frombuffer(data, dtype=np.uint32)
        for j in range(len(adata)):
            expected = (i + j) & 0xffffffff
            assert adata[j] == expected, \
                f'Entry {i + j} = {adata[j]}, expected {expected}'

        i += len(adata)
        if i >= n_samples:
            break

        current_time = time.time()
        if current_time - last_time > PRINT_PERIOD:
            last_time = current_time
            print(f'Checked a total of {i} lines, last entry {adata[-1]}')

    pcap.ENABLE.put('ZERO')
    print(f'Checked {i} lines')


def main():
    args = parse_args()
    client = PandaClient(args.host)
    client.connect()
    configure_layout(client, args)
    handle_pcap(client, args)
    client.close()


if __name__ == '__main__':
    main()
