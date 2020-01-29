from flask import Flask,request,jsonify,make_response
from flask_sqlalchemy import SQLAlchemy
import uuid
from werkzeug.security import generate_password_hash,check_password_hash
import jwt
import datetime

app=Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:morgan8514@127.0.0.1:5432/api_test'
app.config['SECRET_KEY']='secretkey'

db=SQLAlchemy(app)




# creating tables
class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    public_id=db.Column(db.String(200),unique=False,nullable=True)
    name = db.Column(db.String(50))
    password= db.Column(db.String(200))
    admin= db.Column(db.Boolean)

    def create():
        db.create_all()

class Todo(db.Model):
    id= db.Column(db.Integer,primary_key=True)
    text= db.Column(db.String(200))
    complete=db.Column(db.Boolean)
    public_id= db.Column(db.Integer)

User.create()

# creating user route
@app.route('/user',methods=['POST'])
def create_user():

    data= request.get_json()

    hashed_password = generate_password_hash(data['password'],method='sha256')

    new_user= User(public_id=str(uuid.uuid4()), name=data['name'], password=hashed_password, admin=False)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message' : 'new user created'})

# fetching all user route
@app.route('/user',methods=['GET'])
def get_all_users():
    # querying for all users
    users=User.query.all()
    output=[]

    for user in users:
        user_data={}
        user_data['public_id']=user.public_id
        user_data['name']= user.name
        user_data['password']= user.password
        user_data['admin']=user.admin
        output.append(user_data)


    return jsonify({"user":output})

@app.route('/user/<public_id>',methods=['GET'])
def get_one_user(public_id):

    single_user=User.query.filter_by(public_id=public_id).first()
    if not single_user:
        return jsonify({"message":"no user found!"})

    user_data={}
    user_data['public_id']= single_user.public_id
    user_data['name']= single_user.name
    user_data['password']=single_user.password
    user_data['admin']=single_user.admin

    return jsonify({"message": user_data})

@app.route('/user/<public_id>',methods=['PUT'])
def promote_user(public_id):

    single_user=User.query.filter_by(public_id=public_id).first()
    if not single_user:
        return jsonify({"message":" no user found! "})
    single_user.admin=True
    db.session.commit()

    return jsonify({"message" : "User has been promoted!"})

@app.route('/user/<public_id>',methods=['DELETE'])
def delete_user(public_id):
        
    single_user=User.query.filter_by(public_id=public_id).first()
    if not single_user:
        return jsonify({"message":" no user found! "})

    db.session.delete(single_user)
    db.session.commit()

    return jsonify({"message":"user deleted!"})

# login route
@app.route('/login')
def login():

    auth=request.authorization 
    if not auth or not auth.username or not auth.password:
        return make_response ('could not verify!',401, {'WWW-Authenticate':'Basic realm="Login required!'})

    user = User.query.filter_by(name=auth.username).first()

    if not user:
        return make_response ('could not verify!',401, {'WWW-Authenticate':'Basic realm="Login required!'})

    # to compare hasshed password yo use check_password_harsh
    # comparing text password to inputed password. if it is correct, we now generate the token

    if check_password_hash(user.password,auth.password):
        # creating token
        token = jwt.encode({"public_id": user.public_id, "exp":datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'] )
        # returning the token as a jason object
        return jsonify({"token" : token.decode('UTF-8')})

    # if the password is wrong it returns the error message below
    return make_response ('could not verify!',401, {'WWW-Authenticate':'Basic realm="Login required!'})







if __name__=='main':
    app.run(debug=True)