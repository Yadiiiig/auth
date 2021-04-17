#main.py

import jwt
import mysql.connector
from typing import Optional
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse
from enum import Enum
from datetime import timedelta, datetime
from pydantic import BaseModel
from db import *
from authentication import *

app = FastAPI()

@app.get("/verified_route", status_code=201)
def verify(auth: Optional[str] = Header(None)):
    result = check_auth(auth)
    if result == False:
        raise 403

    ac = path_handler(result["role"], "*")
    match ac:
        case True:
            return "Allowed"
        case False:
            return 401
        case _:
            raise 403

@app.get("/verified_route_specific_role", status_code=201)
def verify(auth: Optional[str] = Header(None)):
    result = check_auth(auth)
    if result == False:
        raise 403
        
    ac = path_handler(result["role"], "admin")
    match ac:
        case True:
            return "Allowed"
        case False:
            return 401
        case _:
            raise 403


class LoginBody(BaseModel):
    email: str
    password: str

@app.post("/login", status_code=200)
def login(user: LoginBody):
    query = "SELECT id, password, role FROM users WHERE email = %s"
    data = (user.email, )
    result = query_return(query, data, cursor, cnx)

    if result == []:
        raise 403
    else:
        if result[0]["password"] == user.password:
            return auth_user(result[0]["id"], result[0]["role"])
        else:
            raise 403

@app.patch("/refresh_token", status_code=200)
def refresh(auth: Optional[str] = Header(None)):
    result = check_auth(auth)
    if result == False:
        return 403
    return auth_user(result["user_id"], result["role"])
