"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User
#from models import Person
import datetime 
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app = Flask(__name__)
jwt=JWTManager(app)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

@app.route("/login", methods=['POST'])
def login():
    body = request.get_json()
    user = User.query.filter_by(email=body['email']).first()
    if(user is None):
        return jsonify({"mensaje": "el usuario no existe"}),404
    else:
        if (user.password != body['password']):
            return "la contraseña esta mala"
        else:
            expiracion = datetime.timedelta(minutes=1)
            token = create_access_token(identity=user.serialize(), expires_delta=expiracion)
            return jsonify({
                "mensaje": "bienvenido!",
                "token": token,
                "tiempo": expiracion.total_seconds(),
                "data": user.serialize()
            })

@app.route("/check", methods=['GET'])
@jwt_required()
def check_user():
    return jsonify({
        "logeado": True
    })


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
