#!/usr/bin/env python3
import sys
from urllib.request import urlopen
from bs4 import BeautifulSoup as parse
from pyopenmensa.feed import LazyBuilder
import datetime


if len(sys.argv) < 2 or "--help" in sys.argv[1:] or "-h" in sys.argv[1:]:
	print("Usage: {} <town> [mensa]".format(sys.argv[0]))
	sys.exit()

mensas = {
	"flensburg": {
		"default": 431,
		"munketoft": "4.321"
	},
	"heide": {
		"default": 461
	},
	"kiel": {
		"mensa-i": 411,
		"mensa-ii": 421,
		"kesselhause": 425,
		"schwentine": 426,
		"gaarden": 903
	},
	"luebeck": {
		"default": 441,
		"musikhochschule": 443
	},
	"rendsburg": {
		"default": 901
	}
}

if sys.argv[1] not in mensas:
	print('Town "{}" not found.'.format(sys.argv[1]))
	sys.exit()
town = sys.argv[1]

mensa = "default"
if len(sys.argv) > 2:
	mensa = sys.argv[2]

if mensa not in mensas[town]:
	print('Town "{}" does not have a mensa "{}".'.format(town, mensa))
	sys.exit()


mensa_id = mensas[sys.argv[1]][mensa]

legend = {}
legendcontent = urlopen('http://www.studentenwerk.sh/de/essen/standorte/luebeck/mensa-luebeck/speiseplan.html').read()
legenddocument = parse(legendcontent, 'html.parser')
rawlegend = legenddocument.find(text="Kennzeichnung").parent.parent.div.find('div', {'class': 'text'}).contents[0].strip()

for entry in rawlegend.split(','):
	words = entry.strip().split(' ')
	legend[int(words[0])] = str.join(' ', words[1:])


date = datetime.datetime.now() 

url = 'http://www.studentenwerk.sh/de/menuAction/print.html?m={}&t=d&d={}'.format(mensa_id, date.strftime('%Y-%m-%d'))

content = urlopen(url).read()
document = parse(content, 'html.parser')

items = document.find_all('a', {"class": "item"})

canteen = LazyBuilder()

for item in items:
	title = item.strong.string
	numbers = item.small.string
	notes = []
	if numbers:
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
	canteen.addMeal(datetime.date(date.year, date.month, date.day), "Mittagessen", title, notes=notes, prices=prices)

print(canteen.toXMLFeed())
