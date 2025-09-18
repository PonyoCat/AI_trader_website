from __future__ import annotations
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

# Importér dine routers
from app.routers.authentication import router as auth_router
from app.routers.portfolio import router as portfolio_router
from app.routers.orders import router as trade_router
from app.routers.ai import router as ai_router  # hvis du har AI-routeren aktiv

app = FastAPI(title="AI Trader API")

origins = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Valgfrit: send root til docs
@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse("/docs")

# Registrér routers (bemærk: ingen ekstra prefix her, hvis routeren selv har prefix)
app.include_router(auth_router)       # auth_router definerer allerede /auth/* i filen
app.include_router(portfolio_router)  # giver /positions og /orders/open
app.include_router(trade_router)      # trade_router har prefix="/trade"
app.include_router(ai_router)         # ai_router har prefix="/ai"
