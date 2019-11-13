from chainx_websocket_client import WebsocketClient, client 
import json, math
import config
import requests
import datetime
import logging
from logging.handlers import TimedRotatingFileHandler
from pymongo import MongoClient
from bson import json_util
from bson.objectid import ObjectId
import os, time

is_debugging = False
logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='/tmp/chainx.log',
                filemode='w')
logHandler = TimedRotatingFileHandler(filename = '/tmp/chainx.log',
                when = 'D', interval = 1, encoding='utf-8'
)
logger = logging.getLogger('chainx')
formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)

mongo_client = MongoClient(config.MONGODB_DB_URL)
db = mongo_client[config.MONGODB_DB_NAME]

# use chainx_getIntentionByAccount to fetch balance image of the votee node, here Pubkey= config.Pubkey
def chainx_getAssetsByAccount(Pubkey, page, limit):
	page = int(page)
	limit = int(limit)
	res = client.request('chainx_getAssetsByAccount', [Pubkey, page, limit])
	return res
def chainx_getNominationRecords(Pubkey):
	res = client.request('chainx_getNominationRecords', [Pubkey])
	# res = client.request('chainx_getPseduNominationRecords', [Pubkey])
	return res
def chainx_getIntentionByAccount(Pubkey):
	res = client.request('chainx_getIntentionByAccount', [Pubkey])
	return res
def chainx_getIntentions():
	res = client.request('chainx_getIntentions',[])
	return res
def chainx_getStakingDividendByAccount(Pubkey):
	res = client.request('chainx_getStakingDividendByAccount', [Pubkey])
	return res
def chain_getBlockHash(height):
	res = client.request('chain_getBlockHash', [height])
	return res

def get_nominations(Pubkey, page, limit):
	page = int(page)
	limit = int(limit)
	url = 'https://api.chainx.org/intention/%s/nominations' % (Pubkey)
	data = {'page' : page, 'page_size' : limit}
	# 'https://api.chainx.org/intention/0x589eadd1fec281804b6f080d89b4262114e1e7485962a27259865901b615b895/nominations?page=0&page_size=50'
	r = requests.get(url = url, params = data, verify = True )
	return r.json()['items']

def get_nominations_all(Pubkey):
	page = 0
	limit = 50
	nominations = []
	while 1:
		tmp = get_nominations(Pubkey, page, limit)
		nominations.extend(tmp)
		if len(tmp) < limit:
			break
		page += 1
	return nominations


def do_transfer(_from, _to, amount, memo = ''):
	amount = int(amount)
	privk = config.PRIVK
	cmd = 'node chainx/src/do_transfer.js %s %s %s %s %s' % (_from, _to, str(amount), privk, memo)
	logger.info(cmd)
	res = os.system(cmd)
	return res == 0
def do_staking(_from, vote_to, amount):
	amount = int(amount)
	privk = config.PRIVK
	logger.info('node chainx/src/do_stake.js %s %s %s privkey' % (_from, vote_to, str(amount)))
	cmd = 'node chainx/src/do_stake.js %s %s %s %s' % (_from, vote_to, str(amount), privk)
	res = os.system(cmd)
	return res == 0
	
def do_claim(target):
	privk = config.PRIVK
	cmd = 'node chainx/src/do_claim.js %s %s ' % (target, privk)
	res = os.system(cmd)
	return res == 0
def calc_dividend_rate():	
	NominationRecords = get_nominations_all(config.Pubkey)
	check_total = 0
	for n in range(len(NominationRecords)):
		check_total += NominationRecords[n]['nomination']
	dividend_rate = {}

	for n in range(len(NominationRecords)):
		dividend_rate[NominationRecords[n]['nominator']] = {'dividend' : NominationRecords[n]['nomination'] / float(check_total), 'nomination': NominationRecords[n]['nomination'] }
	return dividend_rate, check_total
def _floor(digit, prec):
	return int(digit)
	return int(digit *(0.1 ** prec) ) * (10 ** prec)
	
def calc_dividend_by_rates(rates, delta):
	dividend = {}
	for k,v in rates.items():
		dividend[k] = {'dividend': _floor(v['dividend'] * config.Alpha * delta, config.Precision), 'nomination':v['nomination'] } 
	return dividend
def calc_dividend(free_delta):
	NominationRecords = get_nominations_all(config.Pubkey)
	check_total = 0
	for n in range(len(NominationRecords)):
		check_total += NominationRecords[n]['nomination']
	dividend = {}

	for n in range(len(NominationRecords)):
		dividend[NominationRecords[n]['nominator']] = {'dividend' : _floor(NominationRecords[n]['nomination'] * free_delta * config.Alpha/ float(check_total), config.Precison), 'nomination': NominationRecords[n]['nomination'] }
	return dividend

def insert2mongo(data, col_name):
	try:
		db[col_name].insert(data)
	except:
		logger.error('failed to insert ' + json.dumps(data))
	
def get_balance_pcx():
	res = chainx_getAssetsByAccount(config.Pubkey, 0, 10)
	
	for asset in res['data']:
		if asset['name'] == 'PCX':
			break
	return asset
def free_balance_pcx():
	asset = get_balance_pcx()
	free = asset['details']['Free']
	logger.info('free_balance_pcx is \n' + json.dumps(free))
	return free
def get_calc_dividend_rate():
	try:
		t_upperbound = int(datetime.datetime.strftime(datetime.datetime.now(),'%s'))
		t_lowerbound = t_upperbound - 3600 * 24 * 7
		logger.info('sampling timepoint is between (%s, %s)' % (str(t_lowerbound), str(t_upperbound)))
		timestamps_count = db.image.find({'timestamp':{'$gte':t_lowerbound}}).count()
		logger.info('valide image number is ' + str(timestamps_count))
		seed = random.random()
		chosen = int(seed * timestamps_count) 
		logger.info('chosen sequence is ' + str(chosen))
		item = list(db.image.find({'timestamp': {'$gte':t_lowerbound}}).skip(chosen).limit(1))[0]
		rates = item['rates']
		total_votes = item['total_votes']
		chosen_time = item['time']
		chosen_timestamp = item['timestamp']
	except:
		logger.error('error when fetch rates from db.image')
		sys.exit(0)
	return rates, total_votes, chosen_time, chosen_timestamp

if __name__ == '__main__':
	import sys
	# 1. load image of base balance for the node from mongodb
	try:
		base_free = list(db['balance'].find().sort([('timestamp',-1)]).limit(1))[0]['pcx']['details']['Free']
	except:
		image_balance = get_balance_pcx()
		insert2mongo({'pcx':image_balance, 'timestamp':int(datetime.datetime.strftime(datetime.datetime.now(), '%s')) , 'time':str(datetime.datetime.utcnow())}, 'balance')
		logger.info('init balance, will not dividend.')
		sys.exit(0)
	logger.info('base pcx free balance is ' + str(base_free))
	# 2. fetch current balance for the node from chain
	free = free_balance_pcx()
	free_delta = free - base_free
	if free_delta <= 0:
		logger.warning('balance is not enough!')
		sys.exit(0)
	# 3. calc voters' dividend after getting free_delta
	# first solution
	# dividend = calc_dividend(free_delta)
	# second solution: after calc rates and store, later load rates from mongo and then calc with delta
	rates, total, chosen_time, chosen_timestamp = get_calc_dividend_rate()
	insert2mongo({'rates':rates,'total_nomination': total,'free_delta': free_delta, 'timestamp':int(datetime.datetime.strftime(datetime.datetime.now(), '%s')), 'time': str(datetime.datetime.utcnow()), 'chosen_time': chosen_time, 'chosen_timestamp':chosen_timestamp}, 'rates')
	# rates = db['rates'].find().sort(['timestamp':-1]).limit(1)
	dividend = calc_dividend_by_rates(rates, free_delta )
	estimate_amount = int(free_delta * 0.2)
	# 4. transfer dividend to other voters
	for k,v in dividend.items():
		if k == config.Pubkey:
			estimate_amount += v['dividend']
			continue
		to = k
		_from = config.Pubkey
		amount = v['dividend']
		if amount < config.Fee :
			continue
		# amount = int(amount - config.Fee)
		memo = '"CybexDex dividends"'
		logger.info('do_transfer(%s, %s, %s, %s)' % (_from, to, str(amount), memo))
		print 'do_transfer(%s, %s, %s, %s)' % (_from, to, str(amount), memo)
		if is_debugging is False:
			is_succeed = do_transfer(_from, to, amount, memo)
			if is_succeed is False:
				logger.error('failed when transfer %s to %s, will exit with code -1 ' % (str(amount), to))
				sys.exit(-1)
			time.sleep(30)
		insert2mongo({'to_addr':to,'amount': amount,'from_addr': _from, 'timestamp':int(datetime.datetime.strftime(datetime.datetime.now(), '%s')), 'time': str(datetime.datetime.utcnow())}, 'dividend_transfer')
	# 5. claim insterest for node
	time.sleep(10)
	staking_dividends = chainx_getStakingDividendByAccount(config.Pubkey)
	node_staking_dividends = staking_dividends.get(config.Pubkey)
	insert2mongo( {'staking_dividends':staking_dividends, 'timestamp':int(datetime.datetime.strftime(datetime.datetime.now(), '%s')), 'time': str(datetime.datetime.utcnow()) }, 'staking_dividends')
	logger.info('current StakingDividend before claim -> ' + json.dumps(staking_dividends) )
	logger.info('do_claim(%s)' % (config.Pubkey))
	if is_debugging is False:
		is_succeed = do_claim(config.Pubkey)
		if is_succeed is False:
			logger.error('failed when do claim, will exit with code -1')
			sys.exit(-1)
		time.sleep(30)
	# 6. stake self
	free = free_balance_pcx()
	stake_amount = free - config.Fee
	estimate_amount += int(staking_dividends.get(config.Pubkey))
	logger.info('estimated transfer amount to %s is %s ' % (config.Pubkey, str(estimate_amount)))
	logger.info('transfer to %s with amount %s ' % (config.Transfer_to, str(stake_amount) ))
	# do_staking(config.Pubkey, config.Pubkey, stake_amount)
	memo = '"CybexDex revenue"'
	if is_debugging is False:
		is_succeed = do_transfer(config.Pubkey, config.Transfer_to, stake_amount, memo)
		if is_succeed is False:
			logger.error('failed when do transfer %s to %s, will exit with code -1' % (str(stake_amount), config.Transfer_to) )
			sys.exit(-1)
		time.sleep(30)
	# 7. fetch balance image for node and store
	image_balance = get_balance_pcx()
	insert2mongo({'pcx':image_balance, 'last_estimate_amount':estimate_amount, 'timestamp':int(datetime.datetime.strftime(datetime.datetime.now(), '%s')) , 'time':str(datetime.datetime.utcnow())}, 'balance')

