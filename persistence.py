import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import pytz


class FirestoreClientSingleton:
    CRED_PATH = "./serviceAccountKey.json"
    __cred = credentials.Certificate(CRED_PATH)
    __app = firebase_admin.initialize_app(__cred)

    __client = None

    @staticmethod
    def get_client():
        if FirestoreClientSingleton.__client is None:
            FirestoreClientSingleton.__client = firestore.client(FirestoreClientSingleton.__app)
        return FirestoreClientSingleton.__client


# Add documents with auto Id
def add_document_to_firestore(data={}, collection="default_collection"):
    return FirestoreClientSingleton.get_client().collection(collection).add(data)


def set_document_to_firestore(key=None, data={}, collection="default_collection", merge=True):
    return FirestoreClientSingleton.get_client().collection(collection).document(key).set(data, merge=merge)


def get_documents_from_firestore(collection="default_collection"):
    return FirestoreClientSingleton.get_client().collection(collection).list_documents()


def add_crawl(cl, data):
    dt = datetime.now(pytz.utc)
    ts = datetime.timestamp(dt)
    crawl = FirestoreClientSingleton.get_client().collection('crawls').document(str(ts))  # DocumentReference
    crawl.set({'dt': dt}, merge=True)
    crawl.collection('entries').add(data)


if __name__ == '__main__':
    # client = FirestoreClientSingleton.get_client()
    # #  documents = get_documents_from_firestore(client)
    # # client.collection('collection').document('test').set({'path': 'test'}, merge=True)
    # add_crawl(client, {'journal': 'epsc', 'year': 1995})
    # # print(fstc.collections())
    set_document_to_firestore(key="key-id", data={"name":"thisisatest"}, collection="collection")
