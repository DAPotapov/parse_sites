import os
from dotenv import load_dotenv
from urllib.request import urlopen

url = "http://olympus.realpython.org/profiles/aphrodite"
page = urlopen(url)

html_bytes = page.read()
html = html_bytes.decode("utf-8")

start = html.find("<title>") + len("<title>")
end = html.find("</title>")

title = html[start:end]
print(title)
