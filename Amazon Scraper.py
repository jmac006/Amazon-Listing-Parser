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

#Global Variables
ASIN_List = ['B06Y27GL9S', #Dr. Fulbright Kegel Balls
			'B0089175GE', #Magic Wand Speed Controller Dial Kit
			'B01DCHMIF2', #Magic Wand Free Travel Wand
			'B00MWB5I9S', #All In One 4 Tip Shower Enema System
			'B06WD5QC6H', #Sex Stool
			'B008ASBIU0', #Lube Launcher
			'B07L9J9518', #Lube Launcher 2 Pack
			'B01BHAJ6MO', #CleanStream Enema Silicone Attachment Kit
			'B07GSH8STW', #Strapless Strap On Black
			'B07GSG6LHH', #Strapless Strap On Pink
			'B01GIPO9B6', #Strapless Strap On Purple
			'B0091PJDX0', #CleanStream Anal Lubricant
			'B00EF8OL0S', #Lidocaine Lube 8oz.
			'B00375LMSE', #Passion 2 oz.
			'B00375LMRU', #Passion 4 oz.
			'B00711X53U', #Passion 8 oz.
			'B004OEBMAK', #Passion 16 oz.
			'B006JR1N72', #Passion 34 oz.
			#'B005MR3IVO', #Passion 55 gal. Water Based Drum
			'B07BH822QF', #Jesse Jane Doggy Style
			'B07BH7TW7K', #Missionary Masturbator
			'B07M5H7WFY', #Jesse Jane Bend Her Over
			'B07M8WN6W5', #Jesse Jane Side Action
			'B07GT67ZZK', #Magic Wand Wireless Controller
			'B07B4NT8FY', #Thunderstick 2.0
			'B00E5PZHOU', #Thunderstick Original
			'B00W89XHQ0', #Black Dual Head Teaser
			'B07C71LBG3', #Dual Vibrating Open Sheath
			'B07HJW6XZ4', #Long Dual Head Teaser
			'B07C6KBR6N', #Medium Dual Head Teaser
			'B07HJRX2FN', #Short Dual Head Teaser
			'B0037A6A1I', #Passion Silicone 2oz.
			'B0071N16KC', #Passion Silicone 4oz.
			'B0071N16Q6', #Passion Silicone 8oz.
			'B00HRINY8S', #CleanStream Silicone Anal 8oz.
			'B00BIDRI4O', #CleanStream 4 oz. AC323
			'B007JHHRTE', #Tenga Passion Kit
			'B07FXXN3TN', #USA Cocks Medium 6 in.
			'B07FXN3HCK', #USA Cocks Medium 7 in.
			'B07FXXNDDL', #USA Cocks Medium 8 in.
			'B07FXXX4JJ', #USA Cocks Medium 9 in.
			'B07FXY77BF', #USA Cocks Medium 10 in.
			'B07PGW1MSR', #Auto Spray Enema Bulb
			]
ASIN_Dict = [] #contains the name along with the ASIN
json_data = [] #list of dictionaries
graph_data = [] #only update graph_data with specific ASIN when selected, instead of populating entire list of ASINs
Products = []
#optionList = []
optionList = [{'label': Products[index]["NAME"], 'value': Products[index]["ASIN"]} for index in range(len(Products))]
server = flask.Flask('app')
server.secret_key = os.environ.get('secret_key', 'secret')


app = dash.Dash('app', server=server)
app.scripts.config.serve_locally = False

file_names = [os.path.basename(x) for x in glob.glob('/Users/justinmac/Documents/Python/Rankings/*.json')]

app.layout = dashHTML.Div([
	dashHTML.H1('Category Rankings'),
	dcc.Dropdown(
		id='my-dropdown',
		options=optionList,
		value=ASIN_List[0],
	),
	dcc.Graph(id='my-graph')
], className="container")

@app.callback(Output('my-dropdown', component_property='options'),
			  [Input('my-graph', component_property='style')])

def update_dropdown(selected_dropdown_value):
	#print(Products)
	return [{'label': Products[index]["NAME"], 'value': Products[index]["ASIN"]} for index in range(len(Products))]

@app.callback(Output('my-graph', 'figure'),
			  [dash.dependencies.Input('my-dropdown', 'value')])

def update_graph(selected_dropdown_value):
	#clear graph_data when called
	#call combineASINData(ASIN)

	combineASINData(selected_dropdown_value)

	Date_range = [graph_data[index]["Date"] for index in range(len(graph_data))]
	
	CategoryData = []

	dayRank = []
	RecentDataIndex = len(graph_data)-1
	#dynamically create the lines on the graph
	#print(graph_data)

	'''
	#check to see if the category has changed since the baseline/initial data by checking if last word of the category matches
	if graph_data[0]["Ranks"][0].split()[-1:] != graph_data[RecentDataIndex]["Ranks"][0].split()[-1:]: #check if the initial category name changed
		info = input("The initial category has changed. Would you like to track the initial data or the recent data?\n")
		if info == 'i' or info == 'initial':
			#change the date range
			for index in range(len(Date_range)):
				if graph_data[0]["Ranks"][0].split()[2:] != graph_data[index]["Ranks"][0].split()[2:]:
					Date_range = Date_range[0:index]
					break
			for i in range(len(graph_data[0]["Ranks"])): #check to see how many rankings there are and iterate through the number of rankings
				for day in range(len(Date_range)): #iterate through the days, find the Rankings, and check to see if there are no rankings for that day (y-coord)
					if graph_data[day]["Ranks"] == []:
						yRank = "Not Available"
					else:
						yRank = graph_data[day]["Ranks"][i].split()[0].replace(",","")
					dayRank.append(yRank)

				categoryName = ' '.join(graph_data[day]["Ranks"][i].split()[2:])
				#print(categoryName)
				CategoryData.append({
					'x': Date_range, 
					'y': dayRank,
					'type': 'line',
					'name': categoryName,
					'line': {
					'width': 3,
					'shape': 'spline'
				}})
				dayRank = []
		else:
			#change the date range
			for index in range(len(Date_range)):
				if graph_data[RecentDataIndex]["Ranks"][0].split()[2:] != graph_data[index]["Ranks"][0].split()[2:]:
					Date_range.pop(0)
			startingIndex = [i for i,_ in enumerate(graph_data) if _['Date'] == Date_range[0]][0] 
			for i in range(len(graph_data[RecentDataIndex]["Ranks"])): #check to see how many rankings there are and iterate through the number of rankings
				for day in range(startingIndex, len(graph_data)): #iterate through the days, find the Rankings, and check to see if there are no rankings for that day (y-coord)
					if graph_data[day]["Ranks"] == []:
						yRank = "Not Available"
					else:
						yRank = graph_data[day]["Ranks"][i].split()[0].replace(",","")
					dayRank.append(yRank)

				categoryName = ' '.join(graph_data[startingIndex]["Ranks"][i].split()[2:])
					#print(categoryName)
				CategoryData.append({
					'x': Date_range, 
					'y': dayRank,
					'type': 'line',
					'name': categoryName,
					'line': {
					'width': 3,
					'shape': 'spline'
				}})
				dayRank = []

		return{
			'data': CategoryData,
			'layout': {
				'showlegend': True,
				#'separators': '.,',
				'margin': {
					'l': 30,
					'r': 20,
					'b': 30,
					't': 20
				}
			}
		}
		'''

	
	#Regular case
	for i in range(len(graph_data[0]["Ranks"])): #check to see how many rankings there are and iterate through the number of rankings
		for day in range(len(Date_range)): #iterate through the days, find the Rankings, and check to see if there are no rankings for that day (y-coord)
			#print(day)
			ranks = []
			categories = []
			for j in range(len(graph_data[day]["Ranks"])):
				
				categoryName = ' '.join(graph_data[day]["Ranks"][j].split()[2:])
				#print(categoryName)
				ranks.append(graph_data[day]["Ranks"][j].split()[0].replace(",",""))
				categories.append(categoryName)
			yRank = {
				'Date': Date_range[day],
				'value': ranks, 
				'category': categories}
			dayRank.append(yRank)

	print(len(dayRank))
		#categoryName = ' '.join(graph_data[day]["Ranks"][i].split()[2:])
		#print(categoryName)
		#print(dayRank[0].items())
		# CategoryData.append({
		# 	'x': Date_range[0:5], 
		# 	'y': [dayRank[i]["value"]],
		# 	'type': 'line', 
		# 	'name': dayRank[i]["category"],
		# 	'line': {
		# 	'width': 3,
		# 	'shape': 'spline',
		# 	'exponentformat': 'none',
		# }})
		# dayRank = []

	#print(dayRank)

	# split the days based on category change

	# for rank in range(len(dayRank[i]["value"])): #one data line per category
	# 	CategoryData.append({
	# 		'x': Date_range, 
	# 		'y': [dayRank[i]["value"][rank] for i in range(len(dayRank))],
	# 		'type': 'line', 
	# 		'name': dayRank[0]["category"][rank],
	# 		'line': {
	# 		'width': 3,
	# 		'shape': 'spline',
	# 		'exponentformat': 'none',
	# 	}})
	# dayRank = []

	# for rank in range(len(dayRank[i]["value"])): #one data line per category
	# 	print(len(dayRank[i]["value"]))
	# 	yCoord = []
	# 	for j in range(len(dayRank)-1):
	# 		#if the number of categories changed
	# 		if dayRank[j]["category"] != dayRank[j+1]["category"]:
	# 			print("Category has changed")
	# 			break
	# 		yCoord.append(dayRank[j]["value"][rank])
	# 	CategoryData.append({
	# 		'x': Date_range, 
	# 		'y': yCoord,
	# 		'type': 'line', 
	# 		'name': dayRank[0]["category"][rank],
	# 		'line': {
	# 		'width': 3,
	# 		'shape': 'spline',
	# 		'exponentformat': 'none',
	# 	}})

	#Finally got the case where it starts off with 3 categories but ends in 1 category but will only stop once category changes, 
	#does not plot new data points
	'''
	for rank in range(len(dayRank[i]["value"])): #one data line per category
		print("Length of day rank value: ", len(dayRank[i]["value"]))
		yCoord = []
		for j in range(len(dayRank)-1):
			#if the number of categories changed
			if dayRank[j]["category"] != dayRank[j+1]["category"]:
				print("Category has changed")
				print(dayRank[j]["category"])
				print(dayRank[j+1]["category"])
				yCoord.append(dayRank[j+1]["value"][rank])
				break

			else:
				yCoord.append(dayRank[j]["value"][rank])
		CategoryData.append({
			'x': Date_range, 
			'y': yCoord,
			'type': 'line', 
			'name': dayRank[0]["category"][rank],
			'line': {
			'width': 3,
			'shape': 'spline',
			'exponentformat': 'none',
		}})
	'''
	#Plots the days where the category changes but not the lines

	'''
	stopDate = 0
	for i in range(len(dayRank)-1):
		for rank in range(len(dayRank[i]["category"])): #one data line per category
			print("Length of day rank value: ", len(dayRank[i]["value"]))
			yCoord = []
			if dayRank[i]["category"] != dayRank[i+1]["category"]:
				print("Category has changed")
				print(dayRank[i]["category"])
				print(dayRank[i+1]["category"])
				yCoord.append(dayRank[i]["value"][rank])
				stopDate = i+1
				#break

			else:
				yCoord.append(dayRank[i+1]["value"][rank])

			print("i ",i)
			print("stop ", stopDate)
			CategoryData.append({
				'x': Date_range[i:stopDate], 
				'y': yCoord,
				'type': 'line', 
				'name': dayRank[i]["category"][rank],
				'line': {
				'width': 3,
				'shape': 'spline',
				'exponentformat': 'none',
			}})
	'''

	#Plots individuals points but not lines VERY CLOSE!!!!!
	'''
	stopDate = len(dayRank)
	for i in range(len(dayRank)-1):
		for rank in range(len(dayRank[i]["category"])): #one data line per category
			print("Length of day rank value: ", len(dayRank[i]["value"]))
			yCoord = []
			if dayRank[i]["category"] != dayRank[i+1]["category"]:
				print("Category has changed")
				print(dayRank[i]["category"])
				print(dayRank[i+1]["category"])
				yCoord.append(dayRank[i]["value"][rank])
				stopDate = i+1
				#break

			else:
				yCoord.append(dayRank[i+1]["value"][rank])

			print("i ",i)
			print("stop ", stopDate)
			CategoryData.append({
				'x': Date_range[i:stopDate], 
				'y': yCoord,
				'type': 'line', 
				'name': dayRank[i]["category"][rank],
				'line': {
				'width': 3,
				'shape': 'spline',
				'exponentformat': 'none',
			}}
)	

	'''
	'''
	works but doesn't separate lines

	catIndex = 0
	dayIndex = 0
	while catIndex < len(dayRank[dayIndex]["value"]): #one data line per category
		#print("Length of dayIndex catIndex value: ", len(dayRank[i]["value"]))
		yCoord = []
		for j in range(len(dayRank)-1):
			#if the number of categories changed
			if dayRank[j]["category"] != dayRank[j+1]["category"]:
				print("Category has changed")
				print(dayRank[j]["category"])
				print(dayRank[j+1]["category"])
				#catIndex = len(dayRank[j+1])
				dayIndex = j+1
				yCoord.append(dayRank[j]["value"][catIndex])
				#break

			else:
				yCoord.append(dayRank[j+1]["value"][catIndex])
		CategoryData.append({
			'x': Date_range, 
			'y': yCoord,
			'type': 'line', 
			'name': dayRank[dayIndex]["category"][catIndex],
			'line': {
			'width': 3,
			'shape': 'spline',
			'exponentformat': 'none',
		}})
		catIndex = catIndex + 1

	graphStartDates = [0]
	for day in range(len(dayRank)):
		for rank in range(len(dayRank[day]["value"])):
			if dayRank[day]["category"] != dayRank[day+1]["category"]: #category has changed
				graphStartDates.append(
	'''			

	#dayRank = []
	'''
	# Displays multiple lines

	catIndex = 0 #keeps track of how many categories in a day
	stopIndex = len(dayRank) #initialize stop index to last date on file
	beginIndex = 0
	j = 0;
	Finished = False
	while catIndex < len(dayRank[beginIndex]["value"])-1: #one data line per category
		#print("Length of Index value: ", len(dayRank[i]["value"]))
		print(catIndex)
		print(len(dayRank[beginIndex]["value"]))
		yCoord = []
		while not Finished: 
			while j < len(dayRank)-1:
				#if the number of categories changed 
				if(catIndex == len(dayRank[j]["value"])-1): #category finished
					print(yCoord)
					Finished = True
					print("cat index:", catIndex)
					catIndex = 0;
					j = beginIndex
					break
				if dayRank[j]["category"] != dayRank[j+1]["category"]:
					#print("Category has changed ", j+1)
					print(dayRank[j]["category"])
					print(dayRank[j+1]["category"])
					#catIndex = len(dayRank[j+1])
					beginIndex = j+1
					j = beginIndex
					#stopIndex = j
					#print(len(dayRank[j]["value"]))
					yCoord.append(dayRank[j]["value"][catIndex])
					break
				else:
					print(j)
					print(catIndex)
					print(dayRank[j]["category"])
					print(dayRank[j+1]["category"])
					yCoord.append(dayRank[j]["value"][catIndex])
				
				j = j + 1;
			print("prints new graph data")
			CategoryData.append({
				'x': Date_range[beginIndex:stopIndex], #Date_range[beginIndex:stopIndex]
				'y': yCoord,
				'type': 'line', 
				'name': dayRank[beginIndex]["category"][catIndex],
				'line': {
				'width': 3,
				'shape': 'spline',
				'exponentformat': 'none',
			}})
			catIndex = catIndex + 1
			if(catIndex == len(dayRank[j]["value"])-1): #category finished
				print(yCoord)
				Finished = True
				break
				'''

	'''
	catIndex = 0 #keeps track of how many categories in a day
	stopIndex = len(dayRank) #initialize stop index to last date on file
	beginIndex = 0
	j = 0;
	Finished = False
	while catIndex <= len(dayRank[beginIndex]["value"])-1: #one data line per category
		#print("Length of Index value: ", len(dayRank[i]["value"]))
		#print("Cat index: ", catIndex)
		#print("Begin index: ", beginIndex)
		#print("condition: ", len(dayRank[beginIndex]["value"])-1)
		yCoord = []
		while not Finished: 
			while j < len(dayRank)-1:
				#if the number of categories changed 
				print(j)
				print("Cat index: ", catIndex)
				print("condition: ", len(dayRank[j]["value"])-1)
				if(catIndex == len(dayRank[j]["value"])-1): #category finished
					print(yCoord)
					Finished = True
					print("Finished cat index:", catIndex)
					#catIndex = 0;
					stopIndex = j
					j = beginIndex #only when it finishes the category, start where it left off
					print("hi")
					break
				if dayRank[j]["category"] != dayRank[j+1]["category"]:
					#print("Category has changed ", j+1)
					print(dayRank[j]["category"])
					print(dayRank[j+1]["category"])
					#catIndex = len(dayRank[j+1])
					if (catIndex != len(dayRank[j]["value"])-1): #if the graph hasn't finished graphing the categories
						j = beginIndex
					beginIndex = j+1 #where the next range should start now there's a new category
					#stopIndex = j
					#print(len(dayRank[j]["value"]))
					yCoord.append(dayRank[j]["value"][catIndex])
					break
				else:
					yCoord.append(dayRank[j]["value"][catIndex])
				
				j = j + 1;
			print("prints new graph data")
			#print(yCoord)
			catIndex = catIndex + 1
			CategoryData.append({
				'x': Date_range[beginIndex:stopIndex], #Date_range[beginIndex:stopIndex]
				'y': yCoord,
				'type': 'line', 
				'name': dayRank[beginIndex]["category"][catIndex],
				'line': {
				'width': 3,
				'shape': 'spline',
				'exponentformat': 'none',
			}})
			
			print("Length of categories: ", len(dayRank[j]["value"]))
			if(catIndex == len(dayRank[j]["value"])-1): #category finished
				print("enters here!")
				Finished = True
				break
	'''

	'''
	Grabs the latest data and plots it (multiple lines) almost there!
	for rank in range(len(dayRank[i]["value"])): #one data line per category
		print("Length of day rank value: ", len(dayRank[i]["value"]))
		yCoord = []
		j = 0
		while j < len(dayRank)-1:
			#if the number of categories changed
			if dayRank[j]["category"] != dayRank[j+1]["category"]:
				print("Category has changed")
				print(dayRank[j]["category"])
				print(dayRank[j+1]["category"])
				yCoord.append(dayRank[j+1]["value"][rank])
				j = j + 1
				break

			else:
				yCoord.append(dayRank[j]["value"][rank])
			j = j + 1
		CategoryData.append({
			'x': Date_range[j:len(dayRank)], 
			'y': yCoord,
			'type': 'line', 
			'name': dayRank[0]["category"][rank],
			'line': {
			'width': 3,
			'shape': 'spline',
			'exponen
	'''
	'''
	Closest I've ever gotten! Multiple lines separating different categories
	
	graphData = []
	stopDate = len(dayRank)
	beginIndex = 0
	i = 0
	rank = 0
	while rank < len(dayRank[i]["category"]): #one data line per category
		xCoord = []
		yCoord = []
		print("hola")
		while i < len(dayRank)-1:
			xCoord.append(dayRank[i]["Date"])
			yCoord.append(dayRank[i]["value"][rank])
			if dayRank[i]["category"] != dayRank[i+1]["category"]:
				graphData.append({'Dates':xCoord,'y':yCoord, 'category':dayRank[i]["category"][rank] })
				if rank < len(dayRank[i]["category"]) - 1:
					print("poop")
					i = beginIndex
					break
				else:
					rank = 0
					beginIndex = i + 1
					i = beginIndex
				break
			i = i + 1
		rank = rank + 1

	print("This is graph Data: \n",graphData)

	

	for j in range(len(graphData)):
		dates = graphData[j]["Dates"]
		CategoryData.append({
			'x': dates, 
			'y': graphData[j]["y"],
			'type': 'line', 
			'name': graphData[j]["category"],
			'line': {
			'width': 3,
			'shape': 'spline',
			'exponentformat': 'none',
		}})
	'''
	graphData = []
	stopDate = len(dayRank)
	beginIndex = 0
	i = 0
	rank = 0

	print("LEN DAY :", len(dayRank)-1)

	for k in range(len(dayRank)):
		print(" ", i, " ", dayRank[k])
	
	while rank < len(dayRank[i]["category"]): #one data line per category
		xCoord = []
		yCoord = []
		
		while i < len(dayRank)-1:
			xCoord.append(dayRank[i]["Date"])
			print(dayRank[i]["Date"])
			yCoord.append(dayRank[i]["value"][rank])
			
			if dayRank[i]["category"] != dayRank[i+1]["category"]:
				print("potato chips")
				graphData.append({'Dates':xCoord,'y':yCoord, 'category':dayRank[i]["category"][rank] })
				print(len(dayRank[i]["category"]) - 1)
				if rank < len(dayRank[i]["category"]) - 1:
					print("rank: ",rank)
					i = beginIndex
					rank = rank + 1
					break
				else: #if it's drawing the last category for the segment, continue the line onto the next subsequent categories
					print("end i: ",i)
					print(len(dayRank[i+1]["category"]))
					rank = 0
					beginIndex = i + 1
					i = beginIndex
					break
			i = i + 1
		if i == len(dayRank)-1:
			break
		#rank = rank + 1

	print("This is graph Data: \n",graphData)

	

	for j in range(len(graphData)):
		dates = graphData[j]["Dates"]
		CategoryData.append({
			'x': dates, 
			'y': graphData[j]["y"],
			'type': 'line', 
			'name': graphData[j]["category"],
			'line': {
			'width': 3,
			'shape': 'spline',
			'exponentformat': 'none',
		}})
	

	return{
		'data': CategoryData,
		'layout': {
			'showlegend': True,
			'exponentformat': 'none',
			'margin': {
				'l': 30,
				'r': 20,
				'b': 30,
				't': 20
			}
		}
	}
	

def AmazonParser(url, ASIN): #Grab information from ASIN URL and export it as a dictionary
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
				print("Captcha Error")
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

def writeToJSONFile(path, fileName, data):
    filePathNameWExt = '/' + path + '/' + fileName
    with open(filePathNameWExt, 'w') as fp:
        json.dump(data, fp,indent=4)

def ReadASINList():
	# ASIN_List = csv.DictReader(open(os.path.join(os.path.dirname(__file__),"Asinfeed.csv")))
	
	for ASIN in ASIN_List:
		url = "http://www.amazon.com/dp/"+ASIN
		print ("Processing: " + url)
		json_data.append(AmazonParser(url, ASIN))
		sleep(5)
	file_name = time.strftime("%m-%d-%Y") + " Category Scrape.json"
	#print(file_name)
	#f=open(file_name,'w')	
	#json.dump(json_data,f,indent=4) #Convert dictionary to JSON file
	filePathName = "Users/justinm/Documents/Coding/Rankings"
	writeToJSONFile(filePathName,file_name,json_data)



def combineASINData(ASIN): #find all data for specific ASIN, while populating optionList
#	date
	print(ASIN)
	path = glob.glob("/Users/justinmac/Documents/Python/Rankings/*.json") #Grab all JSON files from path
	#file_names = [os.path.basename(x) for x in glob.glob('/Users/justinm/Documents/Coding/Rankings/*.json')]
	global Products #declaring variable to modify global variable
	global graph_data
	graph_data = []
	for file in path:
		#f = open(file, 'r')
		data = json.loads(open(file).read())
		for i in data:
			data_ASIN = i['URL'].replace("http://www.amazon.com/dp/","")
			key = {'NAME': i['NAME'], 'ASIN': data_ASIN}
			#if key not in Products: #ensure no duplicates
			if not any(p['ASIN'] == data_ASIN for p in Products): #ensures no duplicates
				Products.append(key) #append dictionary to Product array only if ASIN is not in the list
			if i['URL'] == ("http://www.amazon.com/dp/" + ASIN):
				#print(file)
				rankings = i["RANK"]
				del rankings[0] #remove "Amazon Best Sellers Rank title from list"
				file_date = os.path.basename(file).split()[0]
				if file_date == "Baseline": #Baseline data
					graph_data.insert(0,{'Date': i["DATE"],'Ranks': rankings})
				else:
					graph_data.append({'Date': file_date,'Ranks': rankings})
	#print(graph_data)
	#Products= list(set(Products)) #remove duplicate names			
	#dates = [date.split()[0] for date in file_names] #split file name to list of dates
	#print(dates)
	global optionList
	optionList = [{'label': Products[index]["NAME"], 'value': Products[index]["ASIN"]} for index in range(len(Products))]
	#print(optionList)

if __name__ == "__main__":
	'''
	grabInfo = input("Do you want to gather new information from the list of ASINs? (y/n)\n")
	if grabInfo == 'y':
		print("Gathering new information on ASINs")
		ReadASINList() #Read New Data
	'''
	
	combineASINData("Initializing")
	#print(graph_data)
	app.run_server(debug=False) #Build Graph using Dash