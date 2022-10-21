CONFIG_DIR=$(shell find ~/.config -regex '.*ardour[0-9]+' -type d | head -1)
VERSION=0.0.1


all: install install_lua_scripts

install_lua_scripts:
	chmod +x ${PWD}/lua_scripts/*
	cp -R ${PWD}/lua_scripts/* ${CONFIG_DIR}/scripts/

ardour_meta-${VERSION}-py3-none-any.whl:
	pip wheel .

install: install_lua_scripts ardour_meta-${VERSION}-py3-none-any.whl
	pip install ardour_meta-${VERSION}-py3-none-any.whl --force-reinstall

clean:
	rm -f ardour_meta-${VERSION}-py3-none-any.whl

.PHONY: all clean install install_lua_scripts
