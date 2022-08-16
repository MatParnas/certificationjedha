import mlflow 
import uvicorn
import json
import pandas as pd 

from pydantic import BaseModel
from typing import Literal, List, Union
from fastapi import FastAPI, File, UploadFile
import boto3



tag_metadata = [
    {
        "name": "Rental Price Prediction",
        "description": "Use the predict endpoint to get a rental price"
    }
]

app = FastAPI(
    title="Getaround rental price API",
    openapi_tags=tag_metadata
)


@app.get("/")
async def index():

    message = "Hello. Welcome to my get around API created to calculate rental price for a car based on previous rentals. please use /docs to learn more and make predictions`"

    return message

class PredictionFeatures(BaseModel):
    model_key:str = 'Peugeot'
    mileage: int = 100000
    engine_power: int = 110
    fuel: str = 'diesel'
    paint_color: str = 'grey'
    car_type: str = 'estate'
    private_parking_available: bool = False
    has_gps: bool = False
    has_air_conditioning: bool = False
    automatic_car: bool = False
    has_getaround_connect: bool = False
    has_speed_regulator: bool = False
    winter_tires: bool = True


@app.post("/Predict" , tags=['Prediction'])
async def predict(predictionFeatures: PredictionFeatures):
    """
    Make a rental price prediction with the rental and car informations
    """

    rental_price_per_day = pd.DataFrame(dict(predictionFeatures), index=[0])

    # Log model from mlflow 
    logged_model = 'runs:/0f036c72f186462da14a52a02ecd3ae9/rental_price_predictor'

    # Load model as a PyFuncModel.
    loaded_model = mlflow.pyfunc.load_model(logged_model)
    prediction = loaded_model.predict(rental_price_per_day)

    # Format response
    response = {"prediction": prediction.tolist()[0]}
    return response



if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0", port=4010)


