PREFIX ?= /usr/local
BINDIR ?= $(PREFIX)/bin
MANDIR ?= $(PREFIX)/share/man
EXEDIR ?= $(PREFIX)/libexec
VARDIR ?= /var
ETCDIR ?= /etc
TMPDIR ?= /tmp
BOOTDIR ?= /boot

PIHOME ?= /home/pi

INSTALL ?= install

.PHONY: packages filter web sysconfig wifi imageprune imageclean

packages:
	# Installing system packages
	apt-get update
	apt-get install -y libncurses-dev wireless-tools usbutils lprng byobu \
		lighttpd vim

filter:
	# Installing matterQ lnrng filter
	$(INSTALL) -d $(DESTDIR)$(EXEDIR)/filters
	$(INSTALL) -m 0755 scripts/matterq-lprng \
		$(DESTDIR)$(EXEDIR)/filters

web:
	$(INSTALL) -d $(DESTDIR)$(VARDIR)/www/cgi-bin
	$(INSTALL) -d $(DESTDIR)$(VARDIR)/www/media/css
	$(INSTALL) -d $(DESTDIR)$(VARDIR)/www/media/js
	$(INSTALL) -d $(DESTDIR)$(VARDIR)/www/media/images
	$(INSTALL) -m 0755 web/index.py $(DESTDIR)$(VARDIR)/www/cgi-bin
	$(INSTALL) -m 0644 web/media/css/style.css $(DESTDIR)$(VARDIR)/www/media/css
	$(INSTALL) -m 0644 web/media/js/common.js $(DESTDIR)$(VARDIR)/www/media/js
	$(INSTALL) -m 0644 web/media/images/tick32.png $(DESTDIR)$(VARDIR)/www/media/images
	$(INSTALL) -m 0644 web/media/images/stop32.png $(DESTDIR)$(VARDIR)/www/media/images

sysconfig:
	# System configuration
	$(INSTALL) -d $(DESTDIR)$(ETCDIR)/lprng
	$(INSTALL) -d $(DESTDIR)$(ETCDIR)/profile.d
	$(INSTALL) -d $(DESTDIR)$(BOOTDIR)
	$(INSTALL) -m 0644 config/motd $(DESTDIR)$(ETCDIR)
	$(INSTALL) -m 0644 config/printcap $(DESTDIR)$(ETCDIR)
	$(INSTALL) -m 0644 config/lpd.conf $(DESTDIR)$(ETCDIR)/lprng
	$(INSTALL) -m 0644 config/lpd.perms $(DESTDIR)$(ETCDIR)/lprng
	$(INSTALL) -m 0755 config/lighttpd.conf $(DESTDIR)$(ETCDIR)/lighttpd
	$(INSTALL) -m 0644 config/matterq.conf $(DESTDIR)$(BOOTDIR)
	$(INSTALL) -m 0755 scripts/matterq.sh $(DESTDIR)$(ETCDIR)/profile.d

	ln -sf $(DESTDIR)$(BOOTDIR)/matterq.conf $(DESTDIR)$(ETCDIR)

	cp $(DESTDIR)$(BOOTDIR)/arm240_start.elf $(DESTDIR)$(BOOTDIR)/start.elf

	usermod -a -G dialout pi
	usermod -a -G dialout daemon

wifi:
	# WiFi configuration
	$(INSTALL) -d $(DESTDIR)$(ETCDIR)/wpa_supplicant
	$(INSTALL) -d $(DESTDIR)$(BOOTDIR)
	$(INSTALL) -m 0644 config/wifi.conf \
		$(DESTDIR)$(BOOTDIR)
	ln -sf $(DESTDIR)$(BOOTDIR)/wifi.conf \
		$(DESTDIR)$(ETCDIR)/wpa_supplicant/wpa_supplicant.conf

imageprune:
	apt-get remove -y x11-common desktop-base gnome-icon-theme \
		gnome-themes-standard gpicview python3 lxde-common \
		lxde-icon-theme ttf-freefont fonts-freefont-ttf
	apt-get autoremove -y
	apt-get clean

	rm -fR /opt/vc
 
imageclean:
	apt-get clean

	rm -fR $(PIHOME)/.ssh $(PIHOME)/.aptitude $(PIHOME)/.byobu \
		$(PIHOME)/python_games $(PIHOME)/.screenrc

	dphys-swapfile swapoff
	dd if=/dev/zero of=/var/swap bs=1M count=100
	mkswap /var/swap

	find /var/log -type f | xargs rm

	rm -f $(PIHOME)/.bash_history

install: filter sysconfig packages


