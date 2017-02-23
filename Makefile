# Makefile for CGI/SHell Media Box
#

PACKAGE="mediabox"
DESTDIR?=
PREFIX?=/usr
CGI_BIN?=/var/www/cgi-bin
LINGUAS?=fr

all: msgfmt

pot:
	xgettext -o po/mediabox.pot -L Shell --package-name="MediaBox" \
		./index.cgi ./mediabox

msgmerge:
	@for l in $(LINGUAS); do \
		echo -n "Updating $$l po file."; \
		msgmerge -U po/$$l.po po/$(PACKAGE).pot; \
	done;

msgfmt:
	@for l in $(LINGUAS); do \
		echo "Compiling $$l mo file..."; \
		mkdir -p po/mo/$$l/LC_MESSAGES; \
		msgfmt -o po/mo/$$l/LC_MESSAGES/$(PACKAGE).mo po/$$l.po; \
	done;

install:
	install -m 0755 -d $(DESTDIR)$(PREFIX)/bin
	install -m 0755 -d $(DESTDIR)$(PREFIX)/share/applications
	install -m 0755 mediabox $(DESTDIR)$(PREFIX)/bin
	install -m 0644 data/mediabox.desktop $(DESTDIR)$(PREFIX)/share/applications
	# Web interface
	install -m 0755 -d $(DESTDIR)$(CGI_BIN)/mediabox
	install -m 0777 -d $(DESTDIR)$(CGI_BIN)/mediabox/cache
	install -m 0755 index.cgi $(DESTDIR)$(CGI_BIN)/mediabox
	cp -r images/ $(DESTDIR)$(CGI_BIN)/mediabox
	cp -r lib/ $(DESTDIR)$(CGI_BIN)/mediabox
	cp README $(DESTDIR)$(CGI_BIN)/mediabox
	# i18n
	install -m 0777 -d $(DESTDIR)$(PREFIX)/share/locale
	cp -a po/mo/* $(DESTDIR)$(PREFIX)/share/locale
	
uninstall:
	rm -f $(DESTDIR)$(PREFIX)/bin/mediabox
	rm -rf $(DESTDIR)$(CGI_BIN)/mediabox
	rm -f $(DESTDIR)$(PREFIX)/share/locale/*/mediabox.mo

clean:
	rm -rf po/*~
	rm -rf po/mo
