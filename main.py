import smtplib
import ssl
import requests
import selectorlib
import sqlite3
import time
import os


URL = "https://programmer100.pythonanywhere.com/tours/"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
connection = sqlite3.connect('data.db')


def scrape(url):
    """Scrape the page source from the URL"""
    response = requests.get(url, headers=HEADERS)
    text = response.text
    return text


def extract(source):
    extractor = selectorlib.Extractor.from_yaml_file("extract.yaml")
    value = extractor.extract(source)['tours']
    return value


def send_email(message):
    host = "smtp.gmail.com"
    port = 465
    username = os.environ.get("USERNAME")
    password = os.environ.get("PASSWORD")
    receiver = os.environ.get("RECEIVER")
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(host, port, context=context) as server:
        server.login(username, password)
        server.sendmail(username, receiver, message)
    print("Email was sent!")


def store(extracted_data):
    line = extracted_data.split(',')
    line = [item.strip() for item in line]
    cursor = connection.cursor()
    cursor.execute("INSERT INTO events VALUES(?,?,?)", line)
    connection.commit()


def read(extracted_data):
    line = extracted_data.split(',')
    line = [item.strip() for item in line]
    band, city, date = line
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM events WHERE band=? AND city=? AND date=?", (band, city, date))
    rows = cursor.fetchall()
    print(rows)
    return rows


if __name__ == "__main__":
    while True:
        scraped = scrape(URL)
        extracted = extract(scraped)
        print(extracted)
        if extracted != "No upcoming tours":
            row = read(extracted)
            if not row:
                store(extracted)
                send_email(f'Subject:New event!\n\nHey new event was found! \n{extracted}')
        time.sleep(2)
