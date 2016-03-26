# Compress an RGB image using JPEG.
#
# This program shows how to use the Compression Library to compress an
# RGB image with JPEG.
#
# An alternative way of compressing would be to use CompressImage(),
# but since the order of the scan lines in an RGB file is
# bottom-to-top and in a JPEG image top-to-bottom, we need to use the
# CL.ORIENTATION parameter.  This cannot be done using
# CompressImage().  The call would be:
# data = cl.CompressImage(CL.JPEG, width, height, orig, 15.0, iamge)

Error = 'rgbtojpeg.error'

def readrgb(file):
	import imgfile

	width, height, depth = imgfile.getsizes(file)
	data = imgfile.read(file)
	return width, height, depth, data

def cjpeg(width, height, depth, image, quality):
	import cl, CL

	if depth == 3:
		orig = CL.RGBX
	elif depth == 1:
		orig = CL.RGB332
	elif depth == 4:
		orig = CL.RGBA
	else:
		raise Error, 'unrecognized depth'
	params = [CL.ORIGINAL_FORMAT, orig, \
		  CL.ORIENTATION, CL.BOTTOM_UP, \
		  CL.IMAGE_WIDTH, width, \
		  CL.IMAGE_HEIGHT, height, \
		  CL.QUALITY_FACTOR, quality]
	comp = cl.OpenCompressor(CL.JPEG)
	comp.SetParams(params)
	data = comp.Compress(1, image)
	comp.CloseCompressor()
	return data

def main():
	usage = 'cjpeg [-Q quality] filename [outfilename]'
	import sys, getopt
	try:
		options, args = getopt.getopt(sys.argv[1:], 'Q:')
	except getopt.error:
		print usage
		sys.exit(2)
	quality = 75
	for argpair in options:
		import string
		if argpair[0] == '-Q':
			try:
				quality = string.atoi(argpair[1])
			except string.atoi_error:
				print usage
				sys.exit(2)
	if len(args) not in (1, 2):
		print usage
		sys.exit(2)
	if len(args) == 2:
		outfile = open(args[1], 'w')
	else:
		outfile = sys.stdout

	width, height, depth, image = readrgb(args[0])
	outfile.write(cjpeg(width, height, depth, image, quality))

main()
