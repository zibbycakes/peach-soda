from flask import Flask
from flask import request
import psycopg2
from config import config
import json
from datetime import datetime
from pytz import timezone

app = Flask(__name__)

params = config()
print('connecting to the postgres db...')
conn = psycopg2.connect(**params)

cur = conn.cursor()

tz = timezone('America/Chicago')

@app.route('/suggestions', methods=['GET', 'POST'])
def suggestion():
    if request.method == 'GET':
        return get_suggestions()
    else:
        req_data = request.get_json()
        if 'suggestion' in req_data:
            return post_suggestions(req_data['suggestion'])

def get_suggestions():
    try:
        response = {}
        cur.execute('select * from music_suggestions')
        rows = cur.fetchall()
        suggestions = []
        for row in rows:
            
            formatted_date_added = datetime.strftime(row[2], '%a, %d %b %Y %H:%M:%S') + ' CST' if row[2] else None
            formatted_date_used = datetime.strftime(row[3], '%a, %d %b %Y %H:%M:%S') + ' CST' if row[3] else None
            response_obj = {
                'id': row[0],
                'suggestion': row[1],
                'date_added': formatted_date_added,
                'date_used': formatted_date_used,
                'used': row[4]
            }
            suggestions.append(response_obj)
        response['suggestions'] = suggestions
        return response
    except Exception as e:
        print(e)
        return {'error': 'failed to fetch all suggestions'}

def post_suggestions(suggestion_text):
    try:
        now_string = datetime.datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S %Z')
        cur.execute("insert into music_suggestions (suggestion, date_added) values('" + suggestion_text + "','" + now_string + "')")
        conn.commit()
        return {'success': 'successfully added "' + suggestion_text + '" to the database at time ' + now_string + '.'}
    except Exception as e:
        print(e)
        return {'error': 'adding "' + suggestion_text + '" to the database was unsuccessful.'}

@app.route('/suggestions/<suggestion_id>')
def get_suggestion(suggestion_id):
    try:
        cur.execute('select * from music_suggestions where id='+suggestion_id)
        row = cur.fetchone()
        response = {
            'id': row[0],
            'suggestion': row[1],
            'date_added': row[2],
            'date_used': row[3],
            'used': row[4]
        }
        return response
    except Exception as e:
        print(e)
        return {'error': 'failed to fetch id ' +suggestion_id}

@app.route('/suggestions/<suggestion_id>/use', methods=['PUT'])
def set_suggestion_to_used(suggestion_id):
    try:
        now_string = datetime.datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S %Z')
        cur.execute("update music_suggestions set date_used='"+ now_string +"', used=true where id="+suggestion_id)
        conn.commit()
        return {'success': 'successfully set id ' + suggestion_id + ' to used at time ' + now_string +'.'}
    except Exception as e:
        print(e)
        return {'error': 'setting "' + suggestion_id + '" to used was unsuccessful.'}