from typing import Union
from fastapi import FastAPI, File, HTTPException
import logging

import io

from detector import *
from starlette.responses import Response

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/")
def read_root():
    return {"Hello": "Planes"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.post("/planedetector")
def get_segmentation_map(file: bytes = File(...)):

    logger.info('Send')
    image_detected_bytes = Detector.detector(file)

    return Response(image_detected_bytes)
