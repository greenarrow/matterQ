PREFIX ?= /usr/local
BINDIR ?= $(PREFIX)/bin
MANDIR ?= $(PREFIX)/share/man
EXEDIR ?= $(PREFIX)/libexec
ETCDIR ?= /etc
TMPDIR ?= /tmp

INSTALL ?= install

packages:
	# Installing system packages
	apt-get update
	apt-get install -y libncurses-dev wireless-tools usbutils lprng byobu

filter:
	# Installing matterQ lnrng filter
	$(INSTALL) -d $(DESTDIR)$(EXEDIR)/filters
	$(INSTALL) -m 0755 scripts/matterq-lprng \
		$(DESTDIR)$(EXEDIR)/filters

sysconfig:
	# System configuration
	$(INSTALL) -d $(DESTDIR)$(ETCDIR)/lprng
	$(INSTALL) -d $(DESTDIR)$(ETCDIR)/profile.d
	$(INSTALL) -m 0644 config/printcap $(DESTDIR)$(ETCDIR)
	$(INSTALL) -m 0644 config/lpd.conf $(DESTDIR)$(ETCDIR)/lprng
	$(INSTALL) -m 0644 config/lpd.perms $(DESTDIR)$(ETCDIR)/lprng
	$(INSTALL) -m 0755 config/austerusg.sh $(DESTDIR)$(ETCDIR)/profile.d

	usermod -a -G dialout pi
	usermod -a -G dialout daemon

wifi:
	# WiFi configuration
	$(INSTALL) -d $(DESTDIR)$(ETCDIR)/wpa_supplicant
	$(INSTALL) -m 0644 config/wpa_supplicant.conf \
		$(DESTDIR)$(ETCDIR)/wpa_supplicant

	# Now edit $(DESTDIR)$(ETCDIR)/wpa_supplicant/wpa_supplicant.conf and enter
	# your ssid and psk:
	#  $ sudo vim $(DESTDIR)$(ETCDIR)/wpa_supplicant/wpa_supplicant.conf
	#  OR
	#  $ sudo nano $(DESTDIR)$(ETCDIR)/wpa_supplicant.conf

install: filter sysconfig packages


