from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel

from database import get_db

from models.user import User, LoginLog

from auth.password import hash_password, verify_password
from auth.jwt import create_access_token



router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)





class RegisterSchema(BaseModel):

    username: str

    email: str

    password: str





class LoginSchema(BaseModel):

    email: str

    password: str







@router.post("/register")
def register(
    data: RegisterSchema,
    db: Session = Depends(get_db)
):
    cleaned_email = data.email.strip().lower()
    cleaned_username = data.username.strip()

    if not cleaned_email or not cleaned_username or not data.password:
        raise HTTPException(
            status_code=400,
            detail="Please provide a valid username, email, and password."
        )

    # Check existing email
    existing_email = db.query(User).filter(
        func.lower(User.email) == cleaned_email
    ).first()
    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="This email is already registered. Please log in."
        )

    # Check existing username
    existing_username = db.query(User).filter(
        func.lower(User.username) == cleaned_username.lower()
    ).first()
    if existing_username:
        raise HTTPException(
            status_code=400,
            detail="This username is already taken. Please choose a different username."
        )

    try:
        user = User(
            username=cleaned_username,
            email=cleaned_email,
            password=hash_password(data.password)
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create account: {str(e)}"
        )

    return {
        "message": "Registration Successful",
        "username": user.username
    }


@router.post("/login")
def login(
    data: LoginSchema,
    db: Session = Depends(get_db)
):
    cleaned_email = data.email.strip().lower()

    user = db.query(User).filter(
        func.lower(User.email) == cleaned_email
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="No account found with this email."
        )

    if not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect password. Please try again."
        )






    # =========================
    # SAVE LOGIN LOG
    # =========================


    login_log = LoginLog(

        user_id=user.id,

        username=user.username

    )


    db.add(login_log)

    db.commit()





    token = create_access_token(

        {

            "sub": user.email

        }

    )




    return {


        "access_token":token,


        "token_type":"bearer",


        "username":user.username


    }