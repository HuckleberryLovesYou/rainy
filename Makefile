PREFIX ?= /usr/local/bin
RAINY_DIR = $(PREFIX)/rainy

install:
	install -d $(RAINY_DIR)
	cp -r src/* $(RAINY_DIR)/
	chmod +x $(RAINY_DIR)/rainy.py
	ln -sf $(RAINY_DIR)/__main__.py $(PREFIX)/rainy

uninstall:
	rm -f $(PREFIX)/rainy
	rm -rf $(RAINY_DIR)
	@if [ -n "$$SUDO_USER" ]; then \
		rm -rf /home/$$SUDO_USER/.rainy; \
	else \
		rm -rf $(HOME)/.rainy; \
	fi
