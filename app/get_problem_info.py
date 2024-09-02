import json
import codeforces_wrapper

PROBLEM_LINK = 'https://codeforces.com/problemset/problem/'

def fetch_data(problem_num, letter):
    problem_id = str(problem_num) + '/' + letter
    print(PROBLEM_LINK + problem_id)
    response = codeforces_wrapper.parse_problem(PROBLEM_LINK + problem_id)
    return response

def collect_data(start_num, end_num):
    letters = ['A', 'B', 'C', 'D', 'E', 'F']

    all_data = {}
    for num in range(start_num, end_num + 1):
        for letter in letters:
            site_id = str(num) + letter
            try:
                data = fetch_data(num, letter)
                all_data[site_id] = data
            except Exception as e:
                continue
                # print(f"Error fetching data for id {num}: {e}")
    return all_data

def save_data_to_file(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    start_id = 900
    end_id = 905
    filename = '../problem_descriptions.json'
    
    all_data = collect_data(start_id, end_id)
    save_data_to_file(all_data, filename)
