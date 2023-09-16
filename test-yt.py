import modal

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
    ],
)
def run():
    from WeaviateLink import VectorDB
    import os

    for root, dirs, files in os.walk("/"):
        for d in dirs:
            if d.startswith("classes"):
                print(d)
                print(os.listdir(os.path.join(root, d)))

    print("test")
    db = VectorDB("http://44.209.9.231:8080")
    print(db.add_playlist("6E9WU9TGrec"))


# @stub.local_entrypoint()
# def main():
