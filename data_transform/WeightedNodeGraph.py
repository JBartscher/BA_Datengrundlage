import pickle
from typing import List, Dict

from persistence import get_documents_from_firestore


def get_docs() -> List[Dict]:
    all_documents = []
    try:
        all_documents = pickle.load(open("save_documents.p", "rb"))
        print("loaded from pickled obj")
    except FileNotFoundError as e:
        firestore_generator = get_documents_from_firestore("journal-citations")
        for count, document in enumerate(firestore_generator):
            all_documents.append(document.get().to_dict())
            print(count)
        print("loaded from firestore")
        pickle.dump(all_documents, open("save_documents.p", "wb"))
    except EOFError as e:
        print("eehhh")

    return all_documents


def reduce_keys(dictonary: Dict) -> Dict:
    x = {'keywords': [], 'year': None}
    keywords = dictonary.get('keywords', "No Keywords")
    x['keywords'] = purify_keywords(keywords)
    year = dictonary.get('year', -1)
    x['year'] = year
    return x


def purify_keywords(keyword_str: str) -> List[str]:
    splitted = map(str.strip, keyword_str.split(','))
    lowerd = map(str.lower, splitted)
    return list(lowerd)


if __name__ == '__main__':
    docs = get_docs()
    new_docs = []
    counter = 0
    all_keywords = []
    for d in docs:
        dic = reduce_keys(d)
        keywords = dic.get('keywords')
        counter = counter + len(keywords)
        all_keywords.extend(keywords)
        new_docs.append(dic)

    print("yoo")

    print(len(all_keywords))
    print(len(set(all_keywords)))
