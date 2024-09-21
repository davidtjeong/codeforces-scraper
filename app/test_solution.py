import requests
import bs4
from requests_html import HTMLSession
import asyncio
from playwright.sync_api import sync_playwright, Playwright
from playwright.async_api import async_playwright
import re
import time

cookies = [
    {
        'name': 'JSESSIONID',
        'value': '429175945B3AC5E819AF50DAC1BF34BD',
        'domain': 'codeforces.com',
        'path': '/',
        'httpOnly': True,
        'secure': True,
        'sameSite': 'Lax',
    },
    {
        'name': '39ce7',
        'value': 'CFIBzbOU',
        'domain': 'codeforces.com',
        'path': '/',
        'httpOnly': True,
        'secure': True,
        'sameSite': 'Lax',
    }
]

async def get_solution_ids(contest, letter, language):
    print(language)

    url = f'http://codeforces.com/problemset/status/{str(contest)}/problem/{letter}'

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        await context.add_cookies(cookies)
        page = await context.new_page()

        await page.goto(url)
        await page.wait_for_timeout(100)
        html_content = await page.content()

        m = re.search(r'meta name="X-Csrf-Token" content="(.*)"', html_content)
        if not m:
            raise Exception('Unable to get CSRF token')

        csrf_token = m.group(1)
        print(csrf_token)

        # Perform POST request based on language
        if language == 'python':
            print("python_search")
            new_context = await browser.new_context()
            await new_context.add_cookies(cookies)

            request_context = new_context.request
            response = await request_context.post(
                url,
                data={'csrf_token': csrf_token, 
                    'action': 'setupSubmissionFilter', 
                    'frameProblemIndex': 'A', 
                    'verdictName': 'OK', 
                    'programTypeForInvoker': 'python.2', 
                    'comparisonType': 'NOT_USED', 
                    'judgedTestCount': '', 
                    '_tta': '199'},
                headers={'X-Csrf-Token': csrf_token}
            )
            # await page.wait_for_timeout(10000)
            # html_content = await response.text()
            # print(html_content)
            
        else:
            print("Here")
            await browser.close()
            return []
        
        await page.close()
        await context.add_cookies(cookies)
        page = await context.new_page()

        # Navigate to the page after post request
        await page.goto(url)
        await page.wait_for_timeout(5000)
        html_content = await page.content()

        # if language == 'python':
        #     print("python_search")
        #     response = await context.request.post(
        #         url,
        #         data={'csrf_token': csrf_token, 'action': 'setupSubmissionFilter', 'frameProblemIndex': 'A', 'verdictName': 'OK', 'programTypeForInvoker': 'python.3', 'comparisonType': 'NOT_USED', 'judgedTestCount': '', '_tta': '199'},
        #         headers={'X-Csrf-Token': csrf_token}
        #     )
        # else:
        #     print("Here")
        #     await browser.close()
        #     return []
    
        # await page.goto(url, wait_until='networkidle')
        # html_content = await page.content()
        #print(html_content)

        soup = bs4.BeautifulSoup(html_content, "html.parser")
        #print(soup)

        messages = []

        # Extract solution IDs
        text = soup.select("tr")

        for row in text:
            raw = str(row)
            body = re.search(r'data-submission-id="(.*)" t', raw)
            if body is not None:
                w = body.group(1)
                messages.append(w)

        await browser.close()
        print(messages)
        return messages

# asyncio.run(get_solution_ids(805, 'B', "python"))

    # # Extract CSRF token
    # m = re.search(r'meta name="X-Csrf-Token" content="(.*)"', c.text)
    # if not m:
    #     raise Exception('Unable to get CSRF token')

    # csrf_token = m.group(1)

    # if language == 'python':
    #     print("python_search")
    #     # Perform POST request for Python
    #     c = requests.post(url,
    #                       data={'csrf_token': csrf_token, 'action': 'setupSubmissionFilter', 'frameProblemIndex': 'A', 'verdictName': 'OK', 'programTypeForInvoker': 'python.2', 'comparisonType': 'NOT_USED', 'judgedTestCount': '', '_tta': '199'},
    #                       headers={'X-Csrf-Token': csrf_token},
    #                       cookies=d)
    # elif language == 'c++':
    #     print("c++_search")
    #     # Perform POST request for C++
    #     c = requests.post(url,
    #                       data={'csrf_token': csrf_token, 'action': 'setupSubmissionFilter', 'frameProblemIndex': 'A', 'verdictName': 'OK', 'programTypeForInvoker': 'cpp.g++', 'comparisonType': 'NOT_USED', 'judgedTestCount': '', '_tta': '199'},
    #                       headers={'X-Csrf-Token': csrf_token},
    #                       cookies=d)
    # else:
    #     return []

    # # Retrieve the updated page content
    # page = requests.get(url, cookies=d)
    # while page.status_code == 503:
    #     time.sleep(1)
    #     page = requests.get(url, cookies=d)
    
    # html_content = page.text

    # # Parse HTML content with BeautifulSoup
    # soup = bs4.BeautifulSoup(html_content, "html.parser")

    # messages = []

    # # Extract solution IDs
    # text = soup.select("body a")

    # for row in text:
    #     raw = str(row)
    #     body = re.search(r'submissionid="(.*)" t', raw)
    #     if body is not None:
    #         w = body.group(1)
    #         messages.append(w)

    # return messages
          

async def scrape_from_submission(contest, submission_id):

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        await context.add_cookies(cookies)

        page = await context.new_page()
        await page.goto(f"https://codeforces.com/contest/{str(contest)}/submission/{str(submission_id)}")

        # await page.wait_for_timeout(500)
        html_content = await page.content()

        soup = bs4.BeautifulSoup(html_content, "html.parser")
        text = soup.select("body > div > div > div > div > pre")

        if text:
            pre_element = text[0]
            code_lines = []

            for li in pre_element.find_all('li'):
                line = ''.join(span.get_text() for span in li.find_all('span'))
                code_lines.append(line)

            formatted_code = '\\n'.join(code_lines)

            print(formatted_code)
        else:
            print("No matching elements found in the HTML.")

        await browser.close()

# https://codeforces.com/contest/805/submission/279026244
asyncio.run(scrape_from_submission(805, 279026244))




































# def run(playwright: Playwright):
#     # Emulate user as desktop
#     device = playwright.devices['Desktop Chrome']
#     browser = playwright.webkit.launch(headless=False)

#     context = browser.new_context(**device)
#     page = context.new_page()

#     return page, browser

# def get_solution(contest, solution_id):
#     url = 'http://codeforces.com/contest/' + str(contest[0]) + '/submission/' + str(solution_id)
#     # http://codeforces.com/contest/700/submission/162326194
#     print(url)

#     page = requests.get(url)
#     with sync_playwright() as p:

#         page, browser = run(p)
#         page = browser.new_page()

#         response = page.goto(url)
#         time.sleep(1)
        
#         html_content = page.content()
#         with open("submission.html", "w") as file:
#             file.write(html_content)

#         soup = bs4.BeautifulSoup(html_content, "html.parser")
#         text = soup.select("body > div > div > div > div > pre")

#         failed_to_download = None
#         solution = None

#         if len(text)==0:
#             print("Here")
#             failed_to_download = solution_id
#         else:
#             body = bs4.BeautifulSoup(str(text[0]), "html.parser").get_text()

#             body = body.replace("\\","\\\\")
#             solution = body.encode('utf-8').decode('string-escape')
#             print(solution)
#         return solution_id, solution, failed_to_download

# get_solution([700], 162326194)