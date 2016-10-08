#!/usr/bin/python3

from optparse import OptionParser
import usb
import sys

USB_REQUEST_TYPE = 0x21                   # Host To Device | Class | Interface
USB_REQUEST = 0x09                        # SET_REPORT

USB_VALUE = 0x0300
USB_INDEX = 0x2
USB_INTERFACE = 2

VENDOR_ID = 0x1532                        # Razer
PRODUCT_ID_BLACK_WIDOW = 0x010e           # BlackWidow
PRODUCT_ID_BLACK_WIDOW_ULTIMATE = 0x011a  # BlackWidow Ultimate
PRODUCT_ID_BLACK_WIDOW_2013 = 0x011b      # BlackWidow 2013/2014

PRODUCTS = [("Black Widow", PRODUCT_ID_BLACK_WIDOW),
            ("Black Widow Ultimate", PRODUCT_ID_BLACK_WIDOW_ULTIMATE),
            ("Black Widow 2013/2014", PRODUCT_ID_BLACK_WIDOW_2013)]

LOG=sys.stderr.write

class BlackWidow(object):
	def __init__(self):
		self.kernel_driver_detached = False
		self.interface_claimed = False
		self.detected_keyboard = None

		self.find_device()
		if self.device_found():
			self.claim_interface()

	def __del__(self):
		if self.interface_claimed:
			self.release_interface()

	def find_device(self):
		for product_name, product_id in PRODUCTS:
			self.device = usb.core.find(idVendor=VENDOR_ID, idProduct=product_id)
			if self.device:
				detected_keyboard = product_id
				LOG("Found device: %s\n" % product_name)
				break

	def device_found(self):
		return self.device is not None

	def claim_interface(self):
		try:
			if self.device.is_kernel_driver_active(USB_INTERFACE):
				LOG("Kernel driver active; detaching it\n")

			self.device.detach_kernel_driver(USB_INTERFACE)
			self.kernel_driver_detached = True

			LOG("Claiming interface\n")
			usb.util.claim_interface(self.device, USB_INTERFACE)
			self.interface_claimed = True
		except:
			LOG("Unable to claim interface. Ensure the script is running as root.\n")
			raise

	def release_interface(self):
		if self.interface_claimed:
			LOG("Releasing claimed interface\n")
			usb.util.release_interface(self.device, USB_INTERFACE)

			if self.kernel_driver_detached:
				LOG("Reattaching the kernel driver\n")
				self.device.attach_kernel_driver(USB_INTERFACE)

	def format_command(self, command):
		from functools import reduce
		c1 = bytes.fromhex(command)
		c2 = [ reduce(int.__xor__, c1) ]
		b = [0] * 90
		b[5:5+len(c1)] = c1
		b[-2:-1] = c2
		return bytes(b)

	def send(self, command):
		def internal_send(msg):
			USB_BUFFER = self.format_command(command)
			result = 0
			try:
				result = self.device.ctrl_transfer(USB_REQUEST_TYPE, USB_REQUEST, wValue=USB_VALUE, wIndex=USB_INDEX, data_or_wLength=USB_BUFFER)
			except:
				sys.stderr.write("Could not send data\n")
			if result == len(USB_BUFFER):
				LOG("Data sent successfully\n")
			return result

		if isinstance(command, list):
			for i in command:
				print(' >> {}\n'.format(i))
				internal_send(i)
		elif isinstance(command, str):
			internal_send(command)

def main():
	#
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

	bw = BlackWidow()
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

	else:
		LOG("No device found\n")

if __name__ == '__main__':
	main()
