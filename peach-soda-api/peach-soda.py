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

@app.route('/')
def ping():
    return {'success': 'Hello world!'}

@app.route('/suggestions', methods=['GET', 'POST'])
def suggestion():
    if request.method == 'GET':
        return get_suggestions()
    else:
        req_data = request.get_json()
        if 'suggestion' in req_data:
            return post_suggestions(req_data['suggestion'], req_data['user_id'])

def get_suggestions():
    try:
        response = {}
        cur.execute('select ms.*, users.first_name from music_suggestions ms inner join users on ms.user_id = users.user_id')
        rows = cur.fetchall()
        suggestions = []
        for row in rows:
            formatted_date_added = datetime.strftime(row[2], '%a, %d %b %Y %H:%M:%S') + ' CST' if row[2] else None
            formatted_date_used = datetime.strftime(row[3], '%a, %d %b %Y %H:%M:%S') + ' CST' if row[3] else None
            response_obj = {
                'sugg_id': row[0],
                'suggestion': row[1],
                'date_added': formatted_date_added,
                'date_used': formatted_date_used,
                'used': row[4],
                'active': row[5],
                'user_id': row[6],
                'first_name': row[7]
            }
            suggestions.append(response_obj)
        response['suggestions'] = suggestions
        return response
    except Exception as e:
        print(e)
        return {'error': 'failed to fetch all suggestions'}

def post_suggestions(suggestion_text, user_id):
    try:
        now_string = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S %Z')
        cur.execute("insert into music_suggestions (suggestion, date_added, user_id) values('" + suggestion_text + "','" + now_string + "','" + str(user_id) + "')")
        conn.commit()
        return {'success': 'successfully added "' + suggestion_text + '" to the database at time ' + now_string + ' for user id ' + str(user_id) + '.'}
    except Exception as e:
        print(e)
        return {'error': 'adding "' + suggestion_text + '" to the database was unsuccessful.'}

@app.route('/suggestions/<suggestion_id>')
def get_suggestion(suggestion_id):
    try:
        cur.execute('select * from music_suggestions where sugg_id='+suggestion_id)
        row = cur.fetchone()
        response = {
            'sugg_id': row[0],
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
        now_string = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S %Z')
        cur.execute("update music_suggestions set date_used='"+ now_string +"', active=false where sugg_id="+suggestion_id)
        conn.commit()
        return {'success': 'successfully set id ' + suggestion_id + ' to used at time ' + now_string +'.'}
    except Exception as e:
        print(e)
        return {'error': 'setting "' + suggestion_id + '" to used was unsuccessful.'}

@app.route('/suggestions/<suggestion_id>/activate', methods=['PUT'])
def set_suggestion_to_active(suggestion_id):
    try:
        now_string = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S %Z')
        cur.execute("update music_suggestions set date_used='"+ now_string +"', used=true, active=true where sugg_id="+suggestion_id)
        conn.commit()
        return {'success': 'successfully set id ' + suggestion_id + ' to active at time ' + now_string +'.'}
    except Exception as e:
        print(e)
        return {'error': 'setting "' + suggestion_id + '" to active was unsuccessful.'}

@app.route('/suggestions/<suggestion_id>/remove', methods=['POST'])
def remove_suggestion(suggestion_id):
    try:
        cur.execute("delete from music_suggestions where sugg_id='" + suggestion_id + "'")
        conn.commit()
        return {'success': 'successfully removed suggestion with id ' + suggestion_id}
    except Exception as e:
        print(e)
        return {'error': 'removing suggestion with id"' + suggestion_id + '" was unsuccessful.'}    

@app.route('/user', methods=['POST'])
def add_user():
    try:
        req_data = request.get_json()
        cur.execute("insert into users (first_name) values ('" + req_data['first_name'] + "')")
        conn.commit()
        return {'success': 'successfully added user with first name ' + req_data['first_name']}
    except Exception as e:
        print(e)
        return {'error': 'adding user with first name "' + req_data['first_name'] + '" was unsuccessful.'}    

@app.route('/user/<user_id>/remove', methods=['POST'])
def remove_user(user_id):
    try:
        cur.execute("delete from users where user_id='" + user_id + "'")
        conn.commit()
        return {'success': 'successfully removed user with id ' + user_id}
    except Exception as e:
        print(e)
        return {'error': 'removing user with id"' + user_id + '" was unsuccessful.'}    
