import random
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup

from app import db
from models import Welbextest

url_for_parse = "https://www.sl-24.ru/tablitsa-rasstoyaniy-mezhdu-gorodami-po-rossii.htm"

if __name__ == '__main__':
    response = requests.get(url_for_parse)
    soup = BeautifulSoup(response.text, "lxml")
    delivery_table = soup.find_all('table')[4]
    table_rows = delivery_table.find_all("tr")

    for tr_tag in table_rows:
        name = tr_tag.find("td", class_="name").text.split()[0]
        distance = int(tr_tag.find("td", class_="distance").text)
        count = random.randint(5, 50)
        date = datetime.today() - timedelta(days=random.randint(-40, 40))

        table_record = Welbextest(name=name, distance=distance, count=count, date=date.date())
        db.session.add(table_record)

    db.session.commit()
