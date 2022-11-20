# Python
import json
from uuid import UUID
from datetime import date
from datetime import datetime
from typing import Optional

# Pydantic

from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import Field


# FastAPI
from fastapi import FastAPI
from fastapi import status
from fastapi import Body, Path
from fastapi import HTTPException


app = FastAPI()

# Models --> Defining the models of users and tweets
class UserBase(BaseModel):
    user_id: UUID = Field(...)
    email: EmailStr = Field(...)

class UserLogin(UserBase):
    password: str = Field(
        ...,
        min_length=8,
        max_length=64
    )

class User(UserBase):
    first_name: str = Field(
        ...,
        min_length= 1,
        max_length=50
    )
    last_name: str = Field(
        ...,
        min_length= 1,
        max_length=50
    )
    birth_date: Optional[date] = Field(default=None)

class UserRegister(User):
    password: str = Field(
        ...,
        min_length=8,
        max_length=64
    )

class Tweet(BaseModel):
    tweet_id: UUID = Field(...)
    content: str = Field(
        ...,
        min_length=1,
        max_length=256
    )
    created_at: datetime = Field(default=datetime.now())
    updated_at: Optional[datetime] = Field(default=None)
    by: User = Field(...)

class TweetUpdate(BaseModel):
    content: str = Field(
        ...,
        min_length=1,
        max_length=256
    )
    updated_at: datetime = Field(default=datetime.now())

# Path Operations

## Users

### Register a user
@app.post(
    path="/signup",
    response_model=User,
    status_code=status.HTTP_201_CREATED,
    summary="Register a user",
    tags=["Users"]
    )
def signup(user: UserRegister = Body(...)):
    """
    Signup

    This path operation register a user in the app

    Parameters:
        - Request Body Parameter
            - user: UserRegister

    Returns a json with the basic user information:
        - user_id: UUID
        - email: EmailStr
        - first_name: str
        - last_name: str
        - birth_date: str
    """
    with open("users.json", "r+", encoding="utf-8") as f:
        # Convert a json to dict
        results = json.loads(f.read())
        user_dict = user.dict()
        user_dict["user_id"] = str(user_dict["user_id"])
        user_dict["birth_date"] = str(user_dict["birth_date"])
        results.append(user_dict)
        # Move cursor in f to the start
        f.seek(0)
        # Convert a dict to json
        f.write(json.dumps(results))
        return user

### Login a user
@app.post(
    path="/login",
    response_model=User,
    status_code=status.HTTP_200_OK,
    summary="Login a user",
    tags=["Users"]
    )
def login(email: EmailStr = Body(...), password: str = Body(...)):
    """
    Login

    This path operation login a user in the app

    Parameters:
        - Request Body Parameter
            - email: EmailStr
            - password: str

    Returns a json with the basic user information:
        - user_id: UUID
        - email: EmailStr
        - first_name: str
        - last_name: str
        - birth_date: str
    """
    with open("users.json", "r+", encoding="utf-8") as f:
        user_logged_in = None
        all_users = json.loads(f.read())
        for user in all_users:
            if user["email"] == email and user["password"] == password:
                user_logged_in = user
                break      
        if not user_logged_in:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user or password doesn't exist!"
            ) 
        return user_logged_in

### Show all users
@app.get(
    path="/users",
    response_model=list[User],
    status_code=status.HTTP_200_OK,
    summary="Show all users",
    tags=["Users"]
    )
def show_all_users():
    """
    Show all users

    This path operation shows all  users in the app

    Parameters:
        -

    Returns a json with all users in the app, with the following keys:
        - user_id: UUID
        - email: EmailStr
        - first_name: str
        - last_name: str
        - birth_date: str
    """
    with open("users.json", "r", encoding="utf-8") as f:
        results = json.loads(f.read())
        return results

### Show a user
@app.get(
    path="/users/{user_id}",
    response_model=User,
    status_code=status.HTTP_200_OK,
    summary="Show a user",
    tags=["Users"]
    )
def show_a_user(user_id: UUID = Path(...)):
    """
    Show a user

    This path operation shows a user in the app

    Parameters:
        - Path parameters:
            - user_id

    Returns a json with a user information in the app, with the following keys:
        - user_id: UUID
        - email: EmailStr
        - first_name: str
        - last_name: str
        - birth_date: str
    """
    with open("users.json", "r", encoding="utf-8") as f:
        all_users = json.loads(f.read())
        for user in all_users:
            if user["user_id"] == str(user_id):
                return user
    
        raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="The user doesn't exist!"
        )

### Delete a user
@app.delete(
    path="/users/{user_id}/delete",
    response_model=User,
    status_code=status.HTTP_200_OK,
    summary="Delete a user",
    tags=["Users"]
    )
def delete_a_user(user_id: UUID = Path(...)):
    """
    Delete a user

    This path operation delete a user in the app

    Parameters:
        - Path parameters:
            - user_id

    Returns a json with a user information in the app, with the following keys:
        - user_id: UUID
        - email: EmailStr
        - first_name: str
        - last_name: str
        - birth_date: str
    """
    with open("users.json", "r+", encoding="utf-8") as f:
        deleted_user = None
        all_users = json.loads(f.read())
        for user in all_users:
            if user["user_id"] == str(user_id):
                deleted_user = user
                break
        
        if not deleted_user:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user doesn't exist!"
            ) 

        all_users.remove(deleted_user)
        f.seek(0)
        f.truncate()
        f.write(json.dumps(all_users))
        return deleted_user

### Update a user
@app.put(
    path="/users/{user_id}/update",
    response_model=User,
    status_code=status.HTTP_200_OK,
    summary="Update a user",
    tags=["Users"]
    )
def update_a_user(user_id: UUID = Path(...), user_to_update: User = Body(...)):
    """
    Update a user

    This path operation update a user information in the app

    Parameters:
        - Path parameters:
            - user_id
        - Request Body Parameter
            - user_updated: User


    Returns a json with the user information updated, with the following keys:
        - user_id: UUID
        - email: EmailStr
        - first_name: str
        - last_name: str
        - birth_date: str
    """
    with open("users.json", "r+", encoding="utf-8") as f:
        user_updated = None
        all_users = json.loads(f.read())
        for user in all_users:
            if user["user_id"] == str(user_id):
                user["user_id"] = str(user_to_update.user_id)
                user["first_name"] = user_to_update.first_name
                user["last_name"] = user_to_update.last_name
                user["birth_date"] = str(user_to_update.birth_date)
                user["email"] = user_to_update.email
                user_updated = user
                break
        
        if not user_updated:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user doesn't exist!"
            ) 

        f.seek(0)
        f.truncate()
        f.write(json.dumps(all_users))
        return user_updated

## Tweets

### Show all tweets
@app.get(
    path="/",
    response_model=list[Tweet],
    status_code=status.HTTP_200_OK,
    summary="Show all tweets",
    tags=["Tweets"]
    )
def home():
    """
    Show all users

    This path operation shows all  tweets in the app

    Parameters:
        -

    Returns a json with all tweets in the app, with the following keys:
        - tweet_id: UUID
        - content: str
        - created_at: datetime
        - updated_at: Optional[datetime]
        - by: User
    """
    with open("tweets.json", "r", encoding="utf-8") as f:
        results = json.loads(f.read())
        return results

### Post a tweet
@app.post(
    path="/post",
    response_model=Tweet,
    status_code=status.HTTP_201_CREATED,
    summary="Post a tweet",
    tags=["Tweets"]
    )
def post(tweet: Tweet = Body(...)):
    """
    Post a tweet

    This path operation post a tweet in the app

    Parameters:
        - Request Body Parameter
            - tweet: Tweet

    Returns a json with the basic tweet information:
    tweet_id: UUID
    content: str
    created_at: datetime
    updated_at: Optional[datetime]
    by: User
    """
    with open("tweets.json", "r+", encoding="utf-8") as f:
        # Convert a json to dict
        results = json.loads(f.read())
        tweet_dict = tweet.dict()
        tweet_dict["tweet_id"] = str(tweet_dict["tweet_id"])
        tweet_dict["created_at"] = str(tweet_dict["created_at"])
        if tweet_dict["updated_at"]:
            tweet_dict["updated_at"] = str(tweet_dict["updated_at"])
        tweet_dict["by"]["user_id"] = str(tweet_dict["by"]["user_id"])
        tweet_dict["by"]["user_id"] = str(tweet_dict["by"]["user_id"])
        tweet_dict["by"]["birth_date"] = str(tweet_dict["by"]["birth_date"])
        
        results.append(tweet_dict)
        # Move cursor in f to the start
        f.seek(0)
        # Convert a dict to json
        f.write(json.dumps(results))
        return tweet    

### Show a tweet
@app.get(
    path="/tweets/{tweet_id}",
    response_model=Tweet,
    status_code=status.HTTP_200_OK,
    summary="Show a tweet",
    tags=["Tweets"]
    )
def show_a_tweet(tweet_id: UUID = Path(...)):
    """
    Show a tweet

    This path operation shows a tweet in the app

    Parameters:
        - Path parameters:
            - tweet_id

    Returns a json with a user information in the app, with the following keys:
        - tweet_id: UUID
        - content: str
        - created_at: datetime
        - updated_at: Optional[datetime]
        - by: User
    """
    with open("tweets.json", "r", encoding="utf-8") as f:
        all_tweets = json.loads(f.read())
        for tweet in all_tweets:
            if tweet["tweet_id"] == str(tweet_id):
                return tweet
    
        raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="The tweet doesn't exist!"
        )


### Delete a tweet
@app.delete(
    path="/tweets/{tweet_id}/delete",
    response_model=Tweet,
    status_code=status.HTTP_200_OK,
    summary="Delete a tweet",
    tags=["Tweets"]
    )
def delete_a_tweet(tweet_id: UUID = Path(...)):
    """
    Delete a tweet

    This path operation delete a tweet in the app

    Parameters:
        - Path parameters:
            - tweet_id

    Returns a json with a tweet deleted information in the app, with the following keys:
        - tweet_id: UUID
        - content: str
        - created_at: datetime
        - updated_at: Optional[datetime]
        - by: User
    """
    with open("tweets.json", "r+", encoding="utf-8") as f:
        deleted_tweet = None
        all_tweets = json.loads(f.read())
        for tweet in all_tweets:
            if tweet["tweet_id"] == str(tweet_id):
                deleted_tweet = tweet
                break
        
        if not deleted_tweet:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The tweet doesn't exist!"
            ) 

        all_tweets.remove(deleted_tweet)
        f.seek(0)
        f.truncate()
        f.write(json.dumps(all_tweets))
        return deleted_tweet

### Update a tweet
@app.put(
    path="/tweets/{tweet_id}/update",
    response_model=Tweet,
    status_code=status.HTTP_200_OK,
    summary="Update a tweet",
    tags=["Tweets"]
    )
def update_a_tweet(tweet_id: UUID = Path(...), tweet_to_update: TweetUpdate = Body(...)):
    """
    Update a tweet

    This path operation update a tweet in the app

    Parameters:
        - Path parameters:
            - tweet_id

    Returns a json with the updated tweet in the app, with the following keys:
        - tweet_id: UUID
        - content: str
        - created_at: datetime
        - updated_at: Optional[datetime]
        - by: User
    """
    with open("tweets.json", "r+", encoding="utf-8") as f:
        updated_tweet = None
        all_tweets = json.loads(f.read())
        for tweet in all_tweets:
            if tweet["tweet_id"] == str(tweet_id):
                tweet["content"] = str(tweet_to_update.content)
                tweet["updated_at"] = str(tweet_to_update.updated_at)
                updated_tweet = tweet
                break
        
        if not updated_tweet:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The tweet doesn't exist!"
            ) 

        f.seek(0)
        f.truncate()
        f.write(json.dumps(all_tweets))
        return updated_tweet