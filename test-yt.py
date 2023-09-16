import modal
from WeaviateLink import VectorDB
stub = modal.Stub("test-weaviate")


@stub.local_entrypoint()
def main():
    print('test')
    db = VectorDB("http://44.209.9.231:8080")
    print(db.add_playlist("6E9WU9TGrec"))
