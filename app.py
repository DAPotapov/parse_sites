import csv
# import os
import sys
import re

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

            # Get page
            page = urlopen(url)            
            html_bytes = page.read()
            html = html_bytes.decode("utf-8")

            # Find title
            start = html.find("<title>") + len("<title>")
            end = html.find("</title>")
            title = html[start:end].strip().replace("|", "-")
            print(title)

            # Find phone
            # start = html.find("\"tel:") + len("\"tel:")
            # end = html.find("\"")
            start = 0
            pattern = re.compile(r"\"tel:\+?\d{6,11}\"")
            phones = []
            while start < len(html):
                found = pattern.search(html, pos=start)
                if found:
                    start = found.end()
                    phone = found.group()[5:-1]
                    # TODO take in acount that numbers starting with 7 or 8 are the same
                    if not phone in phones:
                        phones.append(phone)

                # Stop searching if nothing in the end of page
                else:
                    break

            # Try different method if 'tel:' doesn't work
            if not phones:
                pass

            # Write to row
            record = {
                '№': counter,
                'original url': url,
                'title': title,
                'phone': ', '.join(phones),
                'e-mail':''
            }

            # Add row of gathered information to list
            csvlist.append(record)

    # Prepare file name to write into, open file and write row by row, starting with header
    output_file = input_file.rsplit('.',1)[0] + '.csv'
    fieldnames = ['№', 'original url', 'title', 'phone', 'e-mail']
    with open(output_file, "w", newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, dialect='excel')
        writer.writeheader()
        for row in csvlist:
            writer.writerow(row)


if __name__ == '__main__':
    main()