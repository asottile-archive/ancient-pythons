

# merge src into dst.  Assumptions: src and dst are sorted
def mergein(dst, src):
	srclen, dstlen = len(src), len(dst)
	srcidx, dstidx = 0, 0
	for srcitem in src:
		# while there are elements to insert
		while dstidx < dstlen and dst[dstidx] < srcitem:
			dstidx = dstidx + 1
		dst.insert(dstidx, srcitem)
		dstlen = dstlen + 1

# return the merge of s1 and s2.  Assumptions: s1 and s2 are sorted
def merge(s1, s2):
	# this could be made faster
	result = s1[:]			# make a real copy of s1
	mergein(result, s2)
	return result

def binsortinsert(item, data, i, j):
	diff = j - i
	if diff == 0:
		data.insert(data, item)
	else:
		diff = diff >> 1
		if item < data[i + diff]:
			binsortinsert(item, data, i, i+diff)
		else:
			binsortinsert(item, data, i+diff, j)
	

# return a list of (listitem, count) pairs.  Assumptions: s is sorted contains
# no None's
def countitems(list):
	result = []
	lastitem, count = None, 0
	for i in list:
		if i != lastitem:
			if count:
				result.append((lastitem, count))
			lastitem, count = i, 1
		else:
			count = count + 1
	if count:
		result.append((lastitem, count))
	return result

def gluetimes(times, df):
	quot, rem = divmod(times, 2)
	if times:
		if times == 1:
			return df()
		else:
			a = gluetimes(times/2, df)
			b = gluetimes((times+1)/2, df)
			return a + b
	return ''

def gluerange(start, stop, df):
	if start == stop:
		raise ValueError, 'I don\'t know how to return a Null range'
	halfway = (start + stop) / 2
	gotleft, gotright = halfway - start, stop - halfway

	if gotleft:
		if gotleft == 1:
			left = df(start)
		else:
			left = gluerange(start, halfway, df)
	if gotright:
		if gotright == 1:
			right = df(halfway)
		else:
			right = gluerange(halfway, stop, df)
		if gotleft:
			return left + right
		else:
			return right
	else:
		return left
