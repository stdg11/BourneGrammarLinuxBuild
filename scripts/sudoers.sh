1#!/bin/sh
if [ -z "$1" ]; then
    export EDITOR=$0 && sudo -E visudo
else
    echo "includedir /etc/sudoers.d" >> $1
fi
