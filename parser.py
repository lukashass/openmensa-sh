#!/usr/bin/env python3
from urllib.request import urlopen
from bs4 import BeautifulSoup as parse
from pyopenmensa.feed import LazyBuilder
import datetime


legend = {}
legendcontent = urlopen('http://www.studentenwerk.sh/de/essen/standorte/luebeck/mensa-luebeck/speiseplan.html').read()
legenddocument = parse(legendcontent, 'html.parser')
rawlegend = legenddocument.find(text="Kennzeichnung").parent.parent.div.find('div', {'class': 'text'}).contents[0].strip()

for entry in rawlegend.split(','):
	words = entry.strip().split(' ')
	legend[int(words[0])] = str.join(' ', words[1:])


date = datetime.datetime.now() 

m = '441'
url = 'http://www.studentenwerk.sh/de/menuAction/print.html?m={}&t=d&d={}'.format(m, date.strftime('%Y-%m-%d'))

content = urlopen(url).read()
document = parse(content, 'html.parser')

items = document.find_all('a', {"class": "item"})

canteen = LazyBuilder()

for item in items:
	title = item.strong.string
	numbers = item.small.string
	notes = []
	for number in numbers.split(','):
		number = int(number.strip())
		if number > len(legend):
			continue
		notes.append(legend[number])
	row = item.parent.parent
	price = row.find_all('td')[-1].string
	subprice = price.split('/')
	if len(subprice) == 3:
		prices = {'student': subprice[0], 'employee': subprice[1], 'other': subprice[2]}
	else:
		prices = {'other': price}
	canteen.addMeal(datetime.date(date.year, date.month, date.day), "Essen", title, notes=notes, prices=prices)

print(canteen.toXMLFeed())
