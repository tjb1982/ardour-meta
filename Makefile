CONFIG_DIRS=$(shell find ~/.config -regex '.*ardour[0-9]+' -type d)
VERSION=0.1.0


all: install install_lua_scripts

install_lua_scripts:
	chmod +x ${PWD}/lua_scripts/*
	for d in ${CONFIG_DIRS}; do \
	    mkdir -p $$d/scripts/ ; \
	    cp -R ${PWD}/lua_scripts/* $$d/scripts/ ; \
	done

ardour_meta-${VERSION}-py3-none-any.whl:
	pip wheel .

install: install_lua_scripts ardour_meta-${VERSION}-py3-none-any.whl
	pip install ardour_meta-${VERSION}-py3-none-any.whl --force-reinstall

clean:
	find . -regex '.*ardour_meta-.*-py3-.*\.whl' -delete
	rm -rf ardour_meta.egg-info
	rm -rf ./build

.PHONY: all clean install install_lua_scripts
