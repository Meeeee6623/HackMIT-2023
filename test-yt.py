import modal
from modal import Image, Mount, Stub, asgi_app, gpu, method
from pathlib import Path
from pydantic import BaseModel


image = modal.Image.debian_slim().pip_install(
    "youtube_transcript_api", "weaviate-client", "google-api-python-client"
)

stub = modal.Stub("test-weaviate")


@stub.function(
    image=image,
    mounts=[
        modal.Mount.from_local_dir(
            "classes",
            remote_path="/classes",
        ),
        modal.Mount.from_local_python_packages("WeaviateLink"),
        modal.Mount.from_local_dir(
            "frontend",
            remote_path="/root/frontend",
        ),
    ],
)
@asgi_app()
def app():
    frontend_path = Path(__file__).parent / "frontend"

    import fastapi.staticfiles
    from fastapi import FastAPI

    web_app = FastAPI()

    @web_app.get("/train/{playlist}")
    async def train_chatbot(playlist: str):
        # Call the function to train the chatbot using Modal here
        # For now, just a mock response
        return {"message": f"Training started with {playlist}"}

    @web_app.get("/chat/{query}")
    async def chat(query: str):
        # Send the message to the trained chatbot and get the reply
        # For now, just a mock response
        reply = f"Chatbot's response to {query}"
        return {"reply": reply}

    @web_app.get("/infer/{prompt}")
    async def infer(prompt: str):
        return {f"message": "{prompt}"}

    web_app.mount(
        "/", fastapi.staticfiles.StaticFiles(directory=str(frontend_path), html=True)
    )
    return web_app
