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
        for url in file:
            page = urlopen(url)

            html_bytes = page.read()
            html = html_bytes.decode("utf-8")

            start = html.find("<title>") + len("<title>")
            end = html.find("</title>")

            title = html[start:end]
            print(title)
            record = {
                'original url': url,
                'title': title
            }

            csvlist.append(record)

    # TODO parse file name from path and replace extension with csv
    # output_file = input_file.split('.')[0] + '.csv'
    output_file = ".data/result.csv"
    print(output_file)
    fieldnames = ['original url', 'title']
    with open(output_file, "w", newline='') as csvfile:
        # TODO write lines from csvlist using DictWriter
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, dialect='excel')
        writer.writeheader()
        for row in csvlist:
            writer.writerow(row)

        pass


if __name__ == '__main__':
    main()