

'''
Author:
Sadique Adnan Siddiqui <sadique.adnan@gmail.com>
Code modified from : https://python.gotrained.com/scraping-facebook-posts-comments/
'''



import requests
import re
import json
import logging
from extract_comments import json_to_obj, make_login, crawl_profile
import sys
import argparse

def save_data(data,output_file):
    """Converts data to JSON.
    """
    with open(output_file +'.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)



def main(argv):
    parser = argparse.ArgumentParser(add_help=False,
                                     description=('Download Facebook comments without using the Facebook API'))
    parser.add_argument('--help', '-h', action='help', default=argparse.SUPPRESS,
                        help='Show this help message and exit')
    parser.add_argument('--output', '-o', help='Output filename', required=True)
    parser.add_argument('--limit', '-l', type=int, help='Limit the number of posts to scrape', required=True)
    try:
        
        args = parser.parse_args(argv)
        logging.basicConfig(level=logging.INFO)
        base_url = 'https://mobile.facebook.com'
        session = requests.session()
        output_file = args.output

        # Extracts credentials for the login and all of the profiles URL to scrape
        credentials = json_to_obj('credentials.json')
        profiles_urls = json_to_obj('profiles_urls.json')

        make_login(session, base_url, credentials)

        posts_data = None
        for profile_url in profiles_urls:
            posts_data = crawl_profile(session, base_url, profile_url, args.limit)
        logging.info('[!] Scraping finished. Total: {}'.format(len(posts_data)))
        logging.info('[!] Saving.')
        save_data(posts_data, output_file)
        
    except Exception as e:
        print('Error:', str(e))
        sys.exit(1)    

    
if __name__ == "__main__":
    main(sys.argv[1:])
