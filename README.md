# ShoppingListAPI [![Build Status](https://travis-ci.org/Tinitto/ShoppingListAPI.png?branch=master)](https://travis-ci.org/Tinitto/ShoppingListAPI)
This is the RESTful API for the ShoppingList App, the app that allows you to keep and share shopping lists

## About
This project is part of the [Andela Fellowship](https://andela.com/) Bootcamp.

The ShoppingList app is a web application meant to help users keep track of their shopping items easily. 

This is a REST API built in python using Flask.

It also enables users to share such lists with other people for example if the shopper and the list compiler are different people.

## Dependencies
1. Flask version 0.12+
2. Python version 3.5+
3. Postgresql 9.6+

## How to run flask application
1. Clone the repository to your computer
2. Activate your virtualenv
3. In your terminal, enter the directory ShoppingListAPI
4. run the following command to install the app package into your virtualenv (Don't forget the dot at the end)

    ``` pip install -r requirements.txt ```

5. To start the app, run the following commands in succession still in the same directory

    ```export FLASK_APP=flask_app/run.py```

    ```export FLASK_DEBUG=true ```

    ```export DATABASE_URL="sqlite://"```

    ```export APP_SETTINGS="development"```

    ```export SECRET="the-development-key-secret-hide-very-far"```

    ```flask run ```

    _On windows, use 'set' instead of 'export'_

## How to test the flask appliaction
1. Clone the repository to your computer
2. Ensure you have the dependencies on your system
3. Install Coverage.py in your virtualenv using your terminal


    ``` pip install coverage```

4. run command in the folder ShoppingListAPI

    ``` sh -c 'cd ./api/ && coverage run -m --source=app unittest discover test && coverage report' ```

5. Observe the output in your terminal

## Demo
The demo app on Heroku can be found [https://shoppinglist-rest-andela.herokuapp.com](https://shoppinglist-rest-andela.herokuapp.com)

### Current endpoints
1.  Register user

    endpoint:
    ```
    /auth/register
    ``` 
        
    example POST payload :
    ```json
    {
        "username": "any-you-want",
        "name": "Your name",
        "email": "youremail@example.com",
        "password": "password"
    }
    ```
2.  Login

    endpoint:
    ```
    /auth/login
    ``` 
        
    example POST payload :
    ```json
    {
        "username": "any-you-want",
        "password": "password"
    }
    ```

3.  Shoppinglists

    endpoint:
    ```
     /shoppinglists/
    ``` 

    Methods = ['POST', 'GET']

    Authentication header
    ```
    Authorization: Bearer <your access token>
    ```
        
    example POST payload :
    ```json
    {
        "title": "your new shoppinglist title",
        "description": "whatever description"
    }
    ```

3.  Single Shoppinglist

    endpoint:
    ```
     /shoppinglists/<id>
    ``` 

    Methods = ['PUT', 'GET', 'DELETE']

    Authentication header:
    ```
    Authorization: Bearer <your access token>
    ```
        
    example PUT payload :
    ```json
    {
        "title": "your modified shoppinglist title",
        "description": "whatever new description"
    }
    ```

4.  Items of a Shoppinglist

    endpoint:
    ```
     /shoppinglists/<id>/items/
    ``` 

    Methods = ['POST', 'GET']

    Authentication header:
    ```
    Authorization: Bearer <your access token>
    ```
        
    example POST payload :
    ```json
    {
        "name": "name of new item",
        "quantity": 50,
        "unit": "baskets"
    }
    ```

5.  Single Item of Shoppinglist

    endpoint:
    ```
     /shoppinglists/<id>/items/<item_id>
    ``` 

    Methods = ['PUT', 'GET', 'DELETE']

    Authentication header:
    ```
    Authorization: Bearer <your access token>
    ```
        
    example PUT payload :
    ```json
    {
        "name": "modified name of item",
        "quantity": 500,
        "unit": "tonnes"
    }
    ```


### Endpoints in the pipeline
1. ``` /auth/logout ```  
    Methods = [POST]
2. ``` /auth/reset-password ```
    Methods = [POST]
