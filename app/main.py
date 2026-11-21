from fastapi import FastAPI , Depends,status , HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from app import model , schemas
from database import Base, get_db , engine
from passlib.context import CryptContext
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

app = FastAPI(title="secure signup app", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Automatically create database tables on startup
Base.metadata.create_all(bind=engine)

# Password hashing configuration using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


ROOT_DIR = Path(__file__).resolve().parent.parent
HTML_FILE_PATH = ROOT_DIR / "templates" / "index.html"

@app.get("/", response_class=FileResponse)
def read_login():
    return ROOT_DIR / "templates" / "login.html"

# handling login authentication
@app.post("/login")
def login(user_cred: schemas.userlogin, db: Session = Depends(get_db)):
    # Finding the user in the db by username 
    db_user = db.query(model.User).filter(model.User.username == user_cred.username).first()

    # check if the user existed and password matches the stored hash
    if not db_user or not pwd_context.verify(user_cred.password, db_user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid username or password")

    # If authentication is successful, return a success message
    return {"message": "Login successful", "user_id": db_user.id, "username": db_user.username}


#this will serve the index.html directly at the root URL
@app.get("/signup", response_class=FileResponse)
def read_index():
    return HTML_FILE_PATH

@app.post("/signup", response_model=schemas.User , status_code=status.HTTP_201_CREATED)
def signup(user: schemas.UserCreate , db: Session = Depends(get_db)):
    #Hash the incoming plain-text password securely
    hashed_password = pwd_context.hash(user.password)

    #Map schema data to your SQLAlchemy User model
    db_user = model.User(
        username=user.username,
        password=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        address=user.address
    )
    #Save to Neon PostgreSQL database
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    #Return the newly created user
    return db_user

# serve the forget password
@app.get("/forgot-password", response_class=FileResponse)
def read_forget_password():
    return ROOT_DIR / "templates" / "forget_password.html"


#handel password reset
@app.post("/forgot-password")
def reset_password(reset_request: schemas.passwordreset, db: Session = Depends(get_db)):
    # Find the user in the database by username and email
    db_user = db.query(model.User).filter(
        model.User.username == reset_request.username,
        model.User.email == reset_request.email
        ).first()

    # If user not found, raise an HTTP exception
    if not db_user or db_user.email != reset_request.email:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Hash the new password securely
    hashed_new_password = pwd_context.hash(reset_request.new_password)

    # Update the user's password in the database
    db_user.password = hashed_new_password
    db.commit()
    db.refresh(db_user)

    return {"message": "Password reset successful", "user_id": db_user.id, "username": db_user.username}

# serve the delete account page
@app.get("/delete-account", response_class=FileResponse)
def read_delete_account():
    return ROOT_DIR / "templates" / "delete.html"
#handel account deletion
@app.delete("/delete-account")
def delete_acocunt(delete_request: schemas.accountdelete, db: Session = Depends(get_db)):
    # find the user in the datatbase by username
    db_user = db.query(model.User).filter(model.User.username == delete_request.username).first()


    # check if the user exists and password matches the stored hash
    if not db_user or not pwd_context.verify(delete_request.password, db_user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid username or password")

    # delete the user from the database
    db.delete(db_user)
    db.commit()

    return {"message": "Account deleted successfully", "user_id": db_user.id, "username": db_user.username}