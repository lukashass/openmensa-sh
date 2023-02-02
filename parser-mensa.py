#!/usr/bin/env python3
import sys
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup as parse, NavigableString, Tag
from pyopenmensa.feed import LazyBuilder
import datetime


if len(sys.argv) < 3 or "--help" in sys.argv[1:] or "-h" in sys.argv[1:]:
    print("Usage: {} <town> <mensa>".format(sys.argv[0]))
    sys.exit()

mensas = {
    "flensburg": {
        "mensa": 7,
        # "cafeteria": 14,
    },
    "heide": {"mensa": 11},
    "kiel": {
        "mensa-i": 1,
        "mensa-ii": 2,
        "kesselhause": 4,
        "schwentine": 5,
        "gaarden": 3,
        # "cafeteria-i": 413,
        # "cafeteria-ii": 423,
        "cafeteria-fh": 6,
    },
    "luebeck": {
        "mensa": 8,
        # "cafeteria": 442,
        "musikhochschule": 9,
    },
    "wedel": {"cafeteria": 10},
}

town = sys.argv[1]
mensa = sys.argv[2]

if town not in mensas:
    print('Town "{}" not found.'.format(sys.argv[1]))
    sys.exit()

if mensa not in mensas[town]:
    print('Town "{}" does not have a mensa "{}".'.format(town, mensa))
    sys.exit()

mensa_id = mensas[sys.argv[1]][mensa]

legend = {}
legendcontent = urlopen(
    'https://studentenwerk.sh/de/essen-uebersicht?ort=1&mensa=1').read()
legenddocument = parse(legendcontent, 'html.parser')
legends = legenddocument.find_all("div", {"class": "filterbutton"})

for current_legend in legends:
    legend[current_legend['data-wert']
           ] = current_legend.select_one('span:not(.abk)').string.strip()

canteen = LazyBuilder()

# parse current and next week
for next_week in range(0, 2):
    url = "https://studentenwerk.sh/de/mensaplandruck?mensa={}&nw={}".format(
        mensa_id, next_week)

    content = urlopen(url).read()
    document = parse(content, "html.parser")

    days = document.find_all("div", {"class": "tag_headline"})

    for day in days:
        date = datetime.datetime.strptime(day.attrs['data-day'], '%Y-%m-%d')

        meals = day.find_all("div", {"class": "mensa_menu_detail"})

        for meal in meals:
            notes = []
            notes.extend(meal['data-arten'].split('|'))
            notes.extend(meal['data-allergene'].split('|'))
            notes.extend(meal['data-zusatzstoffe'].split('|'))
            notes = list(filter(lambda x: len(x) > 0, notes))
            notes = list(map(lambda x: legend[x], notes))

            category = meal.find(
                "div", {"class": "menu_art"}).contents[0].string.strip()

            title = ""

            def extract(part, title):
                if isinstance(part, NavigableString):
                    title += str(part)
                elif isinstance(part, Tag):
                    if part.name == "small":
                        note_string = part.string.strip(" ()")
                    else:
                        if part.name == "br":
                            if title[-1] != " ":
                                title += " "
                        for child in part.children:
                            title = extract(child, title)
                return title

            title = extract(
                meal.find("div", {"class": "menu_name"}), "")
            title = re.sub("\s+", " ", title).strip()
            if len(title) < 1:
                continue

            price = meal.find("div", {"class": "menu_preis"}).string.strip()
            prices = {}
            if price:
                subprice = price.split("/")
                if len(subprice) == 3:
                    prices = {
                        "student": subprice[0],
                        "employee": subprice[1],
                        "other": subprice[2],
                    }
                else:
                    prices = {"other": price}
            canteen.addMeal(
                datetime.date(date.year, date.month, date.day),
                category,
                title,
                notes=notes,
                prices=prices,
            )

print(canteen.toXMLFeed())
