import json
import codeforces_wrapper
from playwright.sync_api import sync_playwright, Playwright

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

def parse_page(page, contest):
    # Pass the contest number as a parameter to the page.evaluate function
    page_content = page.evaluate(f'''(contest) => {{
        function convertMathJaxToLaTeX(element) {{
            let latex = element.innerHTML
                .replace(/<math.*?>.*?<mi>(.*?)<\/mi>.*?<mi>(.*?)<\/mi>.*?<mo>(.*?)<\/mo>.*?<\/math>/g, '\\\\gcd($1, $2)')
                .replace(/<math.*?>.*?<mi>(.*?)<\/mi>.*?<mo>(.*?)<\/mo>.*?<mi>(.*?)<\/mi>.*?<\/math>/g, '$$\\\\$2$$');
            return latex;
        }}

        var problemStatements = document.querySelectorAll('.problem-statement');

        var parsedStatements = [];
        
        // Generate the letter suffixes
        function getLetterSuffix(index) {{
            const letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
            return letters[index % letters.length];
        }}

        problemStatements.forEach(function(problemStatement, index) {{
            var clone = problemStatement.cloneNode(true);

            var mathJaxElements = clone.querySelectorAll('.MathJax');
            mathJaxElements.forEach(mathElement => {{
                let latex = convertMathJaxToLaTeX(mathElement);
                mathElement.outerHTML = latex;
            }});

            var text = clone.innerText.trim();

            parsedStatements.push({{
                index: contest + getLetterSuffix(index),
                text: text
            }});
        }});

        return parsedStatements;
    }}''', contest)
    return page_content

def save_json(content, filename):
    with open(filename, 'w') as f:
        json.dump(content, f, indent=4)

def run(playwright: Playwright):
    # Emulate user as desktop
    device = playwright.devices['Desktop Chrome']
    browser = playwright.webkit.launch(headless=False)

    context = browser.new_context(**device)
    page = context.new_page()

    return page, browser

# Get list of all editorial links for each contest
def collect_editoral_links(start_num, end_num):

    PROBLEM_LINK = 'https://codeforces.com/problemset/problem/'

    editorial_links = {}
    for num in range(start_num, end_num + 1):
        problem_found = False
        for suffix in ['A', 'B', 'C']:  # Try A, B, then C
            site_id = f"{num}/{suffix}" 

            try:
                problem = PROBLEM_LINK + site_id
                editorial = codeforces_wrapper.get_editorial_link(problem)
                if editorial: 
                    editorial_links[num] = editorial
                    print(f"Editorial found for: {num}{suffix}")
                    problem_found = True
                    break

            except Exception as e:
                print(f"Error fetching data for id {num}{suffix}: {e}")
            
        if not problem_found:
            print(f"No editorial found for any problem in contest {num}")

    return editorial_links


def main():
    
    urls = collect_editoral_links(800, 805)
    print(urls)

    with sync_playwright() as p:
        page, browser = run(p)

        all_parsed_statements = []
        for contest, url in urls.items():
            page = browser.new_page()
            print(url)
            page.goto(url)
            page.wait_for_timeout(100)
            parsed_statements = parse_page(page, contest)
            all_parsed_statements.extend(parsed_statements)
            page.close()

        print(all_parsed_statements)
        save_json(all_parsed_statements, '../editorials.json')

        browser.close()

if __name__ == '__main__':
    main()
