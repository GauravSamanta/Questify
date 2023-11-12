from flask import Flask,render_template,request
import requests
import re
from bs4 import BeautifulSoup
from transformers import pipeline

app = Flask(__name__)


# function to find all acuurance of see also
def find_all(a_str, sub):
    start = 0
    while True:
        start = a_str.find(sub, start)
        if start == -1: return
        yield start
        start += len(sub) # use start += 1 to find overlapping matches

def FindAnswer(url, question):
    url = url
    question = question

    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    content_div = soup.find("div", {"class": "mw-parser-output"})

    for tag in content_div.find_all(["sup", "a", "img"]):
        tag.decompose()

    content = content_div.get_text()

    # Remove special characters, extra whitespace, and blank lines from the text
    cleaned_text = re.sub(r'[^\w\s]', '', content).strip()
    cleaned_text = re.sub(r'\n{2,}', '\n', cleaned_text)

    positions = list(find_all(cleaned_text, 'See also'))

    f_max = max(positions)   # what if empty
    positions.remove(f_max)

    #s_max = max(positions)

    text = cleaned_text[:f_max-1]

    print(text)

    question_answerer = pipeline("question-answering")

    answer=question_answerer(question=question,context=text)
    
    return answer

@app.route("/")
def hello():
    #return "hello world"
    return render_template("input.html")


@app.route('/', methods = ['POST'])
def getvalues():
    url = request.form['url']
    #print(url)
    question = request.form['question']
    #print(question)

    answer = FindAnswer(url,question)

    ans = answer['answer']
    print(answer)
    print(type(answer))
    print(type(ans))
    return render_template('output.html', url = url, question = question, answer = ans )

app.run(debug = True)