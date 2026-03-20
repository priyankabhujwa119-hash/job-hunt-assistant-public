import json
from datetime import datetime
from supabase import create_client

SUPABASE_URL = "https://ggdnrhrwgyezzccrcwyq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdnZG5yaHJ3Z3llenpjY3Jjd3lxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQwMDUxMDQsImV4cCI6MjA4OTU4MTEwNH0.4W6scrIGIJl56y4NN7MI2iHBx5Q-ZmlViottew91iLc"

def get_client():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def track_signup(profile):
    try:
        client = get_client()
        client.table('users').upsert({
            'email': profile.get('email',''),
            'name': profile.get('name',''),
            'location': profile.get('location',''),
            'target_roles': json.dumps(profile.get('target_roles',[])),
            'target_markets': json.dumps(profile.get('target_markets',[])),
            'years_experience': int(profile.get('years_experience',0)),
            'setup_completed': True,
            'onboarding_step_reached': 4
        }).execute()
        track_event(profile.get('email',''), 'signup', {'name': profile.get('name','')})
        print("Signup tracked successfully")
    except Exception as e:
        print(f"Tracking error: {e}")

def track_event(user_email, event_type, metadata=None):
    try:
        client = get_client()
        client.table('events').insert({
            'user_email': user_email,
            'event_type': event_type,
            'metadata': json.dumps(metadata or {}),
            'created_at': datetime.now().isoformat()
        }).execute()
    except Exception as e:
        print(f"Event tracking error: {e}")

def get_all_users():
    try:
        client = get_client()
        return client.table('users').select('*').order('created_at', desc=True).execute().data
    except Exception as e:
        print(f"Error: {e}")
        return []

def get_all_events():
    try:
        client = get_client()
        return client.table('events').select('*').order('created_at', desc=True).execute().data
    except Exception as e:
        return []

def get_event_counts():
    try:
        client = get_client()
        events = client.table('events').select('event_type').execute().data
        counts = {}
        for e in events:
            t = e['event_type']
            counts[t] = counts.get(t, 0) + 1
        return counts
    except Exception as e:
        return {}
