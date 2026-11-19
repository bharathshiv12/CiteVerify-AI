import sys
import os

sys.path.insert(0, "backend")

from app.core.config import settings
from app.repositories.supabase_repo import SupabaseRepository
import asyncio

async def main():
    print(f"REPOSITORY_BACKEND: {settings.REPOSITORY_BACKEND}")
    print(f"STORAGE_BACKEND: {settings.STORAGE_BACKEND}")
    print(f"SUPABASE_STORAGE_BUCKET: {settings.SUPABASE_STORAGE_BUCKET}")
    print(f"is_supabase_configured: {settings.is_supabase_configured}")

    repo = SupabaseRepository()
    is_ready, msg = await repo.check_connection()
    print(f"check_connection(): ready={is_ready}, msg='{msg}'")

    if is_ready:
        print("\nTesting queries on all 12 tables:")
        tables = [
            "profiles", "documents", "claims", "citations", "claim_citations",
            "research_papers", "evidence", "verifications", "human_reviews",
            "reports", "processing_jobs", "user_settings", "activity_log"
        ]
        for tbl in tables:
            try:
                res = repo.client.table(tbl).select("*").limit(1).execute()
                print(f"  Table '{tbl}': OK (rows: {len(res.data)})")
            except Exception as e:
                print(f"  Table '{tbl}': FAILED ({e})")

if __name__ == "__main__":
    asyncio.run(main())
