import modal

image = modal.Image.debian_slim().pip_install(
    "youtube_transcript_api", "weaviate-client", "google-api-python-client"
)

stub = modal.Stub("test-weaviate")


@stub.function(
    image=image,
    mounts=[
        modal.Mount.from_local_dir("classes"),
        modal.Mount.from_local_python_packages("WeaviateLink"),
    ],
)
def run():
    from WeaviateLink import VectorDB

    print("test")
    db = VectorDB("http://44.209.9.231:8080")
    print(db.add_playlist("6E9WU9TGrec"))


# @stub.local_entrypoint()
# def main():
