import requests
from bs4 import BeautifulSoup
from urlparse import urlparse
from .const import DEFAULT_HEADERS, DEFAULT_FIELDNAMES


class ScraperManager(object):
    scraper_providers = {}

    def add_scraper_provider(self, domain):
        def wrapper(fn):
            self.scraper_providers[domain] = fn
            return fn
        return wrapper

    def get_scraped_data(self, url):
        if not url:
            return None

        parsed_uri = urlparse(url)
        domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)

        if domain not in self.scraper_providers:
            return None

        return self.scraper_providers[domain](url)


scraper_manager = ScraperManager()


@scraper_manager.add_scraper_provider("http://www.gsmarena.com/")
def gsmarena(url):
    # get response
    print "gsmarena search: %s" % url

    response = requests.get(url, headers=DEFAULT_HEADERS)

    if response.status_code != 200:
        print "warning:", response.content
        return

    soup = BeautifulSoup(response.text, 'lxml')
    data = {}

    for t in soup.select('table'):
        h = []

        for e in t.select('.ttl > a'):
            h.append(e.contents[0])

        c = []

        for e in t.select('.nfo'):
            if e.contents:
                c.append(e.contents[0])

        data.update(dict(zip(h, c)))

    try:
        title = soup.select('.specs-phone-name-title')[0].get_text()
    except Exception, e:
        print "warning: possible wrong link"
        return

    data.update({'Model': title})

    if 'Technology' in data:
        data['Technology'] = str(data['Technology']).strip(
            '<a class="link-network-detail collapse" href="#"></a>')

    print "return: %s" % data

    return data