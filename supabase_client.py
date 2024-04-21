from django.conf import settings
from supabase import create_client

sp = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
