from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Hello World! I'm CP, your predictive pricing assistant."}
