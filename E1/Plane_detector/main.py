from typing import Union
from fastapi import FastAPI, File


import io

from detector import *
from starlette.responses import Response

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.post("/planedetector")
def get_segmentation_map(file: bytes = File(...)):
    """Get segmentation maps from image file"""


    segmented_image = Detector.detector(file)

    bytes_io = io.BytesIO()
    segmented_image.save(bytes_io, format="PNG")
    return Response(bytes_io.getvalue(), media_type="image/png")
