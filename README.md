# BlackWidow control
Python 3 script to enable macro keys of BlackWidow keyboard under GNU/Linux

It just enables the macro keys which can then be configured as hotkeys in your desktop environment.
However, it does not enable the ability to record macros and to switch between different configurations
like the Windows driver does.

For recording macros under X11 one might use [xmacro](http://download.sarine.nl/xmacro/Description.html)
or [xdotool](http://www.semicomplete.com/projects/xdotool/).

## Supported devices
The script is known to work with the following BlackWidow editions:
- regular edition (the ceapest one which has no background light)
- the regular 2013 edition
- BlackWidow Ultimate Stealth 2014
- BlackWidow Ultimate 2012
- BlackWidow Chroma V2

If you can confirm that those or other devices work or don't work, let me now by editing this file.

### Notes
- The script does not work with the 2016 editions (yet).
- The script has been tested using the firmware update from Razer Synapse 2.0.
  Hence the script might not work when an older firmware version is used.

## Instructions
- Pyusb is required to run the script.
- Use ```-h``` for a list of available options.
- To invoke the script automatically when the keyboard is plugged-in an udev
  rule can be added (see ```razer_blackwidow.rules```).

## Packages
- Arch Linux: [AUR](https://aur.archlinux.org/packages/blackwidowcontrol),
  [PKGBUILDs](https://github.com/Martchus/PKGBUILDs), [binary repository](https://martchus.no-ip.biz/repo/arch/ownstuff)
- openSUSE and Fedora:
  [OBS](https://software.opensuse.org//download.html?project=home%3Amkittler&package=blackwidowcontrol)

## Copyright notice and license
The script itself is based on https://finch.am/projects/blackwidow. While the
original license is unspecified, the author makes it clear that using and
modified the code is permitted (and even encouraged):

> 2020-08-27 Relatives and descendents of this code have been available in
various places for many years now, and are probably better maintained. Check
your distribution's package manager!

---

Copyright © 2012 [finch.am](https://finch.am)
Copyright © 2015-2022 Marius Kittler

All additions and modifications to the original code are licensed under
[GPL-2-or-later](LICENSE).
