# This program converts a raw linear audio stream into a U-law stream.
# Input comes from standard input, output goes to standard output.
# Since in U-law the channels are encoded independently from each
# other and there is no dependence on the sampling frequency, we can
# get away with the frame rate of 8000 samples per second and telling
# the compressor that the data is mono.

import cl, CL

def lin2ulaw(infile, outfile, nchannels):
	comp = cl.OpenCompressor(CL.G711_ULAW)
	if nchannels == 1:
		orig = CL.MONO
	elif nchannels == 2:
		orig = CL.STEREO_INTERLEAVED
	# The important parameters are ORIGINAL_FORMAT and the two
	# sizes.  The FRAME_RATE doesn't matter in U-law, and the
	# BITS_PER_COMPONENT is 16 by default.
	# Notice that the COMPRESSED_BUFFER_SIZE is twice the needed
	# size.
	params = [CL.ORIGINAL_FORMAT, orig, \
		  CL.BITS_PER_COMPONENT, 16, \
		  CL.FRAME_RATE, 8000, \
		  CL.FRAME_BUFFER_SIZE, 8192, \
		  CL.COMPRESSED_BUFFER_SIZE, 8192]
	comp.SetParams(params)
	dummy = comp.Compress(0, '')
	while 1:
		audio = infile.read(8192)
		if not audio:
			break
		data = comp.Compress(len(audio) / (nchannels * 2), audio)
		outfile.write(data)
	comp.CloseCompressor()

def main():
	import sys

	lin2ulaw(sys.stdin, sys.stdout, 1)
