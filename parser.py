#!/usr/bin/env python3
import sys
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup as parse, NavigableString, Tag
from pyopenmensa.feed import LazyBuilder
import datetime


if len(sys.argv) < 2 or "--help" in sys.argv[1:] or "-h" in sys.argv[1:]:
	print("Usage: {} <town> [mensa] [days]".format(sys.argv[0]))
	sys.exit()

mensas = {
	"flensburg": {
		"default": 431,
		"madrid": "4.321",
		"b": "433",
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
	"osterroenfeld": {
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
legendcontent = urlopen('https://www.studentenwerk.sh/de/essen/standorte/luebeck/mensa-luebeck/speiseplan.html').read()
legenddocument = parse(legendcontent, 'html.parser')
legends = legenddocument.find(text='Allergene und Zusatzstoffe').parent.parent.find_all('table', {'class': 'ingredientsLegend'})

for current_legend in legends:
	ingredientKeys = current_legend.find_all('td', {'class': 'ingredientKey'})
	for ingredientKey in ingredientKeys:
		finalKey = ingredientKey.text.strip()
		finalValue = ingredientKey.findNext('td', {'class': 'ingredientName'}).text.strip()
		legend[finalKey] = finalValue

canteen = LazyBuilder()

date = datetime.datetime.now()
days = 1
if len(sys.argv) > 3:
	days = int(sys.argv[3])

for i in range(0, days):
	url = 'https://www.studentenwerk.sh/de/menuAction/print.html?m={}&t=d&d={}'.format(mensa_id, date.strftime('%Y-%m-%d'))

	content = urlopen(url).read()
	document = parse(content, 'html.parser')

	items = document.find_all('a', {"class": "item"})

	for item in items:
		title = ""

		def extract(part, title, notes):
			if isinstance(part, NavigableString):
				title += str(part)
			elif isinstance(part, Tag):
				if part.name == "small":
					note_string = part.string.strip(" ()")
					notes.update(map(lambda x: x.strip(), note_string.split(",")))
				elif part.name == "br" and not part.text:
					if title[-1] != " ":
						title += " "
				else:
					for child in part.children:
						title, notes = extract(child, title, notes)
			return title, notes

		title, notes = extract(item.strong, "", set())
		title = re.sub("\s+", " ", title).strip()
		if len(title) < 1:
			continue

		notes = map(lambda x: legend[x] if x in legend else x, notes)

		row = item.parent.parent
		price = row.find_all('td')[-1].string
		prices = {}
		if price:
			subprice = price.split('/')
			if len(subprice) == 3:
				prices = {'student': subprice[0], 'employee': subprice[1], 'other': subprice[2]}
			else:
				prices = {'other': price}
		canteen.addMeal(datetime.date(date.year, date.month, date.day), "Mittagessen", title, notes=notes, prices=prices)

	date = date + datetime.timedelta(1)

print(canteen.toXMLFeed())
