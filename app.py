#!flask/bin/python
from flask import Flask, jsonify
from flask import abort
import numpy as np
import string
import nltk
import re
from joblib import dump, load

from sklearn.neighbors import KNeighborsClassifier
app = Flask(__name__)

def preprocess(text):
    pattern = re.compile('[\W_]+')
    lowercase = text.lower()
    lowercase = lowercase.replace('\\n', ' ')
    lowercase = pattern.sub(' ', lowercase)
    lcp = "".join([char for char in lowercase if char not in string.punctuation])
    words = nltk.tokenize.word_tokenize(lcp)
    words = [word for word in words if word not in nltk.corpus.stopwords.words('english')]
    words_text = [word for word in words if len(word) <= 15 and len(word)>=3]
    txt = " ".join(words)
    return txt
    
def read_glove_vecs(glove_file):
    with open(glove_file, 'r', encoding="utf8") as f:
        word_to_vec_map = {}
        for line in f:
            line = line.strip().split()
            curr_word = line[0]
            #if curr_word in words_text:
            word_to_vec_map[curr_word] = np.array(line[1:], dtype=np.float64)
    return word_to_vec_map

def sentence_to_avg(sentence, word_to_vec_map):
    words = sentence.split()
    if len(words) == 0: return np.zeros(300)
    avg = np.zeros(300)
    total = 0
    for w in words:
        if w in word_to_vec_map:
            total += word_to_vec_map[w]
    avg = total / len(words)
    return avg

from flask import abort
@app.route('/todo/api/v1.0/tasks/<string:text>', methods=['GET'])
def get_task(text):
    text = preprocess(text)
    glove = sentence_to_avg(text, word_to_vec_map)
    if type(glove) == float: glove = np.zeros((300,))
    y_pred = clf.predict([glove])
    rating = {'rating': int(y_pred[0])}
    return jsonify(rating)

from flask import make_response
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify({'error': 'Bad Request'}), 400)

from flask import request
@app.route('/todo/api/v1.0/tasks', methods=['POST'])
def create_task():
    if not request.json or not 'text' in request.json:
        abort(400)
    text = request.json['text']
    text = preprocess(text)
    glove = sentence_to_avg(text, word_to_vec_map)
    if type(glove) == float: glove = np.zeros((300,))
    y_pred = clf.predict([glove])
    rating = {'rating': int(y_pred[0])}
    return jsonify(rating), 201

@app.route('/todo/api/v1.0/tasks', methods=['GET'])
def get_tasks():
    if not request.args or not 'text' in request.args:
        abort(400)
    text = request.args.get('text')
    text = preprocess(text)
    glove = sentence_to_avg(text, word_to_vec_map)
    if type(glove) == float: glove = np.zeros((300,))
    y_pred = clf.predict([glove])
    rating = {'rating': int(y_pred[0])}
    return jsonify(rating)

if __name__ == '__main__':
    nltk.download('punkt')
    nltk.download('stopwords')
    clf = load('mlp.joblib')
    print("READING GLOVE FILE, COULD TAKE SEVERAL MINUTES...", flush=True)
    word_to_vec_map = read_glove_vecs('../data/glove.42B.300d.txt')
    #word_to_vec_map = {}
    print("GLOVE FILE READING DONE!", flush=True)
    app.run(debug=True)
    