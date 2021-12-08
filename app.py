from flask import Flask , request,jsonify
from flask_sqlalchemy import SQLAlchemy 
from flask_marshmallow import Marshmallow 
from flask_restplus import Api, fields , Resource  #pip install flask-restplus



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///user_details.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True 
app.config['SECRET_KEY']=True

db = SQLAlchemy(app)
ma = Marshmallow(app)
api = Api()
api.init_app(app)


#################################################
###############                ##################
###############    Namespaces  ##################
###############                ##################
#################################################

ns_account = api.namespace('account', description='Account operations')
ns_mall = api.namespace('mall', description='Mall operations')
ns_unit = api.namespace('unit', description='Unit operations')


#################################################
###############                ##################
###############     tables     ##################
###############                ##################
#################################################

class Accounts(db.Model):
    __tablename__ = 'account'
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    name = db.Column(db.String)
    malls = db.relationship('Malls', backref = 'account', cascade = 'all, delete-orphan', lazy = 'dynamic')

class Malls(db.Model):
    __tablename__ = 'mall'
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    name = db.Column(db.String)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable = False)
    units = db.relationship('Units', backref = 'mall', cascade = 'all, delete-orphan', lazy = 'dynamic')


class Units(db.Model):
    __tablename__ = 'unit'
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    name = db.Column(db.String)
    mall_id = db.Column(db.Integer, db.ForeignKey('mall.id'), nullable = False)
    

#################################################
###############                ##################
###############    schemas     ##################
###############                ##################
#################################################

class AccountSchema(ma.Schema):
     class Meta:
         fields = ('id','name')

account_schema = AccountSchema()
accounts_schema = AccountSchema(many=True)

class MallSchema(ma.Schema):
    class Meta:
        fields = ('id','name', 'accountID')

mall_schema = MallSchema()
malls_schema = MallSchema(many=True)


class UnitSchema(ma.Schema):
    class Meta:
        fields = ('id','name', 'mallID')

unit_schema = UnitSchema()
units_schema = UnitSchema(many=True)


#################################################
###############                 #################
###############    payloads     #################
###############                 #################
#################################################

account_model = api.model('account',{
    'name':fields.String('Enter Name'),
})

mall_model = api.model('mall',{
    'name':fields.String('Enter Name'),
    'accountID':fields.Integer('Enter an accountID'),
})

unit_model = api.model('unit',{
    'name':fields.String('Enter a Name'),
    'mallID':fields.Integer('Enter an mallID'),
})


#################################################
###############                     #############
###############    ACCOUNT ROUTES   #############
###############                     #############
#################################################

@ns_account.route('')
class AccountDetails(Resource):
    def get(self):
        #get accounts from the database
        accounts = Accounts.query.all()
        
        list_accounts = [{"id": account.id, "name": account.name} for account in accounts]

        #return the list of accounts
        return list_accounts

    @ns_account.expect(account_model)
    def post(self):
        #Instantiate new account
        new_account = Accounts(name=request.json['name'])
        #add new user
        db.session.add(new_account)
        #commit the change to reflect in database
        db.session.commit()
        #return the response
        return account_schema.jsonify(new_account)

@ns_account.route('/<int:id>')
class AccountPutDelete(Resource):
    @ns_account.expect(account_model)
    def put(self,id):
        try:
            #get Account
            account = Accounts.query.get(id)
            #update account data
            account.name = request.json['name']
            #commit to change in database
            db.session.commit()
            return {'message':'data updated'}
        except :
            return {"error": "this {} id does not exist".format(id)}, 404

    def delete(self,id):
        try:
            #get account
            account = Accounts.query.get(id)
            #delete the account
            db.session.delete(account)
            #commit to reflect in database
            db.session.commit()
            return {'message':'data deleted successfully'}

        except :
            return {"error": "this {} id does not exist".format(id)}, 404
            


#################################################
###############                    ##############
###############    MALL ROUTES     ##############
###############                    ##############
#################################################

@ns_mall.route('')
class MallDetails(Resource):
    def get(self):
        #get malls from the database
        malls = Malls.query.all()
        
        list_malls = [{"id": mall.id, "name": mall.name, "accountID": mall.account_id} for mall in malls]

        #return the list of malls
        return list_malls, 201

    @ns_mall.expect(mall_model)
    def post(self):
        # Check if accountID exist
        list_account_ids =  [account.id for account in Accounts.query.all()]
        accountID = request.json['accountID']

        if accountID not in list_account_ids:
            return {"message": "this {} accountID does not exist".format(accountID)}

        else:
            #Instantiate new mall
            new_mall = Malls(name=request.json['name'], account_id=request.json['accountID'])
            #add new mall
            db.session.add(new_mall)
            #commit the change to reflect in database
            db.session.commit()
            #return the response
            return mall_schema.jsonify(new_mall)

@ns_mall.route('/<int:id>')
class MallPutDelete(Resource):
    @ns_mall.expect(mall_model)
    def put(self,id):
        try:
            #get Mall
            mall = Malls.query.get(id)
            #update mall data
            mall.name = request.json['name']
            #commit to change in database
            db.session.commit()
            return {'message':'data updated'}
        
        except :
            return {"error": "this {} id does not exist".format(id)}, 404

    def delete(self,id):
        try:
            #get mall
            mall = Malls.query.get(id)
            #delete the mall
            db.session.delete(mall)
            #commit to reflect in database
            db.session.commit()
            return {'message':'data deleted successfully'}

        except:
            return {"error": "this {} id does not exist".format(id)}, 404


#################################################
###############                    ##############
###############    UNIT ROUTES     ##############
###############                    ##############
#################################################

@ns_unit.route('')
class UnitDetails(Resource):
    def get(self):
        #get malls from the database
        units = Units.query.all()

        list_units = [{"id": unit.id, "name": unit.name, "accountID": unit.mall_id} for unit in units]

        #return the list of malls
        return list_units, 201

    @ns_unit.expect(unit_model)
    def post(self):
        # Check if accountID exist
        list_mall_ids =  [mall.id for mall in Malls.query.all()]
        mallID = request.json['mallID']

        if mallID not in list_mall_ids:
            return {"message": "this {} mallID does not exist".format(mallID)}

        else:
            #Instantiate new unit
            new_unit = Units(name=request.json['name'], mall_id=request.json['mallID'])
            #add new mall
            db.session.add(new_unit)
            #commit the change to reflect in database
            db.session.commit()
            #return the response
            return unit_schema.jsonify(new_unit)


@ns_unit.route('/<int:id>')
class UnitPutDelete(Resource):
    @ns_unit.expect(unit_model)
    def put(self,id):
        try:
            #get Unit
            unit = Units.query.get(id)
            #update unit data
            unit.name = request.json['name']
            #commit to change in database
            db.session.commit()
            return {'message':'data updated'}
        
        except :
            return {"error": "this {} id does not exist".format(id)}, 404

    def delete(self,id):
        try:
            #get unit
            unit = Units.query.get(id)
            #delete the unit
            db.session.delete(unit)
            #commit to reflect in database
            db.session.commit()
            return {'message':'data deleted successfully'}

        except:
            return {"error": "this {} id does not exist".format(id)}, 404



# Run Server
if __name__ == '__main__':
    app.run(debug=True)
