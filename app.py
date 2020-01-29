from flask import Flask,request,jsonify
from flask_sqlalchemy import SQLAlchemy
import uuid
from werkzeug.security import generate_password_hash,check_password_hash

app=Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:morgan@127.0.0.1:5432/api_test'
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
    user_id= db.Column(db.Integer)

User.create()

# creating user route
@app.route('/user',methods=['POST'])
def create_user():

    data= request.get_json()

    hashed_password = generate_password_hash(data['password_j'],method='sha256')

    new_user= User(public_id=str(uuid.uuid4()), name=data['name_j'], password=hashed_password, admin=False)

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

@app.route('/user/<user_id>',methods=['GET'])
def get_one_user():
    return ''

@app.route('/user/<user_id>',methods=['PUT'])
def promote_user():
    return ''

@app.route('/user/<user_id>',methods=['DELETE'])
def delete_user():
    return ''






if __name__=='main':
    app.run(debug=True)