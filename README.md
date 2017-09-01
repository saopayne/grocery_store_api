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

1. **Register user**

    Endpoint:
    ```
    /auth/register
    ``` 
        
    Example POST payload :
    ```json
    {
        "username": "any-you-want",
        "name": "Your name",
        "email": "youremail@example.com",
        "password": "password"
    }
    ```
2.  **Login** 

    Endpoint:

    ```
    /auth/login
    ``` 
    Methods = ['POST']
        
    Example POST payload :
    ```json
    {
        "username": "any-you-want",
        "password": "password"
    }
    ```

3.  **Logout** 

    Endpoint:

    ```
    /auth/logout
    ``` 

    Methods = ['POST']

    Authentication header:
    ```
    Authorization: Bearer <your access token>
    ```

4.  **Reset Password** 

    Endpoint:

    ```
    /auth/reset-password
    ``` 
    Methods = ['POST']

    Authentication header:
    ```
    Authorization: Bearer <your access token>
    ```
        
    Example POST payload :
    ```json
    {
        "old_password": "the old password",
        "new_password": "the new password"
    }
    ```

5.  **Shoppinglists**

    Endpoint:
    ```
     /shoppinglists/
    ``` 

    Search by title:

    ```
    /shoppinglists/?q=shoppinglist_title_you_want
    ```

    Methods = ['POST', 'GET']

    Authentication header:
    ```
    Authorization: Bearer <your access token>
    ```
        
    Example POST payload :
    ```json
    {
        "title": "your new shoppinglist title",
        "description": "whatever description"
    }
    ```

    Example response to GET:
    ```json
    [
        {
            "title":"whatever title",
            "description":"whatever description"
        },
        {
            "title":" another title",
            "description":"another description"
        },

        ...

    ]
    ```

6.  **Single Shoppinglist**

    Endpoint:
    ```
     /shoppinglists/<id>
    ``` 

    Methods = ['PUT', 'GET', 'DELETE']

    Authentication header:
    ```
    Authorization: Bearer <your access token>
    ```
        
    Example PUT payload :
    ```json
    {
        "title": "your modified shoppinglist title",
        "description": "whatever new description"
    }
    ```
    Example response to GET:
    ```json
    {
        "title":"whatever title",
        "description":"whatever description"
    }
    ```

7.  **Items of a Shoppinglist**

    Endpoint:
    ```
     /shoppinglists/<id>/items/
    ``` 
    Search by name:
    ```
    /shoppinglists/<id>/items/?q=whatever_name_you_want
    ```

    Methods = ['POST', 'GET']

    Authentication header:
    ```
    Authorization: Bearer <your access token>
    ```
        
    Example POST payload :
    ```json
    {
        "name": "name of new item",
        "quantity": 50,
        "unit": "baskets"
    }
    ```
    Example response to GET:
    ```json
    [
        {
            "name":"whatever name",
            "quantity":8,
            "unit": "whatever units"
        },
        {
            "name":"baking flour",
            "quantity":8,
            "unit": "kg"
        },
        
        ...

    ]
    ```

8.  **Single Item of Shoppinglist**

    Endpoint:
    ```
     /shoppinglists/<id>/items/<item_id>
    ``` 

    Methods = ['PUT', 'GET', 'DELETE']

    Authentication header:
    ```
    Authorization: Bearer <your access token>
    ```
        
    Example PUT payload :
    ```json
    {
        "name": "modified name of item",
        "quantity": 500,
        "unit": "tonnes"
    }
    ```
    Example response to GET:
    ```json
    {
            "name":"baking flour",
            "quantity":8,
            "unit": "kg"
    }
    ```
