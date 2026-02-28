#!/usr/bin/env python
import cocotb
import logging
import numpy as np
import random

from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ReadOnly, ClockCycles, Event, Timer
from cocotb_tools.runner import get_runner

from collections import deque
from common import get_panda_path, get_extra_path, get_top
from typing import Any, Sequence

PANDA_PATH = get_panda_path()
EXTRA_PATH = get_extra_path()
TOP_PATH = get_top()


@cocotb.test(skip=True)
async def can_run(dut):
    cocotb.start_soon(Clock(dut.clk_i, 4, 'ns').start(start_high=False))
    cocotb.start_soon(Clock(dut.clk_4x_i, 1, 'ns').start(start_high=False))
    await RisingEdge(dut.clk_i)


async def try_one_oct_delay(dut, oct_delay):
    start_high = True
    dut.signal_i.value = 0
    dut.clk_i.value = 0
    dut.clk_4x_i.value = 0
    await Timer(2, 'ns')
    cocotb.start_soon(
        Clock(dut.clk_4x_i, 2, 'ns').start(start_high=start_high))
    #await ClockCycles(dut.clk_4x_i, 2)
    cocotb.start_soon(
        Clock(dut.clk_i, 8, 'ns').start(start_high=start_high))
    dut.oct_delay_i.value = oct_delay 
    dut.signal_i.value = 0
    await ClockCycles(dut.clk_i, 4)
    for _ in range(4):
        dut.signal_i.value = int(dut.signal_i.value) ^ 1
        await RisingEdge(dut.clk_i)

    await ClockCycles(dut.clk_i, 2)


@cocotb.test()
async def simple_signal(dut):
    for oct_delay in range(8):
        await try_one_oct_delay(dut, oct_delay)


def test_oct_finedelay():
    logging.basicConfig(level=logging.DEBUG)
    runner = get_runner('ghdl')
    runner.build(sources=[
                     PANDA_PATH / 'common' / 'hdl_zynqmp' / 'oct_finedelay.vhd',
                 ],
                 build_args=[
                     '--std=08',
                     '-frelaxed',
                     # this was created by running:
                     # compile-xilinx-vivado.sh --unisim --vhdl2008
                     '-P=../xilinx-vivado/',
                 ],
                 build_dir='sim_oct_finedelay',
                 hdl_toplevel='oct_finedelay',
                 always=True,
                 verbose=True)
    runner.test(hdl_toplevel='oct_finedelay',
                test_args=[
                    '--std=08',
                     '-frelaxed',
                     '-P=../xilinx-vivado/',
                 ],
                plusargs = [
                    '--fst=sim_oct_finedelay.fst',
                ],
                verbose=True,
                test_module='test_oct_finedelay')


def main():
    test_oct_finedelay()


if __name__ == '__main__':
    main()
