import calc as c
import datetime

def do_image_balance(account_pubkey = c.config.Pubkey):
	return c.get_balance_pcx()
def do_image_dividend_rates(account_pubkey = c.config.Pubkey):
	rates, total = c.calc_dividend_rate()
	return rates, total
def do_image_staking_dividends(account_pubkey = c.config.Pubkey):
	staking_dividends = c.chainx_getStakingDividendByAccount(account_pubkey)
	return staking_dividends.get(account_pubkey)

if __name__ == '__main__':
	image = {}
	image['pcx_balance'] = do_image_balance()
	image['rates'], image['total_votes'] = do_image_dividend_rates()
	image['time'] = str(datetime.datetime.utcnow())
	image['timestamp'] = int(datetime.datetime.strftime(datetime.datetime.now(), '%s'))
	image['staking_dividends'] = do_image_staking_dividends()
	c.insert2mongo(image, 'image')
