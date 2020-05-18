#!/usr/bin/env bash
while read -r line 
do
        WINDOW_ID="$(echo  $line | awk '/_NET_ACTIVE_WINDOW\(WINDOW\)/{print $NF}')"
        VMNAME=$(xprop -id $WINDOW_ID | awk '/_QUBES_VMNAME/{$1=$2="";print}' | cut -d'"' -f2)
        if [ -z "$VMNAME" ]; then
            COLOR="dom0"
        else
            COLOR=$(qvm-prefs $VMNAME label)
        fi
        qvm-run --quiet sys-usb "source ~/.virtualenvs/hideous/bin/activate && python3 hideous.py --color $COLOR && deactivate"
done < <(xprop -spy -root _NET_ACTIVE_WINDOW)
