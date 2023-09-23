from fastapi import FastAPI
import models
from database import engine
from routers import user, userauth, provider, providerauth
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
# from mangum import Mangum

load_dotenv()
app = FastAPI()
# handler = Mangum(app)


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


models.Base.metadata.create_all(bind=engine)

app.include_router(user.router)
app.include_router(userauth.router)

app.include_router(provider.router)
app.include_router(providerauth.router)




@app.get("/")
async def root():
    return {"message": "Hello World"}
