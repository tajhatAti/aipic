"""
Core Initialization - Runs early to set global config + Supabase
"""

import os
from plugins.core.command_handler import set_owner
from plugins.core.supabase_client import get_supabase

def setup(bot, userbot):
    """Initialize global settings"""
    owner_id = os.environ.get("OWNER_ID")
    if owner_id:
        try:
            set_owner(int(owner_id))
            print(f"[AIPIC] Owner ID loaded: {owner_id}")
        except ValueError:
            print("[AIPIC] Invalid OWNER_ID in environment")

    # Connect to Supabase early
    sb = get_supabase()
    if sb:
        print("[AIPIC] Supabase ready for group admin storage")

register = setup
