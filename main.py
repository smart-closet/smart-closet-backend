from fastapi import FastAPI
from routers import context, images

app = FastAPI()
app.include_router(context.router)
app.include_router(images.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
