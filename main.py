from typing import Any, Dict, List
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import ydf
import math


app = FastAPI()

origins = [
    "http://localhost:80",  # L'origine de votre app React en développement (ajouter le nom de domaine de l'app)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = ydf.load_model("model")

field_to_feature = {'Prix_m2': 'Prix/m2', 'Type_de_bien': 'Type de bien', 'Nb_de_piece': 'Nb de piece', 'Nb_de_chambre': 'Nb de chambre'}


class Example(BaseModel):
  Prix_m2: float = math.nan
  Type_de_bien: List[str]
  Nb_de_piece: float = math.nan
  Nb_de_chambre: float = math.nan
  Surface: float = math.nan
  Terrasse: str = ""
  Balcon: str = ""
  Garage: str = ""
  Jardin: str = ""
  Ascenseur: str = ""
  Box: str = ""
  Parking: str = ""
  Piscine: str = ""
  Departement: float = math.nan


class Output(BaseModel):
  predictions: float



@app.post("/predict")
async def predict(example: Example) -> Output:
  example_batch: Dict[str, List[Any]] = {
      k: [v] for k, v in example.dict().items()
  }
  example_batch = { field_to_feature.get(k,k):v for k,v in example_batch.items()}
  prediction_batch = model.predict(example_batch).tolist()

  return Output(
    predictions=prediction_batch[0],

  )


@app.post("/predict_batch")
async def predict_batch(example_batch):
  return model.predict(example_batch).tolist()

