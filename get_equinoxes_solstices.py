'''
The main script to calculate and print coordinates in the console.
'''

import argparse
from datetime import datetime
from core import get_coords

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('year', type=int, nargs='?', default=datetime.now().year, help="Format: yyyy (default: %(default)s)")
    
    year = parser.parse_args().year
    
    try:
        results = get_coords(year)

        print (f'The ICRS coordinates (J2000) of equinoxes and solstices in the year {year} are:')
        print ('Vernal Equinox:')
        print (f'  ra = {results["vernal_ra"]}, dec = {results["vernal_dec"]}')
        print ('Autumnal Equinox:')
        print (f'  ra = {results["autumnal_ra"]}, dec = {results["autumnal_dec"]}')
        print ('Summer solstice:')
        print (f'  ra = {results["summer_ra"]}, dec = {results["summer_dec"]}')
        print ('Winter solstice:')
        print (f'  ra = {results["winter_ra"]}, dec = {results["winter_dec"]}')
    
    except Exception as e:
        print(f'Error: {str(e)}')

if __name__ == "__main__":
    main()
