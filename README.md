# Amazon-Listing-Parser
Scrape Amazon listing data (Listing Name, Pricing, Category, Sales Ranking, URL, and Availability) by inputting list of ASINs. Created using Python and LXML. Exports the data to a JSON file.

Graphs the changes in category rankings of the Amazon listing.

Make sure to replace "User-Agent" data with your own data. Find out your user agent header string here: https://www.whatismybrowser.com/detect/what-is-my-user-agent

Library dependencies:
- Install Python, Python PIP, Python Requests, and Python LXML

- Install Dash Dependenceies: dash, dash.dependencies, dash_core_components, dash_html_components, flask

Before running the program:
Must specify path of where JSON 'Rankings' folder is. Specify ASINs to scrape under variable ASIN_List.

Graph output of Amazon best seller ranking
(*Must have archive of rankings, or run the program over a period of at least two days*)

<br />
<br />

![alt text](https://github.com/jmac006/Amazon-Listing-Parser/blob/master/category.PNG)

Because Amazon consistently changes listing categories, I had to modify my code to show the data with the category changes. So, it plots a new line whenever a category change occurs.

To access and share the ranking graph data with another computer, you must deploy the local server:
- Download and install ngrok and 
  - Mac: brew cask install ngrok
  - Windows: install from https://ngrok.com/download
  - Type *ngrok http 8050* into the terminal to forward the localhost, and it will output a ngrok domain
  
