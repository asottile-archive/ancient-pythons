#!/usr/local/bin/python

##Subject: Generate Sun NIS netgroups for your sites' DNS domains
##From: ken.manheimer@NIST.GOV (Ken Manheimer)
##To: python-list@cwi.nl
##Date: Wed, 05 Apr 1995 12:08:39 -0400 (EDT)
##Organization: National Institute of Standards and Technology
##
##I use the following python script to generate Sun NIS (formerly YP)
##netgroups for all the DNS domains in my organizations network.  This
##enables me to export NFS filesystems to, eg, all and only the hosts in
##my organization, or just the hosts in one divisions' network.  It is
##real handy.  See the docstring and comments at the top for
##instructions, if you're interested.
##
##Note that the script uses only the standard python libraries - no
##subproc.py or anything.  (It does depend on the public-domain Unix
##'host' command, though.)  I wanted it to operate under similar
##constraints as the TCL script which i originally wrote to do this job,
##so i could compare the code and operation of the respective scripts.
##
##(I wrote the TCL script about two years ago, when i was evaluating TCL
##as a scripting prospect.  It was a first effort, and probably more
##sloppy than needs be.  The difficulty in implementing it is what led
##me to look for other scripting-language prospects, and finally to
##python.  However, the script has been used in production since then,
##in support of my NFS file service.  I've been having some problems
##with it, and it has gotten almost unbearable to maintain it, so i
##finally gave in and reimplemented in python.
##
##And, of course, the python version was extremely much easier and more
##simple to implement, and more efficient to boot.  I'd be willing to
##post the TCL version, if anyone is interested in contrasting - though
##i don't think i did a fair job on the tcl version.  Perhaps someone
##could work on the TCL version, and we could have a decent version in
##each language, to compare and contrast...)
##
##Note that both versions of the script depend upon the public-domain
##dns lookup utility, 'host', for their operation.  I believe it's
##available from the major unix-sources distribution sites.
##
##ken
##ken.manheimer@nist.gov, 301 975-3539

"""This script produces '/etc/netgroup'-format output, itemizing the hosts for
all the subdomains nested (inclusive) within designated dns domains.  Along the
way, it produces on stderr a cumulative tallies of the number of subdomains,
hosts, and akas (ip numbers directly associated with distinct hostnames; not
CNAMES) per domain, and a grand tally for all.  The stderr tallies can be
silenced by setting the config_vars['verbose'] value to 0.

If invoked as a script, the command line may contain the names of the domains
to be investigated.  If not specified, then the domain names are taken from the
value of config_vars['default_subjs'] - see the config_vars() routine.

Primary groups for each specified root domain are also created, using
the domain-name with '_ALL' appended.  Additionally, a meta-umbrella group,
named by config_vars['umbrella'], if the domains to be examine are specified on
the command line, the or taken from the first part of the first
domain name, if passed from the command line, is created, containing all the
root domains.

Special provisions are made to avoid betraying a hardwired netgroup-line
character length, using fanout indirection (recursively, so ostensibly a domain
with any number of hosts can be represented).

In order to include the resulting output into your NIS databases,
redirect it to a file *distinct* from your /etc/netgroup file, and
tailor your /var/yp/Makefile to incorporate the contents of the file
into the make of the netgroup maps.  (You must *not* fold the catalog
into the netgroup.byuser map - see the comments at the top of the code
for the reasons.)

Ken.Manheimer@nist.gov,  5-Apr-1995"""

# /ufs/guido/CVSROOT/python/Contrib/dns2netgroup.py,v 1.1 1995/04/10 11:48:51 guido Exp

# The complexity of the formatting portion of the process is partly
# due to awkward constraints that Sun's NIS map production mechanisms
# impose.  Each netgroup line *must*:
# 
#  (1) be less than 1027 characters long,
#  (2) not use '\' backslash-escaped text-continuation lines,
#  (3) minimize continuation-chaining of the netgroup references as much
#      as possible.  Ie, use a tree fanout instead of chaining.
# 
# See also the note about netgroup.byuser at the bottom of this doc, for
# an explanation of the reason for not populating netgroup.byuser from
# the netgroup catalog.
# 
# Number (1), the 1027 char-limitation, is a builtin constraint of the
# makedbm routine (at least, as of SunOS 4.1.3).
# 
# Number (2), no backslash-continuation lines, is simply because makedbm
# does not support them.
# 
# Number (3), the chaining limitation is a logical consequence of reverse
# host-to-domain mapping.  Although chaining is a simpler mechanism to
# implement - have an item just below the line-length limit be the
# indirection-link # to the name of a continuation netgroup - the nesting
# causes a serious problem.
#
# The problem is, given a group that contains as many entries as can fit, with
# a concluding chain-reference to another group, then the entries in the last
# group in the chain all belong to each of the previous previous groups in the
# chain.  Thus, for a group that chains 10 times, each item in the last group
# is seen as belonging to 10 groups, which means 10 reverse-map entries for
# each one.  No good.
# 
# So, instead of using a chaining indirection, use a tree indirection.
# If the real group is too big, create as many proxy-netgroups as it
# takes, and have the real group contain the names of all the proxy
# netgroups.  That way, all the entries in the extended group will
# belong to two groups, instead of having all the tenth-link entries
# belonging to ten, ninth-link entries belonging to nine, etc.
# 
# Finally, the netgroup.byuser is derived from only the regular
#  (/etc/netgroups) netgroup file.  The promiscuous way that each
# user in one triad belongs to all the triads in the group makes for
# an exponential explosion, even worse than the geometric explosion
# of the linearly-chained netgroup continuation scheme (and not
# circumventable).  Here is a fragment from my yp Makefile which 
# produces the netgroup extension file and incorporates it into the
# appropriate netgroup maps, along with the standard /etc/netgroup
# file contents:
#
#netgroup+: $(SITENETGROUP) netgroup
#
#$(SITENETGROUP): FORCE
#	$(DNS_TO_NETGROUP) >> $(LOCALDIR)/$(SITENETGROUP).new \
#	&& (cp $(LOCALDIR)/$(SITENETGROUP) $(LOCALDIR)/$(SITENETGROUP).prev; \
#	    mv $(LOCALDIR)/$(SITENETGROUP).new $(LOCALDIR)/$(SITENETGROUP))
#	@echo Updated $(SITENETGROUP)
#
#FORCE:
#
#netgroup.time: $(DIR)/netgroup $(LOCALDIR)/$(SITENETGROUP)
#	@grep -vh "^#" $(DIR)/netgroup $(LOCALDIR)/$(SITENETGROUP) \
#	| $(MAKEDBM) - $(YPDBDIR)/$(DOM)/netgroup
#	@($(REVNETGROUP) < $(DIR)/netgroup -u $(CHKPIPE)) \
#	| $(MAKEDBM) - $(YPDBDIR)/$(DOM)/netgroup.byuser
#	@(grep -vh "^#" $(DIR)/netgroup $(LOCALDIR)/$(SITENETGROUP) \
#	| $(REVNETGROUP) -h $(CHKPIPE)) \
#	| $(MAKEDBM) - $(YPDBDIR)/$(DOM)/netgroup.byhost
#	@touch netgroup.time; 
#	@echo "updated netgroup"; 
#	@if [ ! $(NOPUSH) ]; then $(YPPUSH) -d $(DOM) netgroup; fi
#	@if [ ! $(NOPUSH) ]; then $(YPPUSH) -d $(DOM) netgroup.byuser; fi
#	@if [ ! $(NOPUSH) ]; then $(YPPUSH) -d $(DOM) netgroup.byhost; fi
#	@if [ ! $(NOPUSH) ]; then echo "pushed netgroup"; fi


version = '1.1'

import sys, os, string

################################################################## Declarations
# - establish the configuration and data structures # (edit the values of
# config_vars for your site).  #

config_vars = {
    'default_subjs': [yer.domain, 'yeralt.domain'], # Domains to scan if no args.
    'default_umbrella': 'SITE',		# Name for encompassing meta-group.
					# Name must not be in domains.
    'hostCmd':				# Path of openware 'host' command.
    	'/usr/local/bin/host',
    'lineLenLimit': 1000,		# Netgroup lines length limit.
    'verbose': 1}

#################################################################
# Accumulation							#

# Domains data structure - a domain is a dict mapping the domain name to the
# subdomains and hosts within the domain.
#
#  - a list of contained domain (subdomain) names
#  - a list of host (names,ip) tuples for hosts immediately in the domain
#
# The topmost domain is a tuple, containing:
#   - the domains data structure
#   - a list of unresolved domains
#   - a string (possibly empty) identifying the structure's root domain name
#   - a dict, for registering a running tally, per subdomain of:
#	- the immediately contained domains
#	- the immediately contained, distinct hosts
#	- the 'akas': ip numbers with multiple names

def init_domains(umbrella, subjs):
    """Initialize domain and tracking data structures, based on UMBRELLA name
    and names of SUBJECTS domains."""
    note('Initializing...\n\tUmbrella: "%s"\n\tPrimary Domains: %s' %
	 (umbrella, string.join(subjs)))
    tally = {}
    for sd in subjs:
	tally[sd] = [0, 0, 0]		# [domains, hosts, akas]
    domains = ({umbrella: ([], [])}, [], umbrella, tally)
    for dom in subjs:
	domains[0][umbrella][0].append(dom)
	domains[0][dom] = ([], [])	# add a domains dict entry
	domains[1].append(dom)		# and register on unresolved list
    return domains

def gather(umbrella=None, subjs=None):
    """Resolve domains, optionally given umbrella and subjs, taken from
    config_vars defaults if not specified."""

    umbrella = (umbrella or config_vars['default_umbrella'])
    subjs = (subjs or config_vars['default_subjs'])

    if umbrella in subjs:
	raise ValueError, 'Umbrella name must not be within domains'

    domains = resolve_all(init_domains(umbrella, subjs))
    tallies = domains[3]
    grandTally = [len(subjs), 0, 0]
    note('\n\tTotals:')
    for root in subjs:
	subs, hosts, akas = tallies[root][0], tallies[root][1],tallies[root][2]
	note(' %s:\t %d subdomains, %d hosts, %d AKAs' %
	     (root, subs, hosts, akas))
	grandTally[0] = grandTally[0] + subs
	grandTally[1] = grandTally[1] + hosts
	grandTally[2] = grandTally[2] + akas
    tallies[umbrella] = grandTally
    note('\n ** %s Grand Total: %d domains, %d hosts, %d AKAs' %
	 (umbrella, grandTally[0], grandTally[1], grandTally[2]))
    return domains

def resolve_all(domains):
    """Resolve all unresolved subdomains within domains STRUCT."""
    unresList = domains[1]
    while unresList:
	# Pop current unresolved domain off the unresolved-list:
	curDom = unresList[0]; del unresList[0]
	# And process it:
	resolve_domain(domains, curDom)
    return domains
    

def resolve_domain(domains, domainNm):
    """Given domains STRUCT, iterate and register hosts within DOMAIN_NAME."""

    note('working on ' + domainNm + '... ', 1)
    domainsDict, unregisteredList, tally = domains[0], domains[1], domains[3]
    domainSubs = domainsDict[domainNm][0]
    (subs, hosts) = list_domain(domainNm)

    domainsDict[domainNm][1][:] = hosts	# Register the domain's hosts.

    for subdomain in subs:		# Register subdomains within domain:
	domainSubs.append(subdomain)
	# Check for brand new subdomain:
	if not domainsDict.has_key(subdomain):
	    # Register for later resolution:
	    domainsDict[subdomain] = ([], [])
	    # PREPEND to the unregistered list, for depth-first operation:
	    unregisteredList.insert(0, subdomain)

    # Register and post running notes on the hosts and subdomains tally:
    aka = {}; numAkas = numHosts = 0
    for nm, ip in hosts:
	if aka.has_key(ip):
	    numLst = aka[ip]
	    if len(numLst) == 1:
		# Only chalk up each host with aka's once.
		numAkas = numAkas + 1
	    numLst.append(nm)
	else:
	    aka[ip] = [nm]
	    numHosts = numHosts + 1
    note('%s%d hosts%s' %
	 (((domainSubs and '%s subdomains, ' % len(domainSubs)) or ''),
	  numHosts,
	  (numAkas and (', %d AKAs' % numAkas)) or ''))
    # Find the right tally:
    root = get_root(domains, domainNm)
    if not root:
	note('Subdomain %s not found in roots - excluding from tally' %
	     domainNm, 0)
    else:
	tallyLst = tally[root]
	tallyLst[0] = tallyLst[0] + len(domainSubs)
	tallyLst[1] = tallyLst[1] + numHosts
	tallyLst[2] = tallyLst[2] + numAkas
    return domains
def get_root(domains, subdomainNm):
    """Given domains STRUCT and a subdomain NAME, return subdomains' root."""
    # [domains[0]: domain dict; domains[2]: umbrella][0] -:
    for root in domains[0][domains[2]][0]:
	if string.lower(subdomainNm[-1 * len(root):]) == root:
	    return root							# ===>
    return ''								# ===>

def list_domain(domainNm):
    """Return pair of lists: subdomains and hosts, of domain."""
    hashedHosts = {}
    subs, hosts = [], []
    nmLen, lowNm = len(domainNm), string.lower(domainNm)
    proc = os.popen('%s -l %s 2>/dev/null' % (config_vars['hostCmd'],
					      domainNm))
    try:
	for line in proc.readlines():
	    line = string.split(line)
	    if line[1] == 'PTR':		# Disregard PTR records.
		continue						# ==^
	    elif line[1] == 'NS':		# Name servers - subdomain ids.
		if (len(line[0]) > nmLen	# Gross containment criterion
		    # Precise containment criterion:
		    and (string.lower(line[0][(-1*nmLen):]) == lowNm)
		    # Inhibit duplicates:
		    and line[0] not in subs):
		    subs.append(line[0])
	    elif line[1] == 'has':
		nm = line[0]
		if (# host is, in fact, immediately in domain:
		    (string.lower(nm[1+string.find(nm,'.'):]) == lowNm)
		    # and not already noticed for domain:
		    and (not hashedHosts.has_key(nm))):
		    hosts.append((line[0], line[3]))
		    hashedHosts[nm] = 0
	    else:
		sys.stderr.write('\n ** (%s) "%s" **\n' %
				 (domainNm, string.join(line)))
    except:
	note('**glitch**  (%s: %s)' % (sys.exc_type, str(sys.exc_value)))
    return subs, hosts
		

#################################################################
# Presentation							#

def present(domains):
    """Present the gathered domains in netgroup format on stdout."""

    # See the comments at the top of the module for an overview of the special
    # format-constraints.

    domainsDict, umbrella = domains[0], domains[2]
    roots = domains[0][umbrella][0]

    # First produce a netgroup consisting of all the domain netgroups:
    print ('# %s contains all %s subdomains,\n# and inherently their hosts.' %
	   (umbrella, string.joinfields(roots, ', ')))
    print umbrella + '\t\t',
    for root in roots:
	print root + '_ALL',
    print ''
    
    # Next 'root_ALL' groups, to 
    for root in roots:
	print '\n# %s_ALL entails all hosts in %s domain.' % (root, root)
	print root + '_ALL\t ' + root,
	print string.join(domains[0][root][0])
    print ''
 
    print "# Below are the subdomains of the above root domains, together"
    print "# with their immediate constituents."
    print ''
    print ("# Domain entries that would exceed %s characters are" %
	   config_vars['lineLenLimit'])
    print "# distributed via indirection to subentries, to avoid"
    print "# betraying an inherent limit in, eg, SunOS 4.1.3 netgroup-"
    print "# handling NIS routines."
    print ''

    todo = roots[:]
    while todo:
	cur = todo[0]; del todo[0]
	subdoms, hosts = domains[0][cur][0], domains[0][cur][1]
	if subdoms:
	    # prepend on todo list, for depth-first operation
	    todo[0:0] = subdoms
	for line in fanout(cur, triplize(hosts)):
	    print line
	print ''
    print '# End of automated dns_to_netgroup production.'

def triplize(hostList):
    """Give domains host pairs LIST, return list of netgroup host triples."""
    res = []
    for pair in hostList:
	res.append('(' + pair[0] + ',,)')
    res.sort()
    return res

def fanout(groupNm, leafList, indPref='_'):
    """Return GROUP's leaves LIST as array of netgroup lines, branching out
    through indirection groups to avoid excessive line lengths.

    As many indirection layers are perpetuated as is necessary."""

    # Collect leaves into space-delimited lines, allowing overhead for group
    # name prefix:
    indGroups, indirIndex = [], 1
    leafLines, curLine = [], ''
    lenLim = config_vars['lineLenLimit'] - (len(groupNm) + len(indPref) + 4)
    for leaf in leafList:
	if len(curLine) + len(leaf) + 1 > lenLim:
	    pref = groupNm + indPref + str(indirIndex)
	    indirIndex = indirIndex + 1
	    leafLines.append(pref + '\t' + curLine)
	    indGroups.append(pref)
	    curLine = ' ' + leaf
	else:
	    curLine = curLine + ' ' + leaf

    
	    
    if not leafLines:
	# Ah, we've hit bottom:
	return [groupNm + '\t' + curLine]

    else:
	# Take care of the trailing line:
	pref = groupNm + indPref + str(indirIndex)
	leafLines.append(pref + '\t' + curLine)
	indGroups.append(pref)
	# Oops - have to account for possible fanout in fanout group, itself:
	prefChar = indPref[0]
	if len(indPref) == 1:
	    indPref = prefChar + '1' + prefChar
	else:
	    indPref = prefChar + str(string.atoi(indPref[1:-1]) + 1) + prefChar
	return fanout(groupNm, indGroups, indPref) + leafLines
    
    
def note(msg, noCr=0, threshold=1):
    """Print msg to stderr, optional integer threshold must equal or exceed
    config_vars verbose setting."""
    if config_vars['verbose'] >= threshold:
	sys.stderr.write(msg + (((not noCr) and '\n') or ''))

#################################################################
# Driver							#

if __name__ == '__main__':		# If we're running as a script...

    subjs = umbrella = None
    if len(sys.argv) > 1:
	subjs = sys.argv[1:]
	umbrella = string.upper(string.splitfields(sys.argv[1], '.')[0])

    it = gather(umbrella, subjs)
    present(it)
