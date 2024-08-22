import bs4
from requests_html import HTMLSession
from playwright.sync_api import sync_playwright, Playwright
import re

def parse_problem(problem_link):
    session = HTMLSession()
    markup = session.get(problem_link).text
    soup = bs4.BeautifulSoup(markup, "html.parser")
    problem = {
        "name": soup.find('div', 'title').string,
        "time_limit": split_limit(soup.find('div', 'time-limit').contents[1].string),
        "mem_limit": split_limit(soup.find('div', 'memory-limit').contents[1].string),
        "description": get_description(soup),
        "inputSpecification": get_content(soup, 'input-specification'),
        "outputSpecification": get_content(soup, 'output-specification'),
        "public_tests": get_sample_tests(soup),
        "note": get_content(soup, 'note'),
        "tags": get_tags(soup),
    }
    return problem


def get_editorial_link(problem_link):
    session = HTMLSession()
    markup = session.get(problem_link).text
    soup = bs4.BeautifulSoup(markup, "html.parser")

    links = soup.find_all('a')
    tutorial_link = None
    for link in links:
        if 'Tutorial' in link.get_text():
            tutorial_link = link.get('href')
            if not tutorial_link.startswith("/blog/entry"):
                tutorial_link = None
                continue
            if "codeforces" not in tutorial_link:
                tutorial_link = "https://codeforces.com" + tutorial_link
            break
    
    return tutorial_link if tutorial_link else None
    

def split_limit(soup):
    l = soup.split()
    return {
        "value": int(l[0]),
        "unit": l[1]
    }

def group_tests(lst):
    """returns a list of list({input, output})"""
    return [{"input": _in, "output": _out} for _in, _out in pairwise(lst)]


def get_sample_tests(souped_html):
    return group_tests(get_tags_contents(souped_html, 'pre'))


def get_tags_contents(souped_html, tag_name, class_name=None):
    """This function returns all the tags contents in a souped html"""
    return [concat_contents(tag.contents) for tag in souped_html.find_all(tag_name, class_name)]


def pairwise(iterable):
    a = iter(iterable)
    return zip(a, a)


def get_description(soup):
    return concat_contents(soup.find('div', 'header').next_sibling.contents)


def get_content(soup, _class=''):
    element = soup.find('div', _class)
    if not element:
        return None
    tags = element.contents
    tags.pop(0)
    return concat_contents(tags)


def get_tags(soup):
    soup_body = soup.body.find(id="body")
    if not soup_body:
        return "Did not find soup_body"
    
    sidebar = soup_body.find(id="sidebar")
    if not sidebar:
        return "Did not find sidebar"
    
    tag_boxes = sidebar.find_all('span', class_='tag-box')
    if not tag_boxes:
        return "Did not find tag_boxes"

    tags = [tag.get_text(strip=True) for tag in tag_boxes]
    return tags

def process_string(input_string):

    cleaned = re.sub(r'<.*?>', '', input_string)
    cleaned = cleaned.encode('ascii', 'ignore').decode('ascii')
    cleaned = cleaned.replace('$$$', '')
    return cleaned

def convert_mathjax_to_latex(html_content):
    latex = re.sub(
        r'<math.*?>.*?<mi>(.*?)</mi>.*?<mi>(.*?)</mi>.*?<mo>(.*?)</mo>.*?</math>',
        r'\\gcd(\1, \2)',
        html_content,
        flags=re.DOTALL
    )
    
    latex = re.sub(
        r'<math.*?>.*?<mi>(.*?)</mi>.*?<mo>(.*?)</mo>.*?<mi>(.*?)</mi>.*?</math>',
        r'$$\2$$',
        latex,
        flags=re.DOTALL
    )
    return latex


def concat_contents(ls):\

    concat = ''.join([str(i) for i in ls])
    return process_string(concat)