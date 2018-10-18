from bs4 import BeautifulSoup as bs
import requests
from fake_useragent import UserAgent
from proxymanager import ProxyManager
from pathlib import Path
import os
import json
import random
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from subprocess import Popen, PIPE

me = "xxxxxxxxxxxxx@email.com"
you = "xxxxxxxx@email.com"

home = str(Path.home())
dirpath = os.getcwd()

print(datetime.datetime.now())


ua = UserAgent()
proxy_manager = ProxyManager('{}/proxies.txt'.format(home))
random_proxy = proxy_manager.random_proxy()
proxies = random_proxy.get_dict()
print(proxies)

session = requests.Session()
session.headers = {'User-Agent': ua.random}

product_link_list = ['https://www.ssense.com/en-us/men/product/nike/white-off-white-edition-air-presto-sneakers/3625319', 'https://www.ssense.com/en-us/men/product/nike/black-off-white-edition-air-presto-sneakers/3456739', 'https://www.ssense.com/en-us/men/product/yeezy/grey-boost-700-sneakers/3676879', 'https://www.ssense.com/en-us/women/product/yeezy/grey-boost-700-sneakers/3677059', 'https://www.ssense.com/en-us/men/product/y-3/black-futurecraft-runner-4d-ii-sneakers/3131628', 'https://www.ssense.com/en-us/men/product/nike/beige-off-white-edition-the-ten-blazer-mid-sneakers/3685649', 'https://www.ssense.com/en-us/men/product/nikelab/black/3685639d', 'https://www.ssense.com/en-us/men/product/nikelab/orange/3685649']


def get_sizes_in_stock(product_link):
	global session, proxies
	sizes_in_stock = {}
	product_response = session.get(product_link, proxies=proxies)
#	with open('{}/product_{}.html'.format(dirpath, str(datetime.datetime.now()).replace(' ', '_')), 'w') as f:
#		f.write(product_response.text)
	soup = bs(product_response.text, "html.parser")
	options = soup.findAll("option")	
	for option in options:
		if ("Sold Out" not in option.text) and ("SELECT A SIZE" not in option.text):
			print(option['value'])
			option_value = option['value'].split('_')
			sizes_in_stock[option_value[0]] = option_value[1]
	return sizes_in_stock

def login():
	global session, proxies

	login_link = 'https://www.ssense.com/en-us/account/login'

	login_load = {
		"email": "xxxxxxxxx@email.com",
		"password": "XXXXXXX"
	}

	login_response = session.post(login_link, data=login_load, proxies=proxies)
	print(login_response.status_code)
	print(login_response.text)

def empty_shopping_bag():
	global session, proxies
	shopping_bag_link = 'https://www.ssense.com/en-us/shopping-bag.json'
	bag_response = session.get(shopping_bag_link, proxies=proxies)
	bag_json = json.loads(bag_response.text)
	if bag_json["cart"]["products"]:
		for product in bag_json["cart"]["products"]:
			print(product["sku"])
			session.delete("https://www.ssense.com/en-us/api/shopping-bag/{}".format(product["sku"]), proxies=proxies)




def add_to_cart(sizes_in_stock):
	global session, proxies
	size_chosen = random.choice(list(sizes_in_stock.values()))
	print(size_chosen)

	cart_load = {
		"serviceType": "product-details",
		"sku": size_chosen,
		"userId": ""
	}

	cart_link = "https://www.ssense.com/en-us/api/shopping-bag/" + size_chosen

	cart_response = session.post(cart_link, data=cart_load, proxies=proxies)
	print(cart_response.status_code)
	#print(cart_response.text)
	#with open('{}/cart_{}.html'.format(dirpath, str(datetime.datetime.now()).replace(' ', '_')), 'w') as f:
	#	f.write(cart_response.text)



def checkout():
	global session, proxies

	checkout_link = 'https://www.ssense.com/en-us/checkout'

	form_response = session.get(checkout_link, proxies=proxies)

	with open('{}/checkout_form_{}.html'.format(dirpath, str(datetime.datetime.now()).replace(' ', '_')), 'w') as f:
		f.write(form_response.text)
	
	form_soup = bs(form_response.text, 'html.parser')

	CSRTokenId_soup = form_soup.findAll("input", {"name": "CSRFTokenId"})


	#print(CSRTokenId_soup)
	print(CSRTokenId_soup[0]['value'])
	print(CSRTokenId_soup[0].input['value'])
	
	device_fingerprint_soup = form_soup.findAll("input", {"name": "device_fingerprint"})
	print("Device fignerprint: {}".format(device_fingerprint_soup[0]['value']))
	

	payload = {
		"CSRFTokenId": CSRTokenId_soup[0]['value'],
		"CSRFTokenValue": CSRTokenId_soup[0].input['value'],
		"shipping_id": "", 
		"shipping_isnew": "1",
		"device_fingerprint": device_fingerprint_soup[0]['value'],
		#"device_fingerprint": "2a376561a232f9a8013033653c2099bf",
		"shipping_firstname": "xxxxxxx",
		"shipping_lastname": "xxxx",
		"shipping_company": "",
		"shipping_address": "xxxxxxxx",
		"shipping_country": "xx",
		"shipping_state": "xx",
		"shipping_postalcode": "xxxxx",
		"shipping_city": "xxxxx",
		"shipping_phone": "xxxxxx",
		"shipping_method": "43",
		"pccc": "",
		"paymentMethod": "creditcard",
		"creditcardHolderName": "xxxxxx",
		"creditcardNumber": "xxxxxxxxxxxxxxxxxxxx",
		"creditcardCVV": "xxx",
		"creditCardMonth": "xx",
		"creditCardYear": "xxxx",
		"sameAsShipping": "1",
		"billing_id": "", 
		"billing_isnew": "0",
		"billing_firstname": "",
		"billing_lastname": "",
		"billing_company": "",
		"billing_address": "", 
		"billing_postalcode": "",
		"billing_city": "",
		"billing_phone": ""
	}

	checkout_response = session.post(checkout_link, data=payload, proxies=proxies)

	with open('{}/checkout_{}.html'.format(dirpath, str(datetime.datetime.now()).replace(' ', '_')), 'w') as f:
		f.write(checkout_response.text)

sizes_notification = []

for product_link in product_link_list:
	print(product_link)
	sizes_in_stock = get_sizes_in_stock(product_link)	
	print(sizes_in_stock)
	if sizes_in_stock:
		login()
		empty_shopping_bag()
		add_to_cart(sizes_in_stock)
		checkout()
		available_sizes = ' '.join(list(sizes_in_stock.keys()))
		print(available_sizes)
		sizes_notification.append(product_link + "/n" + available_sizes + "\n")
		sizes_notification.append("------------------------------------")


if sizes_notification:
	msg = MIMEText('\n'.join(sizes_notification))
# Create message container - the correct MIME type is multipart/alternative.
	msg['Subject'] = "Ssense Auto Checkout caught something for you!"
	msg['From'] = me
	msg['To'] = you
	p = Popen(["/usr/sbin/sendmail", "-t", "-oi"], stdin=PIPE, universal_newlines=True)
	p.communicate(msg.as_string())

print(datetime.datetime.now())
