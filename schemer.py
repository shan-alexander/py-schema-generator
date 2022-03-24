import click
from bs4 import BeautifulSoup
from selenium import webdriver
import json 
import rake #for SEO keyword extraction

schema = {
    "@context": "https://schema.org/",
    "@graph": []
}

def get_page_keywords(soup):
    stoppath = 'smart-stoplist.txt'
    # Each word has at least 4 characters
    # Each phrase has at most 4 words
    # Each keyword appears in the text at least 2 times
    rake_object = rake.Rake(stoppath, 4, 4, 2)
    html_body = soup.body
    # remove all javascript and stylesheet code
    [x.extract() for x in html_body.find_all('script')]
    [x.extract() for x in html_body.find_all('style')]
    [x.extract() for x in html_body.find_all('meta')]
    [x.extract() for x in html_body.find_all('noscript')]
    body_string = html_body.get_text()
    body_string_list = body_string.split()
    body_string = ' '.join(body_string_list)
    print("-------------")
    print(body_string)
    print("-------------")
    keywords = rake_object.run(body_string)
    # remove keyword-phrases less than 2 words
    keywords = [x for x in keywords if len(x[0].split()) > 1]
    keywords = [x[0] for x in keywords]
    print("HTML Page Keywords:", keywords)
    return keywords

def get_soup():
    print("Starting web driver...")
    driver = webdriver.Chrome('../../Downloads/chromedriver_win32/chromedriver')
    driver.get('https://www.pixelz.com')
    content = driver.page_source
    soup = BeautifulSoup(content, features="lxml")
    return soup 
    
def get_webpage_schema(soup):
    print("Initializing WebPage Schema")
    results = []
    for element in soup.findAll("h1"):
        results.append(element.text)
    page_h1 = results[0]
    # title = soup.find("meta", property="og:title")
    title = soup.title
    title = title.text if title else ""
    description = soup.find("meta", property="og:description")
    description = description["content"] if description else ""
    url = soup.find("meta", property="og:url")
    url = url["content"] if url else ""
    keywords_list = get_page_keywords(soup)
    webpage_schema = {
        "@type": "WebPage",
        "url": str(url),
        "name": str(title),
        "description": str(page_h1.replace("\n", " ")) + ", " + str(description),
        "keywords": keywords_list
        }
    return webpage_schema

def print_schema(schema):
    print(json.dumps(schema,sort_keys=False, indent=4))



@click.command()
@click.option('-v', default=False, help='is verbose schema')
@click.argument('url')
def run(v,url):
    """Simple program that greets NAME for a total of COUNT times."""
    click.echo(f"Initializing scrape of: {url}")
    soup = get_soup()
    schema["@graph"].append(get_webpage_schema(soup))
    print_schema(schema)

if __name__ == '__main__':
    run()