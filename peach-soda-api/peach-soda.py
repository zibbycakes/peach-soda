from flask import Flask, session
from flask import request
import psycopg2
from config import config, secret
import json
from datetime import datetime
from pytz import timezone
from markupsafe import escape
from werkzeug.security import generate_password_hash, check_password_hash
import user_class
from flask_login import LoginManager, login_user, current_user, logout_user, login_required

app = Flask(__name__)
app.secret_key = secret()

params = config()
print('connecting to the postgres db...')
conn = psycopg2.connect(**params)

cur = conn.cursor()

tz = timezone('America/Chicago')

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return user_class.User.get(user_id)

@app.route('/')
def ping():
    # return {'success': 'Hello world, ' + (current_user.user_id.decode('utf-8'))+'!'}
    return {'success': 'Hello world!'}


@app.route('/suggestions', methods=['GET', 'POST'])
@login_required
def suggestion():
    if request.method == 'GET':
        return get_suggestions()
    else:
        req_data = request.get_json()
        if 'suggestion' in req_data:
            # return post_suggestions(req_data['suggestion'], req_data['user_id'])
            return post_suggestions(req_data['suggestion'])


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

def post_suggestions(suggestion_text):
    try:
        now_string = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S %Z')
        cur.execute("insert into music_suggestions (suggestion, date_added, user_id) values('" + suggestion_text + "','" + now_string + "','" + str(current_user.user_id.decode('utf-8')) + "')")
        conn.commit()
        return {'success': 'successfully added "' + suggestion_text + '" to the database at time ' + now_string + ' for user id ' + str(current_user.user_id.decode('utf-8')) + '.'}
    except Exception as e:
        print(e)
        return {'error': 'adding "' + suggestion_text + '" to the database was unsuccessful.'}

@app.route('/suggestions/<suggestion_id>')
@login_required
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
@login_required
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
@login_required
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
@login_required
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
        exist = does_user_exist(req_data['username'])
        if(exist != True):
            add_query = "insert into users (first_name, username, password) values ('" + req_data['first_name'] + "','"+ req_data['username'] + "','"+ generate_password_hash(req_data['password'])+ "')"
            cur.execute(add_query)
            conn.commit()
            return {'success': 'successfully added user with username ' + req_data['username']}
        else:
            return {'error': 'username ' + req_data['username'] + ' already exists'}
    except Exception as e:
        print(e)
        return {'error': 'adding user with username "' + req_data['username'] + '" was unsuccessful.'}

def does_user_exist(username):
    try:
        check_query = "select count(*) from users where username = '" + username + "'"
        cur.execute(check_query)
        row = cur.fetchone()
        if(row[0] > 0):
            return True
        return False
    except Exception as e:
        print(e)
        return False 

@app.route('/login', methods=['POST'])
def login():
    try:
        login_data = request.get_json()
        cur.execute("select user_id, first_name, username, password, spotify_id, activated from users where username=\'" + login_data['username'] + "\'")
        row = cur.fetchone()

        db_user = {
            'user_id': row[0],
            'first_name': row[1],
            'username': row[2],
            'password': row[3],
            'spotify_id': row[4],
            'activated': row[5]
        }
        if not check_password_hash(db_user['password'], login_data['password']):
            return {'error': 'incorrect username or password'}
        else:
            session['username'] = db_user['username']
            session['first_name'] = db_user['first_name']
            user_obj = user_class.User(str(db_user['user_id']).encode("utf-8"), session['username'], session['first_name']) 
            # need activated account?
            user_obj.set_activated(db_user['activated'])
            user_obj.set_authenticated(True)
            login_user(user_obj)
            return {'success': 'Successfully logged in for ' + escape(session['username'])}
    except psycopg2.ProgrammingError as e:
        print(e)
        return {'error': 'Incorrect username or password.'}
    except Exception as e:
        print(e)
        return {'error': 'Unknown error while logging in'}

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    try:
        # print('logging out for ' + current_user.username + '...')
        logout_user()
        return {'success': 'successfully logged out'}
    except Exception as e:
        print(e)
        return {'error': 'Unknown error while logging out'}