import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS


from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase --> DONE
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()


# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
    where drinks is the list of drinks
        or appropriate status code indicating reason for failure --> DONE
'''
@app.route('/drinks', methods=['GET'])
def get_drinks():
    drinks_query = Drink.query.all()
    print(drinks_query)
    drinks = [drink.short() for drink in drinks_query]
    if not drinks:
        abort(404)
    return jsonify({
        "success": True, "drinks": drinks
    })


'''
@TODO implement endpoint
GET /drinks-detail
it should require the get:drinks-detail permission
it should contain the drink.long() data representation
returns status code 200 and json {"success": True, "drinks":
 drinks} where drinks is the list of drinks
or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(self):
    drinks_query = Drink.query.all()
    drinks = [drink.long() for drink in drinks_query]
    if not drinks:
        abort(404)
    return jsonify({
        "success": True, "drinks": drinks
    })


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks":
     drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth(permission='post:drinks')
def create_drink(payload):
    # Must find out how to store recipe correctly
    data = request.get_json()
    if not data:
        abort(400)

    new_title = data.get('title')
    new_recipe = data.get('recipe')

    if not new_title or not new_recipe:
        abort(400)

    # Creating the drink
    new_drink = Drink(title=new_title, recipe=json.dumps(new_recipe))
    try:
        new_drink.insert()
    except Exception:
        abort(401)

    # Query for drinks and getting the newly created
    new_drinks = Drink.query.all()
    # Formating response
    drinks = [drink.long()
              for drink in new_drinks if drink.id == new_drink.id]
    if not drinks:
        abort(404)

    return jsonify({
        "success": True, "drinks": drinks
    })


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks":
     drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure --> DONE
'''
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth(permission='patch:drinks')
def patch_drink(payload, id):
    # Get drink to PATCH
    drink = Drink.query.get(id)
    if not drink:
        abort(404)
    # Check what values are available to PATCH
    data = request.get_json()
    if 'title' in data:
        drink.title = data.get('title')
    if 'recipe' in data:
        new_recipe = data.get('recipe')
        drink.recipe = json.dumps(new_recipe)
    try:
        drink.update()
    except Exception:
        abort(401)

    result = Drink.query.filter_by(id=drink.id)
    drinks = [drink.long() for drink in result]
    return jsonify({
         "success": True, "drinks": drinks
     })


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete":
     id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure --> DONE
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth(permission='delete:drinks')
def delete_drink(payload, id):
    drink = Drink.query.get(id)
    if not drink:
        abort(404)
    try:
        drink.delete()
    except Exception:
        abort(401)
    return jsonify({
        "success": True,
        "delete": id
    })


# Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                "success": False,
                "error": 422,
                "message": "unprocessable"
            }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404 --> DONE
'''


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


'''
@TODO implement error handler for 404
    error handler should conform to general task above --> DONE SAME AS ABOVE
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(400)
def invalid_header(error):
    return jsonify({
        "success": False,
        'code': 'invalid_header',
        "message": "Unable to find the appropriate key."
    }), 400


@app.errorhandler(401)
def authorization_malformated(error):
    return jsonify({
        "success": False,
        'code': 'authorization_malformated',
        "message": "Authorization malformed."
    }), 401
