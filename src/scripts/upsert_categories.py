import json

from config.clients import create_supabase_client


def upsert_categories():
    CATEGORIES = json.load(open("assets/categories.json"))
    CATEGORIES = [{**category, "order": i} for i, category in enumerate(CATEGORIES)]
    supabase = create_supabase_client()
    response = supabase.table("mathgen_categories").upsert(CATEGORIES, on_conflict="name").execute()
    print(response)

if __name__ == "__main__":
    upsert_categories()