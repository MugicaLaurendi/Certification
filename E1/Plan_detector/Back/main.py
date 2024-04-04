from typing import Union
from fastapi import FastAPI, File, HTTPException


import io

from detector import *
from starlette.responses import Response

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "Planes"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.post("/planedetector")
def get_segmentation_map(file: bytes = File(...)):
    """Get segmentation maps from image file"""

    #if type(file) == bytes :
        #raise HTTPException(status_code=402, detail=f"Empty file")

    image_detected_bytes = Detector.detector(file)

    return Response(image_detected_bytes)
