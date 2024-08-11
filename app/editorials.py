import json
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

def parse_page(page):
    # Evaluate the script in the page's context
    page_content = page.evaluate('''() => {
        function convertMathJaxToLaTeX(element) {
            let latex = element.innerHTML
                .replace(/<math.*?>.*?<mi>(.*?)<\/mi>.*?<mi>(.*?)<\/mi>.*?<mo>(.*?)<\/mo>.*?<\/math>/g, '\\gcd($1, $2)')
                .replace(/<math.*?>.*?<mi>(.*?)<\/mi>.*?<mo>(.*?)<\/mo>.*?<mi>(.*?)<\/mi>.*?<\/math>/g, '$$\\$2$$');
            return latex;
        }

        var problemStatements = document.querySelectorAll('.problem-statement');

        var parsedStatements = [];

        problemStatements.forEach(function(problemStatement, index) {
            var clone = problemStatement.cloneNode(true);

            var mathJaxElements = clone.querySelectorAll('.MathJax');
            mathJaxElements.forEach(mathElement => {
                let latex = convertMathJaxToLaTeX(mathElement);
                mathElement.outerHTML = latex;
            });

            var text = clone.innerText.trim();

            parsedStatements.push({
                index: index + 1,
                text: text
            });
        });

        return parsedStatements;
    }''')
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


def main():
    urls = [
        'https://codeforces.com/blog/entry/56294',
    ]

    with sync_playwright() as p:
        page, browser = run(p)

        all_parsed_statements = []
        for i, url in enumerate(urls):
            page.goto(url)
            page.wait_for_timeout(100) # Wait to allow page to run
            parsed_statements = parse_page(page)
            all_parsed_statements.extend(parsed_statements)

            # Optionally, save all statements to a single file
            save_json(all_parsed_statements, '../editorials.json')

            browser.close()

if __name__ == '__main__':
    main()
