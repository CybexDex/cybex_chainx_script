import calc as c
import datetime, json
image_balance = c.get_balance_pcx()
try:
	c.insert2mongo({'pcx':image_balance, 'timestamp':int(datetime.datetime.strftime(datetime.datetime.now(), '%s')) , 'time':str(datetime.datetime.utcnow())}, 'balance')
except:
	print 'failed to set balance : ' + json.dumps(image_balance)


