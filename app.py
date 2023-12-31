#!.venv/bin/python

import csv
import logging
import re
import sys
import urllib.request
import urllib.error

# Configure logging
logging.basicConfig(filename=".data/scraper.log", 
                    filemode='a', 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def get_phones(html) -> list:
    phones = []

    # Find phone
    pattern = re.compile(r"tel:\+?[\d ()\-]{6,17}(\"|\'|\\\\)")
    for found in re.finditer(pattern, html):
        phone = found.group()[4:-1]
        phone = re.sub("-| |\(|\)", "", phone)
        if not phone in phones:
            phones.append(phone)

    # Try different method if 'tel:' was not 
    if not phones:
        
        # Tricky part, because I can't guess how webmaster write a phone number (how many digits and spaces)
        # pattern = re.compile(r"\+?\d\s?-?\(?\d{3,4}\)?\s?-?[\d\s-]{6,12}")
        # But because we are focused on Russia now, let's continue with line below
        # And in this case focus on text between tags
        pattern = re.compile(r">\+?(7|8)\s?\-?\(?\d{3,4}\)?\s?\-?[\d\s\-]{5,13}<")
        for found in re.finditer(pattern, html):
            phone = re.sub("<|>|-| |\(|\)", "", found.group()).strip()
            if not phone in phones:
                phones.append(phone)
    return phones


def get_emails(html) -> list:
    # Look up for e-mail
    pattern = re.compile(r"mailto:[\-_\.\w]{1,20}@[\w\-]{1,20}\.[a-z]{2,3}", re.IGNORECASE)
    emails = []
    for found in re.finditer(pattern, html):
        email = re.sub("mailto:", "", found.group().lower()).strip()
        if not email in emails:
            emails.append(email)
    
    # Try alternative method to find emails on page
    if not emails:

        # Simplified regex for e-mail address, because its purpose not to validate, only find similar
        # pattern = re.compile(r"[!#$%&'*+-/=?^_`{|}~\w]{1,64}@[\w-]{1,63}\.[a-zA-Z]{2,3}")
        # Let's be reasonable: noone will use full-length e-mail addres for contact on commercial website
        # So let's limit to 20 characters - that's more than enough, 
        # Even special chars not really need to be here in such case
        # And since address like text is present in some attributes, let's look only between tags
        pattern = re.compile(r">[\-_\.\w]{1,20}@[\w\-]{1,20}\.[a-z]{2,3}<", flags=re.IGNORECASE)       
        for found in re.finditer(pattern, html):

            # Throw away tags surrounding email address
            email = re.sub("<|>", "", found.group().lower()).strip()
            if not email in emails:

                # Don't include mail.ru nonsense
                if (not 'Rating@Mail.ru'.lower() in email and
                    not 'Рейтинг@Mail.ru'.lower() in email):
                    emails.append(email)      
    return emails


def get_telegram_links(html) -> list:
    # Look for a telegram link
    pattern = re.compile(r"((t\.me/)|(tlgg\.ru/))[\w_]{5,32}")
    telega = []
    for found in re.finditer(pattern, html):
        if not found.group() in telega:
            telega.append(found.group())
    return telega


def get_whatsapp_links(html) -> list:
    # Look for  whatsapp link
    pattern = re.compile(r"((wa\.me/)|(api\.whatsapp\.com/send\?phone=)|(wa\.clck\.bar/))\d{8,15}", re.IGNORECASE)
    whatsapp = []
    for found in re.finditer(pattern, html):
        if not found.group() in whatsapp:
            whatsapp.append(found.group())

    return whatsapp


def get_vkontakte_links(html) -> list:
        # Look for Vkontakte link
    pattern = re.compile(r"vk.com/\w{6,20}(\"|\')", re.IGNORECASE)
    vkontakte = []
    for found in re.finditer(pattern, html):
        if not found.group()[:-1] in vkontakte:
            vkontakte.append(found.group()[:-1])
    return vkontakte


def main():

    # Check for command-line usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python app.py <file to process>")

    csvlist = []
    input_file = sys.argv[1]

    # Just in case someone don't like crawlers pretend that it's browser
    user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
    headers = {'User-Agent': user_agent}
    
    with open(input_file, "r") as file:
        for counter, url in enumerate(file, start=1):

            # Be safe if there is empty string in file
            if not url or re.match("^\s*$", url):
                continue
            req = urllib.request.Request(url, headers=headers)
            title = 'Парсер не справился, справится ли человек? :)'
            phones = []
            emails = []
            telega = []
            whatsapp = []
            vkontakte = []

            # Get page
            try:
                with urllib.request.urlopen(req) as response:
                    html = response.read().decode("utf-8")
            except urllib.error.HTTPError as e:
                logger.error(f"Error while parsing '{url}': \n{e}")
            except urllib.error.URLError as e:
                logger.error(f"Error while parsing '{url}': \n{e}")
            except UnicodeDecodeError as e:
                logger.error(f"Error while parsing '{url}': \n{e}")
            except ValueError as e:
                logger.error(f"Error while parsing '{url}': \n{e}")
            else:

                # Find title
                pattern = "<title.*?>.*?</title.*?>"
                found = re.search(pattern, html, flags=re.IGNORECASE | re.DOTALL)
                if found:
                    title = re.sub("<.*?>", "", found.group()).strip()
                else:
                    title = ''
                
                # Just in case something went wrong limit length of the title
                if len(title) > 256:
                    title = title[:255]

                # Get information
                phones = get_phones(html)
                emails = get_emails(html)
                telega = get_telegram_links(html)  
                whatsapp = get_whatsapp_links(html)
                vkontakte = get_vkontakte_links(html)
                
                # If not full information gathered try look up at Contacts page
                if not phones or not emails or not telega or not whatsapp or not vkontakte:

                    # try to get Contacts page
                    new_pattern = re.compile(r"((http://)|(https://))?[\w.-]{4,253}\/")
                    found = new_pattern.search(url)
                    if found:
                        contacts_url = found.group() + 'contacts'

                        # Get Contacts page contents
                        new_req = urllib.request.Request(contacts_url, headers=headers)
                        try:
                            with urllib.request.urlopen(new_req) as new_response:
                                contacts_page = new_response.read().decode("utf-8")
                        except urllib.error.HTTPError as e:
                            logger.error(f"Error while parsing '{contacts_url}': \n{e}")
                        except urllib.error.URLError as e:
                            logger.error(f"Error while parsing '{contacts_url}': \n{e}")
                        except UnicodeDecodeError as e:
                            logger.error(f"Error while parsing '{contacts_url}': \n{e}")
                        except ValueError as e:
                            logger.error(f"Error while parsing '{contacts_url}': \n{e}")
                        else:

                            # Try to fill gaps
                            if not phones:
                                phones = get_phones(contacts_page)
                            if not emails:
                                emails = get_emails(contacts_page)
                            if not telega:
                                telega = get_telegram_links(contacts_page)
                            if not whatsapp:
                                whatsapp = get_whatsapp_links(contacts_page)
                            if not vkontakte:
                                vkontakte = get_vkontakte_links(contacts_page)   

                        logger.info(f"Where am I? {contacts_url}") 
                else:
                    logger.info(f"Where am I? {url}")                           

            finally:
                # Construct a row with gathered information
                record = {
                    '№': counter,
                    'original url': url,
                    'title': title,
                    'phone': ', '.join(phones),
                    'e-mail': ', '.join(emails),
                    'telegram link': ', '.join(telega),
                    'whatsapp link': ', '.join(whatsapp),
                    'vkontakte link': ', '.join(vkontakte)
                }

                # Add row of gathered information to list
                csvlist.append(record)

    # Prepare file name to write into, open file and write row by row, starting with header
    output_file = input_file.rsplit('.',1)[0] + '.csv'
    fieldnames = ['№', 'original url', 'title', 'phone', 'e-mail','telegram link','whatsapp link', 'vkontakte link']
    with open(output_file, "w", newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, dialect='excel')
        writer.writeheader()
        for row in csvlist:
            writer.writerow(row)


if __name__ == '__main__':
    main()