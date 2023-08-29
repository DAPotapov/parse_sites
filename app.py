import csv
import os
import sys

# from dotenv import load_dotenv
from urllib.request import urlopen

def main():

    # Check for command-line usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python app.py <file to process>")

    csvlist = []
    input_file = sys.argv[1]
    with open(input_file, "r") as file:
        for counter, url in enumerate(file, start=1):
            page = urlopen(url)
            
            html_bytes = page.read()
            html = html_bytes.decode("utf-8")

            start = html.find("<title>") + len("<title>")
            end = html.find("</title>")

            title = html[start:end]
            print(title)
            record = {
                '№': counter,
                'original url': url,
                'title': title
            }

            csvlist.append(record)

    output_file = input_file.rsplit('.',1)[0] + '.csv'
    fieldnames = ['№', 'original url', 'title']
    with open(output_file, "w", newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, dialect='excel')
        writer.writeheader()
        for row in csvlist:
            writer.writerow(row)


if __name__ == '__main__':
    main()