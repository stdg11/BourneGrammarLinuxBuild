#!/bin/sh
if [ -z "$1" ]; then
    export EDITOR=$0 && sudo -E visudo
else
    echo "%linuxadmins ALL=(ALL:ALL) ALL" >> $1
    echo "%users  localhost=/sbin/poweroff" >> $1
    echo "%users  localhost=/sbin/reboot" >> $1
fi
