PREFIX ?= /usr/local
BINDIR ?= $(PREFIX)/bin
MANDIR ?= $(PREFIX)/share/man
EXEDIR ?= $(PREFIX)/libexec
ETCDIR ?= /etc
TMPDIR ?= /tmp

INSTALL ?= install

packages:
	echo "Installing system packages"
	sudo apt-get update
	sudo apt-get install libncurses-dev wireless-tools usbutils lprng byobu

filter:
	echo "Installing matterQ lnrng filter"
	sudo $(INSTALL) -d $(DESTDIR)$(EXEDIR)/filters
	sudo $(INSTALL) -m 0755 scripts/matterq-lprng \
		$(DESTDIR)$(EXEDIR)/filters

config:
	print "System configuration"
	sudo $(INSTALL) -d $(DESTDIR)$(ETCDIR)/lprng
	sudo $(INSTALL) -m 0644 config/printcap $(DESTDIR)$(ETCDIR)
	sudo $(INSTALL) -m 0644 config/lpd.conf $(DESTDIR)$(ETCDIR)/lprng
	sudo $(INSTALL) -m 0644 config/lpd.perms $(DESTDIR)$(ETCDIR)/lprng

	usermod -a -G pi dialout
	usermod -a -G daemon dialout

wifi:
	print "WiFi configuration"
	sudo $(INSTALL) -d $(DESTDIR)$(ETCDIR)/network
	sudo $(INSTALL) -m 0644 config/wpa.conf $(DESTDIR)$(ETCDIR)
	sudo $(INSTALL) -m 0644 config/interfaces $(DESTDIR)$(ETCDIR)/network
	print "Now edit /etc/wpa.conf and enter your ssid and psk:"
	print "  $ sudo vim /etc/wpa.conf"
	print "  OR"
	print "  $ sudo nano /etc/wpa.conf"

all: packages filter config


