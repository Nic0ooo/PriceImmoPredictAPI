from typing import Any, Dict, List
from fastapi import FastAPI, Request, HTTPException
from starlette.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi.responses import JSONResponse

from pydantic import BaseModel
import ydf
import math

app = FastAPI()

# Liste des origines autorisées
origins = [
    "http://localhost:80",  # L'origine de votre app React en développement
]

# Configuration du rate limiter : ici, 5 requêtes par minute par adresse IP par défaut
limiter = Limiter(key_func=get_remote_address, default_limits=["5/minute"])
app.state.limiter = limiter

# Ajout du middleware SlowAPI
app.add_middleware(SlowAPIMiddleware)

# Gestionnaire d'exceptions pour les dépassements de quota
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Chargement de votre modèle
model = ydf.load_model("model")

# Mapping entre les noms des features et les attributs du modèle
field_to_feature = {
    'Prix_m2': 'Prix/m2',
    'Type_de_bien': 'Type de bien',
    'Nb_de_piece': 'Nb de piece',
    'Nb_de_chambre': 'Nb de chambre'
}

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
@limiter.limit("5/minute")
async def predict(example: Example, request: Request) -> Output:
    # Construction du batch d'exemple
    example_batch: Dict[str, List[Any]] = {k: [v] for k, v in example.dict().items()}
    example_batch = {field_to_feature.get(k, k): v for k, v in example_batch.items()}
    prediction_batch = model.predict(example_batch).tolist()
    return Output(predictions=prediction_batch[0])

@app.post("/predict_batch")
@limiter.limit("5/minute")
async def predict_batch(example_batch, request: Request):
    return model.predict(example_batch).tolist()