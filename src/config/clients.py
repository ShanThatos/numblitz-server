import os
from typing import Annotated

from fastapi import Depends
from supabase import Client, create_client
from supabase.client import AsyncClient, create_async_client

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_KEY")

def create_supabase_client() -> Client:
    return create_client(url, key)

async def create_supabase_async_client() -> AsyncClient:
    return await create_async_client(url, key)

SupabaseClientDep = Annotated[Client, Depends(create_supabase_client)]
SupabaseAsyncClientDep = Annotated[AsyncClient, Depends(create_supabase_async_client)]
