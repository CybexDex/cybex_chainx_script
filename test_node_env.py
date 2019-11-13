import os
"""
please test this script in crontab
"""
try:
	res = os.popen('node chainx/src/hello.js').read()
	print(res)
except:
	print( 'error when exec node chainx/src/hello.js')
