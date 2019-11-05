import calc as c
import datetime

def do_image_balance(account_pubkey = c.config.Pubkey):
	return c.get_balance_pcx()
def do_image_dividend_rates(account_pubkey = c.config.Pubkey):
	rates, total = c.calc_dividend_rate()
	return rates, total


if __name__ == '__main__':
	image = {}
	image['pcx_balance'] = do_image_balance()
	image['rates'], image['total_votes'] = do_image_dividend_rates()
	image['time'] = str(datetime.datetime.utcnow())
	image['timestamp'] = int(datetime.datetime.strftime(datetime.datetime.now(), '%s'))
	c.insert2mongo(image, 'image')
