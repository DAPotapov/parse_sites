#!.venv/bin/python

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
            pattern = re.compile(r"\"tel:\+?\d{6,11}\"")
            phones = []
            for found in re.finditer(pattern, html):
                phone = found.group()[5:-1]
                if not phone in phones:
                    phones.append(phone)

            # Try different method if 'tel:' doesn't work
            if not phones:
                # Tricky part, because I can't guess how webmaster write a phone number (how many digits and spaces)
                pattern = re.compile(r"\+?\d\s?-?\(?\d{3,4}\)?\s?-?[\d\s-]{6,12}")
                for found in re.finditer(pattern, html):
                    phone = found.group().strip()
                    phone = re.sub("-| |\(|\)", "", phone)
                    if not phone in phones:
                        phones.append(phone)

            # Find e-mail
            pattern = re.compile(r"mailto:")
            emails = []
            for found in re.finditer(pattern, html):
                ending_pattern = re.compile(r"\"|\'")
                ending_found = ending_pattern.search(html, pos=found.end())
                if ending_found:
                    email = html[found.end():ending_found.start()].strip()
                    if not email in emails:
                        emails.append(email)

            # Write to row
            record = {
                '№': counter,
                'original url': url,
                'title': title,
                'phone': ', '.join(phones),
                'e-mail': ', '.join(emails)
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