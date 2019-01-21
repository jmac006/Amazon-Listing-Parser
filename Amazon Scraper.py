'''
Scrape Amazon Data to JSON File
Created by: Justin Mac
Library Dependencies:
Install Python, Python PIP, Python Requests, and Python LXML

'''
from lxml import html  
import csv,os,json
import requests
#from exceptions import ValueError
from time import sleep
import re
import time


def AmzonParser(url, ASIN):
	headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}
	page = requests.get(url,headers=headers)
	while True:
		sleep(3)
		try:
			doc = html.fromstring(page.content)
			XPATH_NAME = '//h1[@id="title"]//text()'
			XPATH_SALE_PRICE = '//span[contains(@id,"ourprice") or contains(@id,"saleprice")]/text()'
			XPATH_ORIGINAL_PRICE = '//td[contains(text(),"List Price") or contains(text(),"M.R.P") or contains(text(),"Price")]/following-sibling::td/text()'
			XPATH_CATEGORY = '//a[@class="a-link-normal a-color-tertiary"]//text()'
			XPATH_AVAILABILITY = '//div[@id="availability"]//text()'
			XPATH_RANKING = '//li[contains(@id,"SalesRank")]//text()'

			RAW_NAME = doc.xpath(XPATH_NAME)
			RAW_SALE_PRICE = doc.xpath(XPATH_SALE_PRICE)
			RAW_CATEGORY = doc.xpath(XPATH_CATEGORY)
			RAW_ORIGINAL_PRICE = doc.xpath(XPATH_ORIGINAL_PRICE)
			RAW_AVAILABILITY = doc.xpath(XPATH_AVAILABILITY)
			RAW_RANKING = doc.xpath(XPATH_RANKING)


			#Convert array to string and clean-up string
			NAME = ' '.join(''.join(RAW_NAME).split()) if RAW_NAME else None
			SALE_PRICE = ' '.join(''.join(RAW_SALE_PRICE).split()).strip() if RAW_SALE_PRICE else None #strip() removes whitespace
			CATEGORY = ' > '.join([i.strip() for i in RAW_CATEGORY]) if RAW_CATEGORY else None
			ORIGINAL_PRICE = ''.join(RAW_ORIGINAL_PRICE).strip() if RAW_ORIGINAL_PRICE else None
			AVAILABILITY = ''.join(RAW_AVAILABILITY).strip() if RAW_AVAILABILITY else None
			
			

			#Clean up ranking string
			RANKING = ' '.join(RAW_RANKING).strip('\n') if RAW_RANKING else None

			
			if not RANKING:
				RANKING = ["No Ranking"]
				data = {
					'NAME':NAME,
					'PRICE':SALE_PRICE,
					'CATEGORY':CATEGORY,
					#'ORIGINAL_PRICE':ORIGINAL_PRICE,
					#'AVAILABILITY':AVAILABILITY,
					'URL':url,
					'RANK':RANKING,
					}
				return data

			if not ORIGINAL_PRICE:
				ORIGINAL_PRICE = SALE_PRICE

			if page.status_code!=200:
				print("Captcha")
				raise ValueError('captha')
				return data


			RANKING = RANKING.replace('\n','')
			RANKING = re.sub(r' {[^}]*}','',RANKING)
			RANKING = RANKING.replace(" ",' ')
			RANKING = RANKING.replace(".zg_hrsr", " ")
			RANKING = RANKING.replace("_item", " ")
			RANKING = RANKING.replace("_rank", " ")
			RANKING = RANKING.replace("\u00a0", ' ')

			RANKING = RANKING.split("#") #convert string to list
			for i in range(len(RANKING)):
				RANKING[i] = RANKING[i].strip()

			print(RANKING)

			data = {
					'NAME':NAME,
					'PRICE':SALE_PRICE,
					'CATEGORY':CATEGORY,
					#'ORIGINAL_PRICE':ORIGINAL_PRICE,
					#'AVAILABILITY':AVAILABILITY,
					'URL':url,
					'RANK':RANKING,
					}
 
			return data
		except Exception as e:
			print("Error")
			print(e)
			return data

def ReadASIN():
	# ASIN_List = csv.DictReader(open(os.path.join(os.path.dirname(__file__),"Asinfeed.csv")))
	ASIN_List = ['B06Y27GL9S', #Dr. Fulbright Kegel Balls
	'''
		'B0089175GE', #Magic Wand Speed Controller Dial Kit
		'B01DCHMIF2', #Magic Wand Free Travel Wand
		'B00MWB5I9S', #All In One 4 Tip Shower Enema System
		'B06WD5QC6H', #Sex Stool
		'B008ASBIU0', #Lube Launcher
		'B01BHAJ6MO', #CleanStream Enema Silicone Attachment Kit
		'B07L9J9518', #Lube Launcher 2 Pack
		'B07GSH8STW', #Strapless Strap On Black
		'B07GSG6LHH', #Strapless Strap On Pink
		'B0091PJDX0', #CleanStream Anal Lubricant
		'B00EF8OL0S', #Lidocaine Lube 8oz.
		'B00375LMSE', #Passion 2 oz.
		'B00375LMRU', #Passion 4 oz.
		'B00711X53U', #Passion 8 oz.
		'B004OEBMAK', #Passion 16 oz.
		'B006JR1N72', #Passion 34 oz.
		'B005MR3IVO', #Passion 55 gal. Water Based Drum
		#'B07MKS1VZY', #Passion 55 gal. Performance Drum
		'B07BH822QF', #Jesse Jane Doggy Style
		'B07BH7TW7K', #Missionary Masturbator
		'B07M5H7WFY', #Jesse Jane Bend Her Over
		'B07M8WN6W5', #Jesse Jane Side Action
	'''
	]
	extracted_data = []
	for ASIN in ASIN_List:
		url = "http://www.amazon.com/dp/"+ASIN
		print ("Processing: " + url)
		extracted_data.append(AmzonParser(url, ASIN))
		sleep(5)
	file_name = time.strftime("%m-%d-%Y") + " Category Scrape.json"
	print(file_name)
	f=open(file_name,'w')
	json.dump(extracted_data,f,indent=4)


'''
#def combineData :
#	date
	for f in glob.glob("/Users/justinm/Documents/Coding/Amazon"):
			with open(f, "r", encoding="UTF-16") as read_file:

'''

if __name__ == "__main__":
	ReadASIN()