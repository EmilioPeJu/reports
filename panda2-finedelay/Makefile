TOP := $(CURDIR)
PYTHON = python
BUILD_DIR = build
include CONFIG

test:
	panda_src_dir=$(FPGA) \
	    $(PYTHON) dev-tests/test_oct_finedelay.py
