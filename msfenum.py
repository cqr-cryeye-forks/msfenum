#!/usr/bin/python

import logging, time, json, argparse, fileinput
from os import listdir, system, path, makedirs
from sys import exit

modulesfolder = "modules"

# Load the config
def loadConfig():
	try:
		with open('config') as f:
			return json.load(f)
	except:
		logging.error("Failed to load config")

# Valid the config
def validateModuleConfig(modules, modulesconfig):
	missing = []
	for module in modules:
		modulename = module.split("/")[-1]
		if (not path.isfile(path.join(modulesfolder,modulename))):
			missing.append(modulename)
	if missing:
		logging.warning("missing the following module(s): " + "".path.join(missing))

# Generate a RC file
def generateRcs(targets, threads, currentTime, config):
	postmodule = "spool off\n\n"
	premodule = "spool logs/"
	modules = config.get('modules')
	modulesconfig = [f for f in listdir(modulesfolder) if path.isfile(path.join(modulesfolder, f))]

	validateModuleConfig(modules, modulesconfig)

	if threads == None:
		threads = str(config.get('defaultthreads'))

	rcfile = ""
	for target in targets:
		for module in modules:
			modulename = module.split("/")[-1]
			if (path.isfile(path.join(modulesfolder,modulename))):
				rcfile += "setg threads " + str(threads) + "\n"
				rcfile += premodule + currentTime + "/" + modulename + ".log\n"
				rcfile += "use " + module + "\n"
				rcfile += open(path.join(modulesfolder,modulename),'r').read().replace("%IP%", target)
				rcfile += postmodule
	rcfile += "exit -y\n"
	rcoutput = open('logs/' + currentTime + '/file.rc', 'w')
	rcoutput.write(rcfile)
	rcoutput.close()

# Run msfconsole
def runRcs(currentTime):
	logging.info('--- Starting msfconsole ---')
	system('msfconsole -r logs/' + currentTime + '/file.rc')
	logging.info('--- Msfconsole done ---')

# Get a summary of discovered output
def getSuccessful(currentTime):
	logging.info('--- Summary of discovered results ---')
	logging.info(system('grep [+] logs/' + currentTime + '/*.log'))
	logging.info('--- Msfenum done ---')

# We need some ascii
def ascii():
	print(r"""
	             . --- .
	           /        \
	          |  O  _  O |
	          |  ./   \. |
	          /  `-._.-'  \
	        .' /         \ `.
	    .-~.-~/           \~-.~-.
	.-~ ~    |             |    ~ ~-.
	`- .     |             |     . -'
	     ~ - |             | - ~
	         \             /
	       ___\           /___
	       ~;_  >- . . -<  _i~
	          `'         `'
	   By: @wez3forsec, @rikvduijn
	""")

if __name__ == '__main__':
	# Define variables
	logfile= "msfenum.log"
	targets = []
	currentTime = int(time.time())
	currentDir = 'logs/' + str(currentTime)
	threads = None

	# Define logger settings
	logging.basicConfig(filename=logfile, level=logging.INFO)
	logging.getLogger().addHandler(logging.StreamHandler())
	logging.info('--- Starting msfenum ---')
	ascii()

	# Create current run directory
	logging.info('[*] Saving msfenum logs in: ' + currentDir)
	makedirs(currentDir)

	# Parse command line arguments
	parser = argparse.ArgumentParser(description="Metasploit framework auto enumeration script")
	parser.add_argument('-t', '--threads', nargs='?', help="Number of threads", type=int)
	parser.add_argument('files', metavar='TARGET_FILE', help='File containing targets')
	args = parser.parse_args()

	# Check if target file is accessible and load it
	if not path.isfile(args.files):
		exit('Target file does not exist')
	for target in fileinput.input(files=args.files if len(args.files) > 0 else ('-', )):
		targets.append(target)

	# Check if threads are specified.
	if args.threads is not None:
		threads = args.threads

	# Load config with default settings
	config = loadConfig()

	# Run the script
	generateRcs(targets, threads, str(currentTime), config)
	runRcs(str(currentTime))
	getSuccessful(str(currentTime))