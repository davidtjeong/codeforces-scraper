import json
import codeforces_wrapper

PROBLEM_LINK = 'https://codeforces.com/problemset/problem/'

if __name__ == "__main__":
    problem_id = '900/A'
    editorial = codeforces_wrapper.get_editorial_link(PROBLEM_LINK + problem_id)
    parsed_statements = codeforces_wrapper.scrape_editorial(editorial)

    # Save to a JSON file
    with open('../problem_statements.json', 'w') as json_file:
        json.dump(parsed_statements, json_file, indent=4)