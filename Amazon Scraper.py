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


			#Convert to arry to string and clean-up string
			#print(RAW_RANKING)
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
					'SALE_PRICE':SALE_PRICE,
					'CATEGORY':CATEGORY,
					'ORIGINAL_PRICE':ORIGINAL_PRICE,
					'AVAILABILITY':AVAILABILITY,
					'URL':url,
					'RANK':RANKING,
					}
				return data

			if not ORIGINAL_PRICE:
				ORIGINAL_PRICE = SALE_PRICE

			if page.status_code!=200:
				raise ValueError('captha')


			RANKING = RANKING.replace('\n','')
			RANKING = re.sub(r' {[^}]*}','',RANKING)
			RANKING = RANKING.replace(" ",' ')
			RANKING = RANKING.replace(".zg_hrsr", " ")
			RANKING = RANKING.replace("_item", " ")
			RANKING = RANKING.replace("_rank", " ")
			RANKING = RANKING.replace("\u00a0", ' ')

			#print(type(RANKING))
			RANKING = RANKING.split("#") #convert string to list
			for i in range(len(RANKING)):
				RANKING[i] = RANKING[i].strip()
			#print(type(RANKING))
			#while()

			print(RANKING)

			data = {
					'NAME':NAME,
					'SALE_PRICE':SALE_PRICE,
					'CATEGORY':CATEGORY,
					'ORIGINAL_PRICE':ORIGINAL_PRICE,
					'AVAILABILITY':AVAILABILITY,
					'URL':url,
					'RANK':RANKING,
					}
 
			return data
		except Exception as e:
			print(e)

def ReadASIN():
	# ASIN_List = csv.DictReader(open(os.path.join(os.path.dirname(__file__),"Asinfeed.csv")))
	ASIN_List = ['B06Y27GL9S', 
				'B0089175GE',
				'B01DCHMIF2',
				'B00MWB5I9S',
				'B06WD5QC6H',
				]
	extracted_data = []
	for ASIN in ASIN_List:
		url = "http://www.amazon.com/dp/"+ASIN
		print ("Processing: " + url)
		extracted_data.append(AmzonParser(url, ASIN))
		sleep(5)
	f=open('data.json','w')
	json.dump(extracted_data,f,indent=4)


if __name__ == "__main__":
	ReadASIN()