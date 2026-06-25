from fastapi import FastAPI

from app.database import Base, engine
from app import models  # noqa: F401 — registers all models with Base.metadata
#alle die in der Init unter all stehen

from app.routers import cases, calls, messages, agents, location, addresses


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Patient-Sim Backend")


#Erlaubt die Connection ziwschen Frontend auf Port 5173 (vite) und 3000 (Vue), vite kann eigentlich raus wenn nicht benutzt
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    # localhost UND 127.0.0.1 auf beliebigem Port (Dev) – deckt 5173/5174/127.0.0.1 ab
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


app.include_router(cases.router)
app.include_router(calls.router)
app.include_router(messages.router)
app.include_router(agents.router)

app.include_router(location.router)

app.include_router(addresses.router)

@app.get("/")
def root() -> dict:
    return {"status": "ok"}


