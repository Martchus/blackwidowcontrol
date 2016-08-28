#!/usr/bin/python3

from optparse import OptionParser
import usb
import sys

VENDOR_ID = 0x1532  # Razer
PRODUCT_ID_BLACK_WIDOW = 0x010e # BlackWidow / BlackWidow Ultimate
PRODUCT_ID_BLACK_WIDOW_2013 = 0x011b # BlackWidow 2013

USB_REQUEST_TYPE = 0x21  # Host To Device | Class | Interface
USB_REQUEST = 0x09  # SET_REPORT

USB_VALUE = 0x0300
USB_INDEX = 0x2
USB_INTERFACE = 2

LOG=sys.stderr.write

class blackwidow(object):
	kernel_driver_detached = False
	detected_keyboard = None

	def __init__(self):
		self.device = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID_BLACK_WIDOW)

		if self.device is None:
			self.device = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID_BLACK_WIDOW_2013)
			if self.device is None:
				LOG("No device found\n")
				return
			else:
				LOG("Found device: Black Widow 2013\n")
				detected_keyboard = PRODUCT_ID_BLACK_WIDOW_2013
		else:
			LOG("Found device: Black Widow\n")
			detected_keyboard = PRODUCT_ID_BLACK_WIDOW

		if self.device.is_kernel_driver_active(USB_INTERFACE):
			LOG("Kernel driver active; detaching it\n")

		self.device.detach_kernel_driver(USB_INTERFACE)
		self.kernel_driver_detached = True

		LOG("Claiming interface\n")
		usb.util.claim_interface(self.device, USB_INTERFACE)

	def __del__(self):
		if self.device_found():
			LOG("Releasing claimed interface\n")
			usb.util.release_interface(self.device, USB_INTERFACE)

			if self.kernel_driver_detached:
				LOG("Reattaching the kernel driver\n")
				self.device.attach_kernel_driver(USB_INTERFACE)
			LOG("Done.\n")

	def bwcmd(self, c):
		from functools import reduce
		c1 = bytes.fromhex(c)
		c2 = [ reduce(int.__xor__, c1) ]
		b = [0] * 90
		b[5:5+len(c1)] = c1
		b[-2:-1] = c2
		return bytes(b)

	def device_found(self):
		return self.device is not None

	def send(self, c):
		def _send(msg):
			USB_BUFFER = self.bwcmd(msg)
			result = 0
			try:
				result = self.device.ctrl_transfer(USB_REQUEST_TYPE, USB_REQUEST, wValue=USB_VALUE, wIndex=USB_INDEX, data_or_wLength=USB_BUFFER)
			except:
				sys.stderr.write("Could not send data\n")
			if result == len(USB_BUFFER):
				LOG("Data sent successfully\n")
			return result

		if isinstance(c, list):
			for i in c:
				print(' >> {}\n'.format(i))
				_send(i)
		elif isinstance(c, str):
			_send(c)

def main():
	init_new    = '0200 0403'
	init_old    = '0200 0402'
	no_pulsate  = '0303 0201 0400'
	pulsate     = '0303 0201 0402'
	brightness  = '0303 0301 04'
	backlight   = '0303 0301 05'
	gamemode    = '0303 0001 08'

	usage = "usage: %prog [options]"
	parser = OptionParser(usage=usage)
	parser.add_option("-i", "--init", action="store_true", dest="init", default=False, help="initiates the functionality of macro keys")
	parser.add_option("-l", "--set-led", type="string", dest="led", default="unmodified", help="sets the status of the led (pulsate, bright, normal, dim, off or number between 0 - 255)", metavar="STATUS")
	parser.add_option("-b", "--set-backlight", type="string", dest="backlight", default="unmodified", help="sets the status of the backlight (pulsate, bright, normal, dim, off or number between 0 - 255)")
	parser.add_option("-g", "--set-game-mode", type="string", dest="gamemode", default="unmodified", help="sets whether the game mode is enabled (on/off)")
	(options, args) = parser.parse_args()

	bw = blackwidow()
	if bw.device_found():
		# enable macro keys
		if options.init == True:
			LOG("Sending initiation command\n")
			bw.send(init_old)

		# set led status (doesn't work with BlackWidow 2016 yet)
		if options.led == "unmodified":
			pass
		elif options.led == "pulsate":
			LOG("Sending led pulsate command\n")
			bw.send(pulsate)
		elif options.led == "bright":
			LOG("Sending no pulsate command and led bright command\n")
			bw.send(no_pulsate)
			bw.send(brightness + 'FF')
		elif options.led == "normal":
			LOG("Sending no pulsate command and led normal command\n")
			bw.send(no_pulsate)
			bw.send(brightness + 'a8')
		elif options.led == "dim":
			LOG("Sending no pulsate command and led dim command\n")
			bw.send(no_pulsate)
			bw.send(brightness + '54')
		elif options.led == "off":
			LOG("Sending no pulsate command and led off command\n")
			bw.send(no_pulsate)
			bw.send(brightness + '00')
		else:
			try:
				brightness_level = int(options.led)
				if brightness_level >= 0 and brightness_level <= 0xFF:
					LOG("Sending no pulsate command and led command with custom brightness\n")
					bw.send(no_pulsate)
					bw.send(brightness + "{0:#0{1}x}".format(brightness_level,4)[2:])
				else:
					raise ValueError
			except ValueError:
				LOG("Specified value for led status \"%s\" is unknown and will be ignored.\n" % options.led)

		# experimantal: set backlight (BlackWidow 2016 only)
		if options.backlight == "unmodified":
			pass
		else:
			if False: # condition for BlackWidow 2016
				if options.backlight == "bright":
					LOG("Sending blacklight command\n")
					bw.send(backlight + 'FF')
				elif options.backlight == "normal":
					LOG("Sending blacklight command\n")
					bw.send(backlight + 'a8')
				elif options.backlight == "dim":
					LOG("Sending blacklight command\n")
					bw.send(backlight + '54')
				elif options.backlight == "off":
					LOG("Sending blacklight command\n")
					bw.send(backlight + '00')
				else:
					try:
						brightness_level = int(options.backlight)
						if brightness_level >= 0 and brightness_level <= 0xFF:
							bw.send(brightness + "{0:#0{1}x}".format(brightness_level,4)[2:])
						else:
							raise ValueError
					except ValueError:
						LOG("Specified value for backlight status \"%s\" is unknown and will be ignored.\n" % options.led)
			else:
				LOG("Setting the backlight is not supported by the detected keyboard.")

		# enable/disable game mode
		if options.gamemode == "unmodified":
			pass
		elif options.gamemode == "on":
			bw.send(gamemode + '01')
		elif options.gamemode == "off":
			bw.send(gamemode + '00')
		else:
			LOG("Specified value for game mode is unknown and will be ignored.\n")

if __name__ == '__main__':
	main()
