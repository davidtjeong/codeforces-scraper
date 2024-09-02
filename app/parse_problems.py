import json
import codeforces_wrapper
from playwright.sync_api import sync_playwright, Playwright

PROBLEM_LINK = 'https://codeforces.com/problemset/problem/'

def fetch_problem_data(problem_num, letter):
    problem_id = f"{problem_num}/{letter}"
    print(PROBLEM_LINK + problem_id)
    response = codeforces_wrapper.parse_problem(PROBLEM_LINK + problem_id)
    return response

def convert_mathjax_to_latex(element):
    latex = element.innerHTML
    latex = latex.replace(
        r'<math.*?>.*?<mi>(.*?)<\/mi>.*?<mi>(.*?)<\/mi>.*?<mo>(.*?)<\/mo>.*?<\/math>',
        r'\\gcd(\1, \2)'
    ).replace(
        r'<math.*?>.*?<mi>(.*?)<\/mi>.*?<mo>(.*?)<\/mo>.*?<mi>(.*?)<\/mi>.*?<\/math>',
        r'$$\\\2$$'
    )
    return latex


def parse_editorial(page, contest, target_index):
    page_content = page.evaluate('''({ contest, targetIndex }) => {
        function convertMathJaxToLaTeX(element) {
            let latex = element.innerHTML
                .replace(/<math.*?>.*?<mi>(.*?)<\/mi>.*?<mi>(.*?)<\/mi>.*?<mo>(.*?)<\/mo>.*?<\/math>/g, '\\\\gcd($1, $2)')
                .replace(/<math.*?>.*?<mi>(.*?)<\/mi>.*?<mo>(.*?)<\/mo>.*?<mi>(.*?)<\/mi>.*?<\/math>/g, '$$\\\\$2$$');
            return latex;
        }

        var problemStatements = document.querySelectorAll('.problem-statement');

        if (targetIndex < 0 || targetIndex >= problemStatements.length) {
            return null;  // Return null if the target index is out of bounds
        }

        var problemStatement = problemStatements[targetIndex];
        var clone = problemStatement.cloneNode(true);

        var mathJaxElements = clone.querySelectorAll('.MathJax');
        mathJaxElements.forEach(mathElement => {
            let latex = convertMathJaxToLaTeX(mathElement);
            mathElement.outerHTML = latex;
        });

        var text = clone.innerText.trim();

        // Generate the letter suffix
        function getLetterSuffix(index) {
            const letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
            return letters[index % letters.length];
        }

        return text;
    }''', { 'contest': contest, 'targetIndex': target_index })

    return page_content


def run(playwright: Playwright):
    device = playwright.devices['Desktop Chrome']
    browser = playwright.webkit.launch(headless=False)
    context = browser.new_context(**device)
    page = context.new_page()
    return page, browser

lettersDict = {
    0 : 'A',
    1 : 'B',
    2 : 'C',
    3 : 'D',
    4 : 'E',
    5 : 'F'
}

def collect_data(start_num, end_num):
    all_data = {}

    with sync_playwright() as p:
        page, browser = run(p)

        for num in range(start_num, end_num + 1):
            for letterIdx in range(6):
                letter = lettersDict[letterIdx]
                site_id = str(num) + letter
                problem_data = {}
                try:
                    page = browser.new_page()
                    # Fetch problem data
                    data = fetch_problem_data(num, letter)
                    problem_data['problem'] = data

                    # Fetch editorial link
                    editorial_link = codeforces_wrapper.get_editorial_link(PROBLEM_LINK + str(num) + '/' + letter)
                    if editorial_link:
                        page.goto(editorial_link)
                        page.wait_for_timeout(100)
                        editorial_content = parse_editorial(page, num, letterIdx)
                        problem_data['editorial'] = editorial_content

                    page.close()
                    all_data[site_id] = problem_data
                except Exception as e:
                    print(f"Error fetching data for id {site_id}: {e}")
                    page.close()
                    continue

        browser.close()

    return all_data

def save_data_to_file(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    start_id = 900
    end_id = 905
    filename = '../compiled_problems.json'
    
    all_data = collect_data(start_id, end_id)
    save_data_to_file(all_data, filename)
