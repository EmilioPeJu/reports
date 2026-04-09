# (draft) Pandabox2 Test Plan
NOTE: This plan has been mapped to [tickets](https://github.com/PandABlocks/PandABlocks-FPGA/issues?q=state%3Aopen%20label%3A%22PandABox2%20Prototype%20Testing%22).

In order to follow this test plan, first all the carrier blocks must be added
to target pandabox2, including digital inputs, digital outputs and encoders.
Some tests also require the full implementation of the displays, at least
driver and device tree nodes.

## Digital Outputs (repeat for each one)
- Manually toggle each digital output and confirm it physically changes. Check
  that the voltage level matches the electrical signaling used.
- Plug a Clock block at minimum period to each digital output and check signal
  on the scope, a 62.5MHz square wave is expected.
- (only for LVDSOUTs) Test fine delay following
  [this tutorial](https://pandablocks.github.io/main/how-to/finedelay-test.html).

## Digital input (repeat for each one)
- Plug a digital output to the digital input physically, manually toggle the
  output and confirm the input block senses the change.
- Keeping the last setup, plug a clock block to the output and to counter1,
  connect the input to counter2, use a calc block to subtract the two counters,
  then set minimum period and verify that the calc value is constant.
- Plug a signal generator to the digital input, then set a slow square wave to be
  at the limit of the logic electrical standard used, for example, for TTL it
  would be low=0.8V high=2V, then confirm the input changes in the web interface.
  This test can be repeated with higher frequency and counters.

## Encoders (for each one)
- Test that the counts in the motors controller and in the encoder block matches
  or it's different by a constant. Move the motor and make sure it still in
  sync.
- Set up a real acquisition scenario with motor, camera and sample, confirm that
  data obtained is equal(or close enough) to the obtained using a pandabox.

## Bandwidth requirements
- Test maximum raw bandwidth with iperf, should be better than with pandabox.
- Test maximum PCAP bandwidth by using a clock block to trigger both a counter
  and PCAP then do successive acquisitions reducing period until overrun
  occurs. Make sure the switch/router/NIC on the other end is not limiting. This
  should be better than with pandabox.
- Test sequencer block streaming tables can do 16MB/s (1MHz trigger),
  [helper script](./scripts/seq.py) provided for convenience.

## Misc Interfaces
- Plug a JTAG programmer and verify it works.
- Use a python script to write on the frame buffer of both displays, toggle a
  few pixels as quickly as possible and physically check that meets the >=10Hz
  requirement(not sure if just timing the write loop will provide that
  information too).
- Repeat the last test using a FMC with an extension that requires periodical
  I2C access, verify that there is no conflict and doesn't significantly affect
  the refresh rate of both displays.
- Verify the SFP by setting up a simple scenario, like mirroring a clock, with
  `sfp_panda_sync`, with a neighbor pandabox or/and with a loopback.

## FMC\_ACQ427 (for each channel and gain)
- Plug a signal generator configured with a sine wave, do a PCAP capture and
  plot the data, confirming it matches the source sine wave.

## CPU
- Run infinite loops (one per core) for some time, monitor temperature of the
  cores and stability, e.g. whether system freezes or there is a power glitch.
  This can be done with `stress-ng --cpu 2`, adding some flags you can stress
  memory and disk too.
- Repeat the last test while running a PCAP acquisition and verify the data is
  correct and that there were no underruns(do we want to guarantee some specific
  bandwidth in the scenario of high CPU load?).
