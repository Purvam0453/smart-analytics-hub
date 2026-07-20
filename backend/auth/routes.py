from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
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


    existing = db.query(User).filter(
        User.email == data.email
    ).first()


    if existing:

        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )



    user = User(

        username=data.username,

        email=data.email,

        password=hash_password(data.password)

    )



    db.add(user)

    db.commit()

    db.refresh(user)



    return {

        "message":"Registration Successful"

    }









@router.post("/login")
def login(
    data: LoginSchema,
    db: Session = Depends(get_db)
):


    user = db.query(User).filter(

        User.email == data.email

    ).first()



    if not user:

        raise HTTPException(

            status_code=401,

            detail="Invalid Email"

        )





    if not verify_password(

        data.password,

        user.password

    ):


        raise HTTPException(

            status_code=401,

            detail="Invalid Password"

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