from playwright.sync_api import sync_playwright
import os
import re
import shutil
from bs4 import BeautifulSoup
import time
import concurrent.futures

def sub_strip(matchobj):   
    return matchobj.group(0).replace(u"\u2009", "")

def get_problem_list(url, page):
    page.goto(url)
    html_content = page.content()
    soup = BeautifulSoup(html_content, "html.parser")

    messages = []

    text = soup.select("body a")

    for row in text:
        raw = str(row)
        body = re.search(' href="/problemset/problem/(.*)">', raw)

        if body is not None:
            w = body.group(1)
            c = w.split('/')
            messages.append(c)

    return messages

def get_solution_ids(name, language, page):
    print(f"Fetching solution IDs for problem {name} in {language}")

    url = f'https://codeforces.com/problemset/status/{name[0]}/problem/{name[1]}'
    print(f"Fetching page for URL: {url}")

    page.goto(url)

    # Wait for CSRF token to be attached in the DOM instead of visible
    page.wait_for_selector("meta[name='X-Csrf-Token']", state="attached")

    # Get the CSRF token
    csrf_token = page.get_attribute("meta[name='X-Csrf-Token']", "content")
    if not csrf_token:
        raise RuntimeError('Unable to get CSRF token')

    print(f"CSRF Token: {csrf_token}")

    # Define data based on language
    program_type = 'python.2' if language == 'python' else 'cpp.g++'
    data = {
        'csrf_token': csrf_token,
        'action': 'setupSubmissionFilter',
        'frameProblemIndex': 'A',
        'verdictName': 'OK',
        'programTypeForInvoker': program_type,
        'comparisonType': 'NOT_USED',
        'judgedTestCount': '',
        '_tta': '199'
    }

    # Use Playwright to send a POST request from the browser context
    print("Sending POST request to filter solutions")
    page.evaluate(f'''
        fetch('{url}', {{
            method: 'POST',
            headers: {{
                'X-Csrf-Token': '{csrf_token}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }},
            body: new URLSearchParams({data}).toString()
        }})
    ''')

    # Wait for the results to load after filtering
    page.wait_for_selector("body")
    print("Page loaded, extracting solution IDs")

    html_content = page.content()
    soup = BeautifulSoup(html_content, "html.parser")

    messages = []
    text = soup.select("body a")

    for row in text:
        raw = str(row)
        body = re.search('submissionid="(.*)" t', raw)
        if body is not None:
            w = body.group(1)
            messages.append(w)

    print(f"Found {len(messages)} solution IDs")
    return messages

def get_solution(contest, solution_id, page):
    url = f'https://codeforces.com/contest/{contest[0]}/submission/{solution_id}'

    page.goto(url)

    # Wait until the page loads the content
    page.wait_for_selector("body > div > div > div > div > pre")

    html_content = page.content()
    soup = BeautifulSoup(html_content, "html.parser")

    text = soup.select("body > div > div > div > div > pre")

    failed_to_download = None
    solution = None

    if len(text) == 0:
        failed_to_download = solution_id
    else:
        body = BeautifulSoup(str(text[0]), "html.parser").get_text()
        body = body.replace("\\", "\\\\")
        solution = body.encode('utf-8').decode('unicode_escape')

    return solution_id, solution, failed_to_download

def get_solutions(contest, solution_ids, page):
    solutions = {}
    if not solution_ids:
        print("No solution IDs found.")
        return solutions

    for solution_id in solution_ids:
        solution_data = get_solution(contest, solution_id, page)
        if solution_data[2] is None:  # If not failed to download
            solutions[solution_data[0]] = solution_data[1]
        else:
            print(f"Failed to download solution {solution_id}")

    print(f"Collected {len(solutions)} solutions")
    return solutions

def download_all_challenge_names(filename, page):
    target = open(filename, 'w')

    problem_list = []

    for i in range(0, 30):
        a = f'https://codeforces.com/problemset/page/{i+1}'
        l = get_problem_list(a, page)
        for jdx, j in enumerate(l):
            if jdx % 2 == 0:
                problem_list.append(j)
    target.write(str(problem_list))
    target.close()

def download_descriptions_solutions(filename, index_n, page):
    root_dir = 'codeforces_data'

    with open(filename, 'r') as f:
        all_names = eval(f.read())

    # Example language array, adjust as needed
    language = ["python", "c++"]

    for idx, i in enumerate(all_names):
        print(f"Processing problem {i}")

        save_dir = os.path.join(root_dir, f"{i[0]}_{i[1]}")
        os.makedirs(save_dir, exist_ok=True)

        ids_l = []
        for l in language:
            print(f"Fetching solutions for language: {l}")
            ids = get_solution_ids(i, l, page)
            ids_l.append(ids)

            solutions = get_solutions(i, ids, page)
            if not solutions:
                print(f"No solutions found for problem {i} in language {l}")
                continue

            solution_dir = os.path.join(save_dir, f"solutions_{l}")
            os.makedirs(solution_dir, exist_ok=True)

            for jdx, j in enumerate(solutions):
                if len(solutions[j]) < 10000:
                    solution_file_path = os.path.join(solution_dir, f"{j}.txt")
                    with open(solution_file_path, 'w') as solution_file:
                        solution_file.write(solutions[j])
                    print(f"Solution saved to {solution_file_path}")
                else:
                    print(f"Skipping large solution {j} with size {len(solutions[j])}")

        # Remove problems with zero solutions
        if len(ids_l[0]) == 0 and len(ids_l[1]) == 0:
            print(f"Removing directory {save_dir} due to no solutions")
            shutil.rmtree(save_dir)

if __name__ == "__main__":
    index_n = 0
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Use headless=True if you don't want to see the browser
        context = browser.new_context()
        page = context.new_page()
        download_descriptions_solutions('challenges_all.txt', index_n, page)
        browser.close()
