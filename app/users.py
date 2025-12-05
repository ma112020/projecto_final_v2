# Serviço Utilizador

from fastapi import FastAPI, HTTPException, Path
# from fastapi.responses import JSONResponse
from typing import Dict, Any

# Setup de monitorização com opentelemetry
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export import ConsoleSpanExporter
# pyright: ignore[reportMissingImports]


# Configure Tracer Provider (Service Name is key for tracing)
resource = Resource.create({"service.name": "user-service"})
provider = TracerProvider(resource=resource)
provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))

app = FastAPI()
FastAPIInstrumentor.instrument_app(app, tracer_provider=provider)

# Base de dados de Utilizador
USERS_DB: Dict[int, Dict[str, Any]] = {
    1: {"id": 1, "username": "alice", "role": "admin"},
    2: {"id": 2, "username": "bob", "role": "editor"},
    3: {"id": 3, "username": "charlie", "role": "viewer"},
}

# Verificação de serviço ativo


@app.get('/')
def index():
    return {"message": "User Service is running."}

# Verificação da informação user_id:


@app.get('/user/profile/{user_id}')
def get_user_profile(

    user_id: int = Path(..., title="O ID do utilizador a obter", ge=1)
):
    user = USERS_DB.get(user_id)
    if user is None:
        raise HTTPException(status_code=404,
                            detail=f"User with ID {user_id} not found")

    return user

# Verificação da informação user_status


@app.get('/user/status')
def get_user_status():
    return {"status": "User DB healthy"}
