import json

from config.clients import supabase


def upsert_categories():
    CATEGORIES = json.load(open("assets/categories.json"))
    CATEGORIES = [{**category, "order": i} for i, category in enumerate(CATEGORIES)]
    response = supabase.table("mathgen_categories").upsert(CATEGORIES, on_conflict="name").execute()
    print(response)

if __name__ == "__main__":
    upsert_categories()