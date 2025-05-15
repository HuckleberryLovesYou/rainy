PREFIX ?= /usr/local
BINDIR = $(PREFIX)/bin

install:
	install -d $(BINDIR)
	install -m 755 src/rainy.py $(BINDIR)/rainy
	install -m 644 src/rainy.conf.ini $(BINDIR)/rainy.conf.ini
	chmod +x $(BINDIR)/rainy

uninstall:
	rm -f $(BINDIR)/rainy
	rm -f $(BINDIR)/rainy.conf.ini
