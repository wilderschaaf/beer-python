import db
from flask_login import UserMixin
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
# from api import login

class User(UserMixin,db.Model):
    def __init__(self, username = None, id = None):
        UserMixin.__init__(self)
        db.Model.__init__(self)
        self.id = id
        self.username = username
        self.passhash = None

    ## need to set up this funtion to return a new user based on id

    @classmethod
    def grab_id(cls,id):
        #stuff
        cls = cls(id = id)
        cls.get_user_by_id(id)
        return cls

    def get_user_by_id(self,id):
        try:
            self.cur.execute('SELECT name, pass_hash FROM users where user_id=%s',(id,))
            self.username, self.passhash = self.cur.fetchone()
        except Exception as e:
            raise e


    def check_user(self):
        try:
            self.cur.execute('SELECT user_id,pass_hash From Users WHERE name=%s',(self.username,))
            results = self.cur.fetchone()
            print(self.username)
            print('results: ',results)
            if results == None:
                return False
            else:
                self.id = results[0]
                self.passhash = results[1]
                return True
        except Exception as e:
            print(e)
            return False
        else:
            return True

    def create_user(self):
        if not self.passhash:
            print("Must have a password set.")
            return
        try:
            self.cur.execute('INSERT INTO users (name, pass_hash, created_on) VALUES (%s,%s,%s)',(self.username.lower(),self.passhash,datetime.datetime.now()))
        except Exception as e:
            print("error: ",e)
            # raise e
            return
        else:
            self.conn.commit()

    def set_password(self, password):
        self.passhash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.passhash,password)


# user = User('Wilder')
# if user.check_user():
#     print(user.check_password('wider'))
# print(user.check_user('wilder'))
