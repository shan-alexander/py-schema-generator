import click
from bs4 import BeautifulSoup
from selenium import webdriver
import json 
import rake #for SEO keyword extraction
from datetime import datetime

schema = {
    "@context": "https://schema.org/",
    "@graph": []
}

def get_videoobject_schema(soup):
    page_h1 = soup.h1.get_text()
    ifr = soup.find_all('iframe', src=lambda x: x and 'player.vimeo' in x)
    print(ifr)
    video_iframe = {}
    for i in ifr:
        if ('src' in i) & ('player.vimeo' in i['src']):
            video_iframe = i
    print(video_iframe)
    #filter the link ending with .mp4
    videoobject_schema = {
        "@type": "VideoObject",
        "inLanguage": "en-US",
        "embedUrl": video_iframe['src'] if video_iframe else "",
        # "transcript": "Pain points were a lot of excel docs, a lot of google docs, a lot of admin, a lot of human error, and not enough speed-to-market and not enough creative time. We no longer have a, let's say, over-deadline product anymore, so now it's more about what we can do with an SLA, which is super fun. Right, like you've got seven days, what can you do in that to enhance brand awareness. Once we deliver to post-production, we know how long it takes, and we work back from that, and we've got all this time now to spend extra time with the brand, create extra images or GIFs or whatever it is, if they want, because we now know how much time we've got based on check-in and check-out, which is the Creative Force part of it. We also have a lot more control, of every process. So if a brand says please shoot ten items, and give me more creative options, I can do that, knowing that I'm not using any time. So I guess it was putting something in place before Pixelz that enhanced the whole process, instead of just putting them at the end, now we can rely on the whole process.",,
        "name": page_h1,
        "description": "Bestseller is a 20+ brand company and their Photo Studio Manager, Kate Davies-Benade, discusses how Pixelz and Creative Force is creating better workflows and improving creativity for Bestseller photo studios.",
        "caption": "Photo: Bestseller's Photo Studio Manager provides a photo editing service review for Pixelz, the world's largest and most advanced retouching service for professional ecommerce studios.",
        "contentLocation": "Bestseller Product Photography Studio",
        "isFamilyFriendly": "True",
        "keywords": [
            "photo editing service reviews",
            "best photo editing services",
            "image retouching reviews",
            "bestseller photo editing review",
            "Creative Force review"
        ],
        "author": "Pixelz",
        "duration": "PT1M10S",
        "datePublished": "2017-01-25",
        "uploadDate": "2017-01-25",
        "thumbnailURL": "https://i.vimeocdn.com/video/885329635-5dcd32ca3920fe93b316c21637014bcc87d0185babfd1b50999df92618cce145-d.jpg"
    }

    return videoobject_schema

def get_imageobject_list_schema(soup, limit):
    imageobject_list = []
    print("Initializing imageobject schema generator...")
    try:
        imgs = soup.findAll('img')
        # print(imgs)
        print("Limit images to: ", limit)
        counter = 0
        for i in imgs:
            print(i)
            if counter >= limit: 
                break
            img = {
                "@type": "ImageObject",
                "inLanguage": "en-US",
                "url": i["data-src"] if "data-src" in i else "",
                # "caption": i["title"] if i["title"] else "",
                # "name": i["title"] if i["title"] else "",
                # "description": i["alt"] if i["alt"] else "",
                "representativeOfPage": True
            }
            imageobject_list.append(img)
            counter = counter + 1
    except:
        print("Did not find suitable images for imageobject schema, or broke trying.")

    return imageobject_list

def get_published_date(soup):
    published_date_string = ""
    try:
        author_element = soup.body.find("p", class_="author")
        published_date_text = author_element.get_text()
        print(published_date_text)
        published_date_text = published_date_text.replace(" | Updated ", "")
        print(published_date_text)
        published_date_text = datetime.strptime(published_date_text, '%b %d, %Y %I:%M %p').strftime('%Y-%m-%d')
        print(published_date_text)
    except:
        print("Could not find a published date")

    return published_date_string

def get_page_keywords(soup):
    keywords = []
    try:
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
        # print(body_string)
        print("-------------")
        keywords = rake_object.run(body_string)
        # remove keyword-phrases less than 2 words
        keywords = [x for x in keywords if len(x[0].split()) > 1]
        keywords = [x[0] for x in keywords]
        # print("HTML Page Keywords:", keywords)
    except:
        print("could not run keyword search")
    
    return keywords

def get_soup(url):
    print("Starting web driver...")
    driver = webdriver.Chrome('../../Downloads/chromedriver_win32/chromedriver')
    driver.get(url)
    content = driver.page_source
    soup = BeautifulSoup(content, features="lxml")
    return soup 
    
def get_webpage_schema(soup):
    print("Initializing WebPage Schema")
    results = []
    h1s = soup.findAll("h1")
    h2s = soup.findAll("h2")
    if len(h1s) > 0:
        for element in h1s:
            results.append(element.text)
    elif len(h2s) > 0:
        for element in h2s:
            results.append(element.text)
    else: 
        results = [""]

    page_h1 = ' '.join(results)
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
        "keywords": keywords_list,
        "datePublished": get_published_date(soup),
        "dateModified": datetime.today().strftime('%Y-%m-%dT%H:%M:%S+00:00'),
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
    soup = get_soup(url)
    schema["@graph"].append(get_webpage_schema(soup))
    schema["@graph"] = schema["@graph"] + get_imageobject_list_schema(soup, 2)
    schema["@graph"].append(get_videoobject_schema(soup))
    print_schema(schema)

if __name__ == '__main__':
    run()