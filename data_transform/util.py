synonyms = {"machine learning for test": "machine learning",
            "machine learning (ml)": "machine learning",
            "machine learning for health": "machine learning for sports and health analytics"
            }


def find_synonym(input: str):
    if input in synonyms.keys():
        return synonyms[input]