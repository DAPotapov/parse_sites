import csv
import os
import sys

# from dotenv import load_dotenv
from urllib.request import urlopen

def main():

    # Check for command-line usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python app.py <file to process>")

    with open(sys.argv[1], "r") as file:
        for url in file:
            page = urlopen(url)

            html_bytes = page.read()
            html = html_bytes.decode("utf-8")

            start = html.find("<title>") + len("<title>")
            end = html.find("</title>")

            title = html[start:end]
            print(title)


if __name__ == '__main__':
    main()