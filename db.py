import psycopg2 as pg
from flask_login import UserMixin

abbrevs = ["AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA","KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT","VA","WA","WV","WI","WY","DC"]
states = ["Alabama","Alaska","Arizona","Arkansas","California","Colorado","Connecticut","Delaware","Florida","Georgia","Hawaii","Idaho","Illinois","Indiana","Iowa","Kansas","Kentucky","Louisiana","Maine","Maryland","Massachusetts","Michigan","Minnesota","Mississippi","Missouri","Montana","Nebraska","Nevada","New Hampshire","New Jersey","New Mexico","New York","North Carolina","North Dakota","Ohio","Oklahoma","Oregon","Pennsylvania","Rhode Island","South Carolina","South Dakota","Tennessee","Texas","Utah","Vermont","Virginia","Washington","West Virginia","Wisconsin","Wyoming", "Washington D.C."]
def establish_connection():

    conn = pg.connect("dbname=beerdb user=beerscraper password=getbeer")
    cur = conn.cursor()
    return conn

def create_cursor(conn):
    cur = conn.cursor()
    return cur

def close_connection(conn, cur):
    cur.close()
    conn.close()

def populate_states(conn, cur):
    for i in range(len(states)):
        cur.execute("INSERT INTO States (Abbr, Name) VALUES (%s, %s)",(abbrevs[i], states[i]))

def add_brewery(info, abbr, cur):
    try:
        cur.execute("INSERT INTO Breweries (Name, Beerrating, Link, StateID) VALUES (%s, %s, %s, (SELECT StateID FROM States WHERE Abbr=%s)) RETURNING BreweryID", (info['name'],info['beerrating'],info['link'],abbr))
        # print(cur.fetchone()[0])
        # return cur.fetchone()[0]
    except Exception as e:
        print("ADD BREWERY BUG: ",e,info)
        raise e
    finally:
        return cur.fetchone()[0]

def add_beer(object, abbr, brewid, cur):
    try:
        cur.execute("""
            INSERT INTO Beers (Name, Style, Ratings, AVG, ABV, Link, StateID, BreweryID)
            VALUES (%s, %s, %s, %s, %s, %s, (SELECT StateID FROM States WHERE Abbr=%s), %s);""",
            (object['name'], object['style'],object['ratings'],object['avg'],object['abv'],object['link'],abbr,brewid))
    except Exception as e:
        # print("ADD BEER BUG: %s",e)
        raise e
    finally:
        return

def drop_beer(name, brewery):
    try:
        cur.execute("DELETE FROM Beers where name=%s and breweryID=(SELECT BreweryID FROM Breweries WHERE name=%s)",(name,brewery))
    except Exception as e:
        print(e)
    finally:
        return

def drop_brewery(name, cur):
    try:
        cur.execute("DELETE FROM Beers WHERE BreweryID=(SELECT BreweryID FROM Breweries WHERE name=%s)",(name,))

    except Exception as e:
        print("Beer drop problem: %s",e)
    finally:
        try:
            cur.execute("DELETE FROM Breweries where name=%s",(name,))
        except Exception as e1:
            print("Brew drop problem: %s",e1)
        finally:
            return
        return

class Model():
    def __init__(self):
        self.conn = establish_connection()
        self.cur = create_cursor(self.conn)

    def close():
        close_connection(conn, cur)

# um = UserModel()
# um.check_user('wilder')
# conn, cur = establish_connection()

# bid = add_brewery({'name': 'Deschutes Brewery & Public House', 'beerrating': 4.09, 'link': 'https://www.beeradvocate.com/beer/profile/16862/'},"OR",cur)
# add_beer({'name': 'The Obliterator Maibock', 'style': 'German Maibock', 'abv': '7.4', 'ratings': '3', 'avg': '4.06', 'link': '/beer/profile/63/58877/'},"OR",bid,cur)
# drop_brewery('Deschutes Brewery & Public House',cur)
#cur.execute("CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);")
# cur.execute("DROP TABLE test;")
# cur.execute("CREATE TABLE test ")
#populate_states(conn, cur)
# cur.execute("SELECT * FROM test;")
# print(cur.fetchall())

# conn.commit()

# close_connection(conn, cur)
