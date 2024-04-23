from typing import Union
from fastapi import FastAPI, File, HTTPException, Depends, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext # type: ignore
import logging
import io
import random

from database import *
from detector import *
from starlette.responses import Response

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def read_root():
    return {"Hello": "Planes"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.post("/planedetector")
def get_segmentation_map( username: str, file: bytes = File(...), db: Session = Depends(get_db)):

    logger.info(' PREDICTION started ... ')
    image_detected_bytes = Detector.detector(file)
    logger.info(' PREDICTION finished. ')

    ran = random.randint(100000,999999)
    path = f"../images/prediction{ran}.png"
    image = Image.open(io.BytesIO(image_detected_bytes)).convert("RGB")
    image.save(path,'PNG')

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    new_img = Img(image_link= path, user_id=user.id)
    db.add(new_img)
    db.commit()

    return Response(image_detected_bytes)

@app.post("/getuser")
async def login_for_access_token(username: str, password: str, db: Session = Depends(get_db)):
    #logger.info(' !! Send !! ')
    user = db.query(User).filter(User.username == username).first()

    if not user or not pwd_context.verify(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"message": "Login successful for user: {}".format(username)}

@app.post("/adduser/")
def create_user(username: str, password: str, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = pwd_context.hash(password)
    db_user = User(username=username, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"username": db_user.username, "id": db_user.id}

#@app.post("/addhistory")
#async def add_to_history(username: str, password: str, db: Session = Depends(get_db)):

@app.post("/gethistory")
async def get_from_history(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    imgs = db.query(Img).filter(Img.user_id == user.id).all()

    return [img.image_link for img in imgs]
