# Makefile for pdfsizeopt3, the Python 3 version of pdfsizeopt.
#
# The program is installed as pdfsizeopt3, so it can coexist with the old
# Python 2 version installed as pdfsizeopt.
#
# Usage:
#   make                       # Build pdfsizeopt3.single.
#   make test                  # Run the unit tests.
#   make check                 # Unit tests + optimize a small PDF.
#   make install PREFIX=~      # Install to ~/bin/pdfsizeopt3.
#   make uninstall PREFIX=~
#   make clean

PYTHON ?= python3
PREFIX ?= /usr/local
BINDIR ?= $(PREFIX)/bin
DESTDIR ?=
INSTALL ?= install

PROGRAM = pdfsizeopt3
SINGLE = $(PROGRAM).single
SOURCES = lib/pdfsizeopt/__init__.py lib/pdfsizeopt/binstr.py \
    lib/pdfsizeopt/cff.py lib/pdfsizeopt/float_util.py \
    lib/pdfsizeopt/main.py lib/pdfsizeopt/psproc.py

.PHONY: all test check install uninstall clean

all: $(SINGLE)

$(SINGLE): mksingle.py $(SOURCES)
	$(PYTHON) mksingle.py

test:
	$(PYTHON) pdfsizeopt_test.py

# Optimizes a tiny PDF with the freshly built single-file script. Set
# PDFSIZEOPT_GS to test with a specific Ghostscript.
check: test $(SINGLE)
	$(PYTHON) $(SINGLE) --use-pngout=no --use-jbig2=no \
	    --do-require-image-optimizers=no extra/small.pdf check.tmp.pdf
	rm -f check.tmp.pdf

install: $(SINGLE)
	$(INSTALL) -d $(DESTDIR)$(BINDIR)
	$(INSTALL) -m 755 $(SINGLE) $(DESTDIR)$(BINDIR)/$(PROGRAM)

uninstall:
	rm -f $(DESTDIR)$(BINDIR)/$(PROGRAM)

clean:
	rm -f t.zip check.tmp.pdf
	rm -rf lib/pdfsizeopt/__pycache__
