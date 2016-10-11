# BlackWidow control
Python 3 script to enable macro keys of BlackWidow keyboard under GNU/Linux

It just enables the macro keys which can then be configured as hotkeys in your desktop environment.
However, it does not enable the ability to record macros and to switch between different configurations
like the Windows driver does.

For recording macros under X11 one might use [xmacro](http://download.sarine.nl/xmacro/Description.html)
or [xdotool](http://www.semicomplete.com/projects/xdotool/).

## Supported devices
The script is know to work with the following BlackWidow editions:
- regular edition (the ceapest one which has no background light)
- the regular 2013 edition
- BlackWidow Ultimate Stealth 2014

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
- The repository [PKGBUILDs](https://github.com/Martchus/PKGBUILDs) contains files
  for building an Arch Linux package.
