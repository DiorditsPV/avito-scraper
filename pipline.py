from main.scraper import scrape
from main.parser import parse_html

from datetime import datetime

timestamp_marker = datetime.now().strftime("%Y%m%d_%H%M%S")

scrape(enable_pagination=False, timestamp_marker=timestamp_marker)
parse_html(timestamp_marker=timestamp_marker)

