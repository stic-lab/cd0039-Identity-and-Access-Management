from http.client import HTTPException
from multiprocessing import AuthenticationError
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


"""
Use the after_request decorator to set Access-Control-Allow
"""
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Headers', 'GET, POST, PATCH, DELETE, OPTIONS')
    return response


'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
# db_drop_and_create_all()



# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks", methods=['GET'])
# @requires_auth('get:drinks')
def retrieve_drinks():
    try:
        drinks = Drink.query.order_by(Drink.id).all()
        drinks_formated=[drink.short() for drink in drinks]
        
        if len(drinks_formated) == 0:
            abort(404)
            
        return jsonify(
            {
                "success": True,
                "drinks": drinks_formated,
            })

    except (MemoryError) as exception: # included for future use case
        print(exception)
        abort(422)
    except Exception as e:
        print(e)
        abort(422)

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks-detail", methods=['GET'])
# @requires_auth('get:drinks-detail')
def retrieve_drinks_details():
    try:
        drinks = Drink.query.order_by(Drink.id).all()
        drinks_formated=[drink.long() for drink in drinks]
        
        if len(drinks_formated) == 0:
            abort(404)
            
        return jsonify(
            {
                "success": True,
                "drinks": drinks_formated,
            })

    except (MemoryError): # included for future use case
        abort(422)
    except Exception as e:
        abort(422)


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks", methods=['POST'])
# @requires_auth('post:drinks')
def create_drinks():
    title = ""
    recipe = ""
    try:
        body = request.get_json()
        title = body.get("title", "")
        recipes = body.get("recipe", "")
        # User Input handling
        if title.isspace() or title == "":
            raise AttributeError(
                "Sorry, title should not be empty")
        if len(recipes) == 0:
            raise AttributeError(
                "Sorry, recipe should not be empty")
        for recipe in recipes:
            if "color" not in recipe or  "name" not in recipe or  "parts" not in recipe:
                raise AttributeError(
                "Sorry, recipe should not be empty")
            if recipe["color"].isspace() or recipe["color"]=="" or recipe["name"].isspace() or recipe["name"]=="" or recipe["parts"]=="":
                raise AttributeError(
                    "Sorry, recipe attribute should not be empty")
            if not isinstance(recipe["parts"], int):
                raise TypeError("Sorry, parts should be an integer")
        
        new_drink = Drink(title=title, recipe=json.dumps(recipes))
        new_drink.insert()
        
        return jsonify({"success": True, "drinks": [new_drink.long()],})
    except (AuthenticationError, MemoryError, TypeError) as exception:  # included for future use case
        print(exception)
        abort(422)
    except Exception as e:
        print(e)
        abort(422)

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks/<int:drink_id>", methods=['PATCH'])
# @requires_auth('patch:drinks')
def update_drink(drink_id):
    title = ""
    recipe = ""
    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        if drink is None:
            abort(404)

        body = request.get_json()
        title = body.get("title", "")
        recipes = body.get("recipe", "")
        # User Input handling
        if title:
            drink.title = title
        if len(recipes) != 0:
            for recipe in recipes:
                if "color" not in recipe or  "name" not in recipe or  "parts" not in recipe:
                    raise AttributeError(
                    "Sorry, recipe should not be empty")
                if recipe["color"].isspace() or recipe["color"]=="" or recipe["name"].isspace() or recipe["name"]=="" or recipe["parts"]=="":
                    raise AttributeError(
                        "Sorry, recipe attribute should not be empty")
                if not isinstance(recipe["parts"], int):
                    raise TypeError("Sorry, parts should be an integer")
            drink.recipe = json.dumps(recipes)
        drink.update()
        return jsonify({"success": True,"drinks": [drink.long()],})

    except (AuthenticationError, MemoryError, TypeError) as exception:  # included for future use case
        print(exception)
        abort(422)
    except Exception as e:
        print(e)
        abort(422)



'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks/<int:drink_id>", methods=["DELETE"])
# @requires_auth('delete:drinks')
def delete_drinks(drink_id):
    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        if drink is None:
            abort(404)
        drink.delete()
        return jsonify({"success": True, "deleted": drink_id,})
    except (AuthenticationError, MemoryError, TypeError):  # included for future use case
        abort(422)
    except Exception as e:
        if e.code == 404:
            abort(e.code)
        else:
            abort(422)

# Error Handling

@app.errorhandler(422)
def unprocessable(error):
    return (
        jsonify({"success": False, "error": 422, "message": "unprocessable"}),
        422,
    )


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''

@app.errorhandler(404)
def not_found(error):
    return (
        jsonify({"success": False, "error": 404, "message": "resource not found"}),
        404,
    )


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''

@app.errorhandler(400)
def bad_request(error):
    return jsonify({"success": False, "error": 400, "message": "bad request"}), 400

@app.errorhandler(405)
def not_found(error):
    return (
        jsonify({"success": False, "error": 405, "message": "method not allowed"}),
        405,
    )
