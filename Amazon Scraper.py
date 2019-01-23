'''
Scrape Amazon Data to JSON File
Created by: Justin Mac
Library Dependencies:
Install Python, Python PIP, Python Requests, and Python LXML

Graph Library Dependencies: dash, dash-html-components, dash-core-components, dash-table

'''
from lxml import html  
import csv,os,json
import requests
#from exceptions import ValueError
from time import sleep
import re
import time
import glob #import all files in folder

#Dash Dependencies
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as dashHTML
import plotly.graph_objs as go
import flask
import pandas as pd

#Global Variables
ASIN_List = ['B06Y27GL9S', #Dr. Fulbright Kegel Balls
			]
ASIN_Dict = [] #contains the name along with the ASIN
extracted_data = []
graph_data = [] #only update graph_data with specific ASIN when selected, instead of populating entire list of ASINs
Products = []
server = flask.Flask('app')
server.secret_key = os.environ.get('secret_key', 'secret')

dataFrame = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/hello-world-stock.csv')

app = dash.Dash('app', server=server)
app.scripts.config.serve_locally = False
dcc._js_dist[0]['external_url'] = 'https://cdn.plot.ly/plotly-basic-latest.min.js'

file_names = [os.path.basename(x) for x in glob.glob('/Users/justinm/Documents/Coding/Rankings/*.json')]

#optionList = [{'label': }]
optionList = [{'label': Products[index]["NAME"], 'value': Products[index]["ASIN"]} for index in range(len(Products))]
app.layout = dashHTML.Div([
	dashHTML.H1('Category Rankings'),
	dcc.Dropdown(
		id='my-dropdown',
		options=[
			{'label': 'Tesla', 'value': 'TSLA'},
			#{'label': optionList[0]["NAME"], 'value': 'AAPL'},
			{'label': 'Coke', 'value': 'COKE'}
		],
		value='Passion'
	),
	dcc.Graph(id='my-graph')
], className="container")


@app.callback(Output('my-graph', 'figure'),
			  [Input('my-dropdown', 'value')])

def update_graph(selected_dropdown_value):
	#clear graph_data when called
	#call combineData(ASIN)

	#print(DatabyCategory)
	#print(range(len(graph_data)-1))
	Date_range = [graph_data[index]["Date"] for index in range(len(graph_data))]
	print(Date_range)

	'''
	Category1 = [graph_data[index]["Ranks"][0].split()[0] for index in range(len(graph_data))]
	#Category1 = [Category1[index].replace(",",'') for index in range(len(Category1))]
	#Category1 = list(map(int,Category1))
	#print(Category1)
	Category2 = [graph_data[index]["Ranks"][1].split()[0] for index in range(len(graph_data))] #worried about out of range
	#Category2 = [Category2[index].replace(",",'') for index in range(len(Category2))]
	#Category2 = list(map(int,Category2))
	#print(Category2)
	Category3 = [graph_data[index]["Ranks"][2].split()[0] for index in range(len(graph_data))]
	#Category3 = [Category3[index].replace(",",'') for index in range(len(Category3))]
	#Category3 = list(map(int,Category3))
	#print(Category3)
	'''
	CategoryData = []
	print(graph_data)

	dayRank = []
	for i in range(len(graph_data[1]["Ranks"])): #check to see how many rankings there are and iterate through the number of rankings
		for day in range(len(Date_range)): #iterate through the days, find the Rankings, and check to see if there are no rankings for that day (y-coord)
			if graph_data[day]["Ranks"] == []:
				yRank = "Not Available"
			else:
				yRank = graph_data[day]["Ranks"][i].split()[0].replace(",","")
			dayRank.append(yRank)

		CategoryData.append({'x': Date_range, 
			'y': dayRank,
			'type': 'scatter',
			'line': {
			'width': 3,
			'shape': 'spline'
			}})
		dayRank = []
	
	print(CategoryData)
	return{
		'data': CategoryData,
		'layout': {
			'margin': {
				'l': 30,
				'r': 20,
				'b': 30,
				't': 20
			}
		}
	}


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
	
	for ASIN in ASIN_List:
		url = "http://www.amazon.com/dp/"+ASIN
		print ("Processing: " + url)
		extracted_data.append(AmzonParser(url, ASIN))
		sleep(5)
	file_name = time.strftime("%m-%d-%Y") + " Category Scrape.json"
	print(file_name)
	f=open(file_name,'w')
	json.dump(extracted_data,f,indent=4) #Convert dictionary to JSON file



def combineData(ASIN):
#	date
	path = glob.glob("/Users/justinm/Documents/Coding/Rankings/*.json") #Grab all JSON files from path
	#file_names = [os.path.basename(x) for x in glob.glob('/Users/justinm/Documents/Coding/Rankings/*.json')]
	global Products #declaring variable to modify global variable
	for file in path:
		#f = open(file, 'r')
		data = json.loads(open(file).read())
		for i in data:
			data_ASIN = i['URL'].replace("http://www.amazon.com/dp/","")
			key = {'NAME': i['NAME'], 'ASIN': data_ASIN}
			Products.append(key)
			if i['URL'] == ("http://www.amazon.com/dp/" + ASIN):
				#print(file)
				rankings = i["RANK"]
				del rankings[0] #remove "Amazon Best Sellers Rank title from list"
				file_date = os.path.basename(file).split()[0]
				graph_data.append({'Date': file_date,'Ranks': rankings})

	
	#Products= list(set(Products)) #remove duplicate names			
	#dates = [date.split()[0] for date in file_names] #split file name to list of dates
	#print(dates)


if __name__ == "__main__":
	#ReadASIN() #Read new Data
	combineData("B06Y27GL9S")
	#print(Products)
	#print(graph_data)
	app.run_server() #Build Graph using Dash