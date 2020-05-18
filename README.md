# HIDeous - switching keyboard RGB underglow to match the label of the active VM in Qubes.

## What?

Qubes is a security-focused OS based on the Xen hypervisor. It allows you to create isolated VMs and closely control how they interact with each other, the system hardware, and the outside world. Typically this is used to create systems with multiple security levels. To visually distinguish which level a given VM's application windows belong to, VMs can be assigned a color that is used for window decorations. So, for example, a VM that you use to safely open scary-looking email attachments could be assigned red for **DANGER!!!**, while a VM with no network access that you use to store your password manager database could be assigned black, as a reference to the void whence all attempts at communication would be consigned.

Keyboards with fancy RGB lighting are readily accessible these days - the code in this repo is an experiment in using one to provide an extra security level indicator, by switching the underglow lighting to match the colour of the active Qubes VM. A rev4 Keebio Iris is being used here, but any keyboard with controllable underglow should work.

## How?

To get this working, three components need to be set up:

- The keyboard firmware needs to be updated to handle raw HID messages - see a basic example in my [qmk_firmware fork](https://github.com/zenmonkeykstop/qmk_firmware/commit/3c858b6e515d681cd52fba2b54fafd76402de9ac#diff-86e342410bc75a347d38da0a87edf2dbR132).
- USB keyboards need to be enabled in Qubes, and the host control program (`hideous.py` in this repo) and associated dependencies need to be added in the `sys-usb` Qubes VM.
- Some means of triggering the host control program whenever the active window changes needs to be added in `dom0`. A quick-n-dirty bash script can do the trick for the purpose of experimentation, but a more robust solution would probably require something that either listened for window manager events (like i3ipc-python) or polled the WM at pretty frequent intervals.

## Is this even a good idea?
From a security perspective, there are some points worth considering:

- USB keyboards are frowned upon in Qubes for [a bunch of reasons](https://www.qubes-os.org/doc/device-handling-security/#security-warning-on-usb-input-devices). 
- Customization of `dom0` is also frowned upon, as  `dom0` has privileged access to everything in the system. 
- Customizing your keyboard's firmware implies a level of trust in the firmware toolchain - but you do get the ability to audit said firmware if so inclined. (Who does this, though?)
- Obviously, this will make your active VM label visible to any passive observer using MK1 eyeball tech.


## Setup

### Flashing the keyboard firmware

TK ( or see @qmk/qmk_firmware )

### Configuring sys-usb 
- Back up `sys-usb`, jussst in case.
- Enable USB keyboard support following [these instructions](https://www.qubes-os.org/doc/usb-qubes/#enable-a-usb-keyboard-for-login) - note that there are 2 paths here, the simple (enable the keyboard for everything including login/LUKS password entry) and the paranoid (enable it for everything but that and prompt for dom0 use).
- Install hidapi, virtualenv, virtualenvrwapper, and its dependencies (`sudo dnf install hidapi python3-virtualenv python3-virtualenvrwapper`) in the `fedora-30` template and restart `sys-usb`
- Create a `hideous` Python3 virtualenv, and install the python3 `hid` module - I did this  by *temporarily* giving `sys-usb` network access, but for a working system, you should find a safer way!
- Clone this repo in a network-attached VM and copy the `hideous.py` script to `sys-usb`.
- Add a udev rule allowing hidraw access for your keyboard in `sys-usb`:
  - Create a file `/rw/config/keebio.rules` with the following contents:
    ```
    KERNEL=="hidraw*", ATTRS{idVendor}=="cb10", ATTRS{idProduct}=="4256", MODE="0666"
    ```
  - Append the following two lines to `/rw/config/rc.local`:
    ```
    ln -s /rw/config/keebio.rules /etc/udev/rules.d
    udevadm control --reload
    ```
  - make `rc.local` executable (`sudo chmod +x /rw/config/rc.local`) and run it once (`sudo /rw/config/rc.local`)
- Plug in the keyboard. For the Iris, 4 `/dev/hidraw*` devices are created. Figure out which one gives you RGB control and sub it into the `DEVICE_PATH` definition in the `hideous.py` script - **TODO: autodetect the correct device in the script! Otherwise you have to do this step each time you restart sys-usb, as it may change depending on the order in which devices are connected.**
-  Test it out by running `source ~/.virtualenvs/hideous/bin/activate && python3 hideous.py --color red && deactivate` - you should see the RGB underglow change! If not, good luck - `lsusb -t` and `dmesg` are your new best friends.
   
### Configuring dom0
- Once you've got the `sys-usb` configuration working, with the usual provisos that copying files to `dom0` is not a good practice and done at your own risk, copy `dom0-focus-spy.sh` from this repo to `dom0` with the following command in a `dom0` terminal (assuming you checked it out in the default homedir of a VM named `work`):
  ```
  qvm-run --pass-io work "cat /home/user/hideous/dom0-focus-spy.sh" > dom0-focus-spy.sh
  ```
- Then, run the script in the background and try switching focus between windows! (Note that this script will only work with i3.)


## What would take for this to not suck?

This code **SHOULD NOT BE USED IN PRODUCTION**, as it has a lot of rough edges and virtually no error-checking. Some attributes that a production-ready version of this would have include:

- support for XFCE (or any WM)
- auto-detection of the correct `hidraw*` device in  the host control script.
- decent error-handling in the host control script, including an expansion of the communication protocol (it's almost a joke to call it that right now) to allow for acknowledgements and status updates from the keyboard. It currently just echos back the data it was sent for testing purposes, but no reason it couldn't send success/failure responses.
- a packaged version of the host control script, including dependencies and udev rules, to make it less hairy to set up.
- daemonization of the host control program, and some sort of queueing system to manage rapid updates from dom0. 
- a more robust method of monitoring focus changes and sending messages to `sys-usb` - `i3` has `i3ipc`, something similar to that that would allow the focus spy to register for interesting events would be nice.

