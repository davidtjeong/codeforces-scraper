import json
import codeforces_wrapper
import asyncio
from playwright.sync_api import sync_playwright, Playwright
from playwright.async_api import async_playwright

PROBLEM_LINK = 'https://codeforces.com/problemset/problem/'

async def fetch_problem_data(problem_num, letter):
    problem_id = f"{problem_num}/{letter}"
    print(PROBLEM_LINK + problem_id)
    response = await codeforces_wrapper.parse_problem(PROBLEM_LINK + problem_id)
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


async def parse_editorial(page, contest, target_index):
    page_content = await page.evaluate('''({ contest, targetIndex }) => {
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


async def run(playwright: Playwright):
    device = playwright.devices['Desktop Chrome']
    browser = await playwright.chromium.launch(headless=True)

    context = await browser.new_context(**device)
    page = await context.new_page()
    return page, browser

lettersDict = {
    0 : 'A',
    1 : 'B',
    2 : 'C',
    3 : 'D',
    4 : 'E',
    5 : 'F'
}

async def collect_data(start_num, end_num):
    all_data = {}

    async with async_playwright() as p:
        page, browser = await run(p)
        device = p.devices['Desktop Chrome']
        context = await browser.new_context(**device)

        for num in range(start_num, end_num + 1):
            editorial_link = None

            # Fetch the editorial link once per problem ID
            if editorial_link is None:
                try:
                    editorial_link = await codeforces_wrapper.get_editorial_link(PROBLEM_LINK + str(num) + '/A')
                    if not editorial_link:
                        print(f"No editorial link found for problem {num}")
                except Exception as e:
                    print(f"Error fetching editorial link for problem {num}: {e}")
                    editorial_link = None

            # If editorial link is available, fetch content for each problem under this ID
            for letterIdx in range(6):
                letter = lettersDict[letterIdx]
                site_id = str(num) + letter
                problem_data = {}

                try:
                    # Fetch problem data
                    page = await context.new_page()
                    data = await fetch_problem_data(num, letter)
                    problem_data['problem'] = data

                    # If editorial link is available, parse editorial for the specific problem
                    if editorial_link:
                        try:
                            context = await browser.new_context(**device)
                            page = await context.new_page()

                            await page.goto(editorial_link)
                            await page.wait_for_timeout(100)
                            # markup = await page.content()  # Get the full HTML of the page
                            # print(markup)
                            # Parse editorial for the specific problem (e.g., 900A, 900B)
                            editorial_content = await parse_editorial(page, num, letterIdx)

                            problem_data['editorial'] = editorial_content
                        except Exception as e:
                            print(f"Error parsing editorial for problem {site_id}: {e}")
                            problem_data['editorial'] = "No editorial available"
                        finally:
                            await page.close()
                    else:
                        problem_data['editorial'] = "No editorial available"
                        await page.close()

                    all_data[site_id] = problem_data
                except Exception as e:
                    print(f"Error fetching data for id {site_id}: {e}")
                    await page.close()
                    continue

        await browser.close()

    return all_data



def save_data_to_file(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    start_id = 2000
    end_id = 2000
    filename = '../compiled_problems.json'

    async def main():
        all_data = await collect_data(start_id, end_id)
        save_data_to_file(all_data, filename)

    # Run the asynchronous main function
    asyncio.run(main())

# if __name__ == "__main__":
#     start_id = 900
#     end_id = 901
#     filename = '../compiled_problems.json'
    
#     all_data = await collect_data(start_id, end_id)
#     save_data_to_file(all_data, filename)
