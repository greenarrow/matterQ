PREFIX ?= /usr/local
BINDIR ?= $(PREFIX)/bin
MANDIR ?= $(PREFIX)/share/man
EXEDIR ?= $(PREFIX)/libexec
ETCDIR ?= /etc
TMPDIR ?= /tmp

INSTALL ?= install

packages:
	echo "Installing system packages"
	apt-get update
	apt-get install libncurses-dev wireless-tools usbutils lprng byobu

filter:
	echo "Installing matterQ lnrng filter"
	$(INSTALL) -d $(DESTDIR)$(EXEDIR)/filters
	$(INSTALL) -m 0755 scripts/matterq-lprng \
		$(DESTDIR)$(EXEDIR)/filters

config:
	print "System configuration"
	$(INSTALL) -d $(DESTDIR)$(ETCDIR)/lprng
	$(INSTALL) -m 0644 config/printcap $(DESTDIR)$(ETCDIR)
	$(INSTALL) -m 0644 config/lpd.conf $(DESTDIR)$(ETCDIR)/lprng
	$(INSTALL) -m 0644 config/lpd.perms $(DESTDIR)$(ETCDIR)/lprng
        
	usermod -a -G pi dialout
	usermod -a -G daemon dialout

wifi:
	print "WiFi configuration"
	$(INSTALL) -d $(DESTDIR)$(ETCDIR)/network
	$(INSTALL) -m 0644 config/wpa.conf $(DESTDIR)$(ETCDIR)
	$(INSTALL) -m 0644 config/interfaces $(DESTDIR)$(ETCDIR)/network
	print "Now edit /etc/wpa.conf and enter your ssid and psk:"
	print "  $ sudo vim /etc/wpa.conf"
	print "  OR"
	print "  $ sudo nano /etc/wpa.conf"

all: packages filter config


