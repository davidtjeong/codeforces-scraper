# CodeForces Problem Scraper API

A straightforward Flask-Python API designed to parse Codeforces problems into JSON format.

## Endpoint

Make a **GET** request to the root `/?id=1325/A` and provide the required query parameter `id`. The `id` should be in the following format `contest_id/problem_letter`.

For example, parsing [this](https://codeforces.com/contest/1325/problem/A) problem yields the following JSON response:

```json
{
  "description": "\u003Cp\u003EYou are given a positive integer $$$x$$$. Find \u003Cspan class=\"tex-font-style-bf\"\u003Eany\u003C/span\u003E such $$$2$$$ positive integers $$$a$$$ and $$$b$$$ such that $$$GCD(a,b)+LCM(a,b)=x$$$.\u003C/p\u003E\u003Cp\u003EAs a reminder, $$$GCD(a,b)$$$ is the greatest integer that divides both $$$a$$$ and $$$b$$$. Similarly, $$$LCM(a,b)$$$ is the smallest integer such that both $$$a$$$ and $$$b$$$ divide it.\u003C/p\u003E\u003Cp\u003EIt's guaranteed that the solution always exists. If there are several such pairs $$$(a, b)$$$, you can output any of them.\u003C/p\u003E",
  "inputSpecification": "\u003Cp\u003EThe first line contains a single integer $$$t$$$ $$$(1 \\le t \\le 100)$$$  — the number of testcases.\u003C/p\u003E\u003Cp\u003EEach testcase consists of one line containing a single integer, $$$x$$$ $$$(2 \\le x \\le 10^9)$$$.\u003C/p\u003E",
  "mem_limit": {
    "unit": "megabytes",
    "value": 256
  },
  "name": "A. EhAb AnD gCd",
  "note": "\u003Cp\u003EIn the first testcase of the sample, $$$GCD(1,1)+LCM(1,1)=1+1=2$$$.\u003C/p\u003E\u003Cp\u003EIn the second testcase of the sample, $$$GCD(6,4)+LCM(6,4)=2+12=14$$$.\u003C/p\u003E",
  "outputSpecification": "\u003Cp\u003EFor each testcase, output a pair of positive integers $$$a$$$ and $$$b$$$ ($$$1 \\le a, b \\le 10^9)$$$ such that $$$GCD(a,b)+LCM(a,b)=x$$$. It's guaranteed that the solution always exists. If there are several such pairs $$$(a, b)$$$, you can output any of them.\u003C/p\u003E",
  "public_tests": [
    {
      "input": "\n2\n2\n14\n",
      "output": "\n1 1\n6 4\n"
    }
  ],
  "tags": [
    "constructive algorithms",
    "greedy",
    "number theory",
    "*800"
  ],
  "time_limit": {
    "unit": "second",
    "value": 1
  }
}
```

## Usage

After cloning the repository, you have two options:

- **Option 1: Docker Installed**
  - Build the image.  
    `docker build -t cf-problem-scraper-api .`
  - Create a container.  
    `docker run -d --name cf-api -p 80:80 cf-problem-scraper-api`
    - The above maps port 80 on your local host to port 80 within the container
  - To make requests go to `http://localhost:80`
    - An example request is `http://localhost/?id=1325/A`


- **Option 2: Python3 Installed**
  - Navigate to the `/app` directory.
  - Install packages in `requirements.txt` using pip3.  
    `pip3 install -r requirements.txt`
  - Start the server.  
    `FLASK_APP=main.py flask run`

## Scrape and Compile Multiple Problems
- Simply navigate to `/app` and run the script with `python compile_problems.py`
  - This will compile all json responses within the provided range of problem ID's into one json file with the shown formats
    


## JSON Schema

```json
{
  "description": String,
  "inputSpecification": String,
  "mem_limit": {
    "unit": String,
    "value": Number
  },
  "name": String,
  "note": String, // or null
  "outputSpecification": String,
  "public_tests": [
    {
      "input": String,
      "output": String
    }
  ],
  "tags": [String],
  "time_limit": {
    "unit": String,
    "value": Number
  }
}
```
