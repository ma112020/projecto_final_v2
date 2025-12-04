# Serviço Produtos

import os
import requests
from fastapi import FastAPI, HTTPException, Path
# from fastapi.responses import JSONResponse
from typing import Dict, Any

# Setup OpenTelemetry (
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export import ConsoleSpanExporter

# Configuração de Ambiente
# É mais seguro usar variáveis de ambiente para chaves, mesmo que esta seja fictícia.
API_KEY = os.environ.get("CHAVE_FICTICIA")

# Configuração de Tracing
resource = Resource.create({"service.name": "product-service"})
provider = TracerProvider(resource=resource)
provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
RequestsInstrumentor().instrument(tracer_provider=provider)

app = FastAPI()
FastAPIInstrumentor.instrument_app(app, tracer_provider=provider)

# Hostname na porta 5001 (como definido em users.py and docker-compose)
USER_SERVICE_URL = 'http://users:5001'

# Dados do Produto (Mock Database)
PRODUCTS_DB: Dict[int, Dict[str, Any]] = {
    101: {"id": 101, "name": "Laptop", "price": 1200.00, "owner_id": 1},
    102: {"id": 102, "name": "Monitor", "price": 300.00, "owner_id": 2},
    103: {"id": 103, "name": "Keyboard", "price": 150.00, "owner_id": 1},
}

# Permite que o User Service pergunte: "Que produtos pertencem ao user X?"


@app.get('/products/by_user/{user_id}')
def get_products_by_user(
    user_id: int = Path(..., title="O ID do utilizador a obter", ge=1)
):
    user_products = []
    for p in PRODUCTS_DB.values():
        if p['owner_id'] == user_id:
            user_products.append(p)

    return user_products


# verificação health check
@app.get('/')
def root():
    return {"status": "Product Service Operational"}


# Pedido interno ao utilizador:
def get_user_data(user_id: int):
    try:
        # CORREÇÃO 1 (B113): Adicionar timeout de 5 segundos
        r = requests.get(f'{USER_SERVICE_URL}/user/profile/{user_id}', timeout=5)
        r.raise_for_status()

        return r.json()
    except requests.exceptions.RequestException:
        # Se o serviço de utilizadores falhar, não queremos expor o erro interno
        raise HTTPException(status_code=503, detail="User Service currently unavailable.")


# Pedido de informação de produto:
@app.get('/product/{product_id}')
def get_product_details(
    product_id: int = Path(..., title="O ID do produto a obter", ge=1)
):
    product = PRODUCTS_DB.get(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    owner_id = product.get('owner_id')
    user_info = get_user_data(owner_id)

    # Retornar o objeto diretamente
    return {
        "product": product,
        "owner_details": user_info
    }
