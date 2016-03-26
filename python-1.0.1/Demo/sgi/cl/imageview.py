# View a compressed image file in a GL window.
#
# This program shows how to use the Compression Library to view a
# compressed image and how to get relevant parameters from the image file.
#
# Instead of specifying the CL.ORIENTATION as CL.BOTTOM_UP, we could
# also have used the call gl.pixmode(GL.PM_TTOB, 1)
#
# An alternative way of decompressing a compressed image would be to use
# DecompressImage(), but this requires that the size of the image be
# known beforehand.  The call would be:
# image = cl.DecompressImage(scheme, width, height, CL.RGBX, filep.read())

def imageview(file):
	import cl, CL, gl, GL, DEVICE

	filep = open(file, 'r')
	header = filep.read(16)
	filep.seek(0)
	scheme = cl.QueryScheme(header)
	decomp = cl.OpenDecompressor(scheme)
	headersize = cl.QueryMaxHeaderSize(scheme)
	header = filep.read(headersize)
	filep.seek(0)
	headersize = decomp.ReadHeader(header)
	width = decomp.GetParam(CL.IMAGE_WIDTH)
	height = decomp.GetParam(CL.IMAGE_HEIGHT)
	params = [CL.ORIGINAL_FORMAT, CL.RGBX, \
		  CL.ORIENTATION, CL.BOTTOM_UP, \
		  CL.FRAME_BUFFER_SIZE, width*height*CL.BytesPerPixel(CL.RGBX)]
	decomp.SetParams(params)

	image = decomp.Decompress(1, filep.read())
	filep.close()
	decomp.CloseDecompressor()

	gl.foreground()
	gl.prefsize(width, height)
	win = gl.winopen(file)
	gl.RGBmode()
	gl.pixmode(GL.PM_SIZE, 32)
	gl.gconfig()
	gl.qdevice(DEVICE.REDRAW)
	gl.qdevice(DEVICE.ESCKEY)
	gl.qdevice(DEVICE.WINQUIT)
	gl.qdevice(DEVICE.WINSHUT)
	gl.lrectwrite(0, 0, width-1, height-1, image)
	while 1:
		dev, val = gl.qread()
		if dev in (DEVICE.ESCKEY, DEVICE.WINSHUT, DEVICE.WINQUIT):
			break
		if dev == DEVICE.REDRAW:
			gl.lrectwrite(0, 0, width-1, height-1, image)
	gl.winclose(win)

def main():
	import sys
	if len(sys.argv) != 2:
		print 'Usage: imageview file'
		sys.exit(2)
	imageview(sys.argv[1])

main()
