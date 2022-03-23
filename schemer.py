import click
from bs4 import BeautifulSoup
from selenium import webdriver
import json 

schema = {
    "@context": "https://schema.org/",
    "@graph": []
}

def get_soup():
    print("hello")
    driver = webdriver.Chrome('../../Downloads/chromedriver_win32/chromedriver')
    driver.get('https://www.pixelz.com')
    results = []
    content = driver.page_source
    
    soup = BeautifulSoup(content, features="lxml")
    return soup 
    
def get_webpage_schema(soup):
    results = []
    for element in soup.findAll("h1"):
        results.append(element.text)
    page_name = results[0]
    webpage_schema = {
        "@type": "WebPage",
        "name": page_name}
    return webpage_schema

def print_schema(schema):
    print(json.dumps(schema,sort_keys=False, indent=4))



@click.command()
@click.option('-v', default=False, help='is verbose schema')
@click.argument('url')
def run(v,url):
    """Simple program that greets NAME for a total of COUNT times."""
    click.echo(f"{url}")
    soup = get_soup()
    schema["@graph"].append(get_webpage_schema(soup))
    print_schema(schema)

if __name__ == '__main__':
    run()