import os
from dotenv import load_dotenv
from os.path import join, dirname
from flask import Request, Response
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient
from pydantic import BaseModel
from services import check_coverage

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Instancia de la aplicación FastAPI
app = FastAPI(
    title="ms-core-factibility",
    description="Microservicio para verificar cobertura",
    version="1.0.0",
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todos los orígenes (puedes personalizar esto)
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos HTTP
    allow_headers=["*"],  # Permitir todos los headers
)

# Modelo de datos para la entrada
class CoverageRequest(BaseModel):
    latitude: float
    longitude: float

EXPECTED_TOKEN = os.environ.get("API_TOKEN")

# Endpoint principal
@app.post("/check_coverage/")
async def verify_coverage(request: CoverageRequest, Authorization: str = Header(...)):
    try:
        if Authorization != EXPECTED_TOKEN:
            raise HTTPException(status_code=401, detail="Unauthorized")
        result = check_coverage(request.latitude, request.longitude)
        return {"coverage": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Punto de entrada para Google Cloud Functions
def main(request: Request) -> Response:
    """
    Convierte una solicitud Flask en una solicitud FastAPI.
    """
    path = request.path
    method = request.method
    body = request.get_data(as_text=True)
    headers = dict(request.headers)

    # Usa FastAPI TestClient para manejar la solicitud
    client = TestClient(app)
    fastapi_response = client.request(
        method=method,
        url=path,
        headers=headers,
        data=body,
    )

    # Devuelve la respuesta de FastAPI como respuesta Flask
    return Response(
        response=fastapi_response.content,
        status=fastapi_response.status_code,
        headers=dict(fastapi_response.headers),
    )

# Bloque para pruebas locales
if __name__ == "__main__":
    import uvicorn

    # Ejecuta la aplicación localmente con Uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)