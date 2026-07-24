"""
Supabase Client for storing managed groups + admins
Table needed in Supabase (SQL Editor):

create table if not exists managed_groups (
    chat_id bigint primary key,
    title text,
    admins jsonb default '[]'::jsonb,
    is_active boolean default true,
    updated_at timestamptz default now()
);

create index if not exists idx_managed_groups_active on managed_groups(is_active);
"""
import os
import json
from supabase import create_client, Client

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

supabase: Client = None

def get_supabase() -> Client:
    global supabase
    if supabase is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            print("⚠️ SUPABASE_URL or SUPABASE_KEY not set. DB features disabled.")
            return None
        try:
            supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
            print("✅ Supabase connected")
        except Exception as e:
            print(f"❌ Supabase connection failed: {e}")
            return None
    return supabase

def save_managed_group(chat_id: int, title: str, admin_ids: list):
    """Save or update a group where our userbot is admin."""
    sb = get_supabase()
    if not sb:
        return False
    
    try:
        data = {
            "chat_id": chat_id,
            "title": title or str(chat_id),
            "admins": admin_ids,
            "is_active": True,
            "updated_at": "now()"
        }
        # upsert
        sb.table("managed_groups").upsert(data).execute()
        print(f"📌 Saved managed group: {title} ({chat_id}) with {len(admin_ids)} admins")
        return True
    except Exception as e:
        print(f"Supabase save error: {e}")
        return False

def get_group_admins(chat_id: int) -> list:
    """Return list of admin user_ids for this group."""
    sb = get_supabase()
    if not sb:
        return []
    try:
        res = sb.table("managed_groups").select("admins").eq("chat_id", chat_id).eq("is_active", True).limit(1).execute()
        if res.data:
            return res.data[0].get("admins", []) or []
    except Exception as e:
        print(f"Supabase get admins error: {e}")
    return []

def is_group_admin(chat_id: int, user_id: int) -> bool:
    """Check if user is admin in this managed group."""
    admins = get_group_admins(chat_id)
    return user_id in admins

def get_all_managed_groups() -> list:
    sb = get_supabase()
    if not sb:
        return []
    try:
        res = sb.table("managed_groups").select("*").eq("is_active", True).execute()
        return res.data or []
    except:
        return []

def remove_managed_group(chat_id: int):
    sb = get_supabase()
    if not sb:
        return
    try:
        sb.table("managed_groups").update({"is_active": False}).eq("chat_id", chat_id).execute()
    except:
        pass
