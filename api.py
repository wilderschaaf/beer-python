import flask
from flask import request, jsonify, render_template, url_for, flash, redirect
import flask_login as fl
from forms import LoginForm
import db
import passlib
import os
from models import User
SECRET_KEY = os.urandom(32)


app = flask.Flask(__name__)
app.config["DEBUG"] = True
app.config['SECRET_KEY'] = SECRET_KEY   
login_manager = fl.LoginManager(app)



"""TODO: Need to create a users table in the db to store userids, usernames,
passwords and foreign keys to beers and breweries (maybe states). Then I need
a db function to validate the user and a login form on the home page. once
I have that in place, I should be able to use the flask_login module to
manage sessions. Users should only be able access the db for now."""

@app.route('/', methods=['GET','POST'])
def home():
    try:
        if request.method == "POST":
            name = request.form['name']
            pw = request.form['password']
            print(name)
            print(pw)
    except Exception as e:
        print('error: ',e)
    finally:
        return "<h1>Distant Reading Archive</h1><p>This site is a prototype API for distant reading of science fiction novels.</p>"


@app.route('/api/login',methods=('GET','POST'))
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User(username = form.name.data)
        print("!!!:", user.username)
        if not user.check_user():
            print('invalid username')
            flash('invalid username')
            return redirect(url_for('login'))
        else:
            if not user.check_password(form.password.data):
                flash('invalid password')
                return redirect(url_for('login'))
            print("id attribute: ",login_manager.id_attribute)
        fl.login_user(user)
        return redirect(url_for('get_resources'))
    return render_template('login.html',form=form)
# @login_manager.user_loader
# def load_user(user_id):
#     return User.get(user_id)

@app.route('/api/logout')
def logout():
    fl.logout_user()
    return redirect(url_for('home'))

@login_manager.user_loader
def load_user(id):
    return User.grab_id(id)
# @app.route('/api', methods=('GET','POST'))

@app.route('/api/resources',methods=['GET'])
@fl.login_required
def get_resources():
    return '<h1>USAGE: etc..<h1>'

@app.route('/brewery',methods=['GET'])
def get_brewery():
    b = True
    if 'brewery' in request.args:
        bry = '.*'+request.args['brewery']+'.*'
    elif 'sid' in request.args:
        bry = request.args['sid']
        b = False
    else:
        return "No brewery provided. You fool."
    conn = db.establish_connection()
    cur = db.create_cursor(conn)
    out = ""
    try:
        if b:
            cur.execute('SELECT * FROM Breweries WHERE name ~* %s',(bry,))
        else:
            cur.execute('SELECT * FROM Breweries WHERE StateID=%s',(bry,))
        for brew_data in cur:
            out += "<h1>Here's a brewery</h1><p>"+str(brew_data)+"</p><a href='/beer?id="+str(brew_data[4])+"'>BEERS</a>"
        # cur.execute('SELECT * FROM Beers WHERE BreweryId=%s',(brew_data[4],))
        # for item in cur:
        #     out+="<p>"+str(item)+"</p>"

    except Exception as e:
        out = "<h1>Here's an error</h1><p>"+str(e)+"</p>"
    finally:
        # conn.commit()
        db.close_connection(conn, cur)
        return out

@app.route('/api/resources/breweries/', methods=['GET'])
@fl.login_required
def api_get_brewery():
    name = None
    abbr = None
    beer = None
    vals = []
    if 'name' in request.args:
        name = ".*"+request.args['name']+".*"
        vals.append(name)
    if 'beer' in request.args:
        beer = ".*"+request.args['beer']+".*"
        vals.append(beer)
    if 'abbr' in request.args:
        abbr = request.args['abbr']
        vals.append(abbr)
    results = None
    if name == None and abbr == None and beer==None:
        return jsonify('Usage: supply a brewery name: ?name=brewname, and or a state abbreviation: ?abbr=stabbr, and or a beer name: ?beer=bname')
    conn = db.establish_connection()
    cur = db.create_cursor(conn)

    try:
        qbase = 'SELECT * FROM Breweries WHERE '
        abbrq = '' if abbr == None else ' AND stateid=(SELECT stateid FROM States WHERE abbr=%s)'
        beerq = '' if beer == None else 'breweryid= ANY (SELECT breweryid FROM Beers WHERE name ~* %s)'
        brewq = '' if name == None else 'name ~* %s'

        if name != None:
            cur.execute(qbase+brewq+abbrq,vals)
        elif beer != None:
            cur.execute(qbase+beerq+abbrq,vals)
        else:
            cur.execute(qbase+'TRUE'+abbrq,vals)
        results = cur.fetchall()
    except Exception as e:
        results = str(e)
    finally:
        return jsonify(results)

@app.route('/beer',methods=['GET'])
def get_beers():
    if 'id' in request.args:
        id = request.args['id']
    else:
        return "No brewery id provided. You fool."
    conn = db.establish_connection()
    cur = db.create_cursor(conn)
    out = ""
    try:
        cur.execute('SELECT * FROM Beers WHERE BreweryId=%s',(id,))
        for item in cur:
            out+="<p>"+str(item)+"</p>"
    except Exception as e:
        out = "<h1>Here's an error</h1><p>"+str(e)+"</p>"
    finally:
        # conn.commit()
        db.close_connection(conn, cur)
        return out

@app.route('/api/resources/beers/', methods=['GET'])
def api_get_beer():
    name = None
    abbr = None
    abv = None
    brew = None
    style = None
    results = 20
    vals = []
    if 'name' in request.args:
        name = ".*"+request.args['name']+".*"
        vals.append(name)
    if 'brew' in request.args:
        brew = ".*"+request.args['brew']+".*"
        vals.append(brew)
    if 'style' in request.args:
        style = ".*"+request.args['style']+".*"
        vals.append(style)
    if 'abv' in request.args:
        abv = request.args['abv']
        vals.append(abv)
    if 'abbr' in request.args:
        abbr = request.args['abbr']
        vals.append(abbr)
    if 'results' in request.args:
        try:
            results = int(request.args['abbr'])
        except Exception as e:
            return str(e)

    if len(vals)==0:
        return jsonify('Usage: supply a beername, brewery, state abbreviation, style, or abv')
    conn = db.establish_connection()
    cur = db.create_cursor(conn)
    vals.append(results)
    try:
        qbase = 'SELECT * FROM Beers WHERE TRUE'
        abbrq = '' if abbr == None else ' AND stateid=(SELECT stateid FROM States WHERE abbr=%s)'
        brewq = '' if brew == None else ' AND breweryid= ANY (SELECT breweryid FROM Breweries WHERE name ~* %s)'
        beerq = '' if name == None else ' AND name ~* %s'
        abvq = '' if abv == None else ' AND abv=%s'
        styleq = '' if style == None else ' AND style ~* %s'
        qend = ' ORDER BY ratings DESC LIMIT %s'
        cur.execute(qbase+beerq+brewq+styleq+abvq+abbrq+qend,vals)
        # if name != None:
        #     cur.execute(qbase+brewq+abbrq,vals)
        # elif beer != None:
        #     cur.execute(qbase+beerq+abbrq,vals)
        # else:
        #     cur.execute(qbase+'TRUE'+abbrq,vals)
        results = cur.fetchall()
    except Exception as e:
        results = str(e)
    finally:
        db.close_connection(conn,cur)
        return jsonify(results)

@app.route('/state',methods=['GET'])
def get_state():
    if 'ab' in request.args:
        ab = request.args['ab']
    else:
        ab = '__'
    conn = db.establish_connection()
    cur = db.create_cursor(conn)
    out = ""
    try:
        cur.execute('SELECT * FROM States WHERE Abbr LIKE %s',(ab,))
        for item in cur:
            out+="<p>"+str(item)+"</p><a href='/brewery?sid="+str(item[2])+"'>BREWERIES</a>"

    except Exception as e:
        out = "<h1>Here's an error</h1><p>"+str(e)+"</p>"
    finally:
        # conn.commit()
        db.close_connection(conn, cur)
        return out

@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404

app.run()
