import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, date
import json


SUPABASE_URL = "https://ggdnrhrwgyezzccrcwyq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdnZG5yaHJ3Z3llenpjY3Jjd3lxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQwMDUxMDQsImV4cCI6MjA4OTU4MTEwNH0.4W6scrIGIJl56y4NN7MI2iHBx5Q-ZmlViottew91iLc"


def get_client():
    from supabase import create_client

    return create_client(SUPABASE_URL, SUPABASE_KEY)


def save_alert(email, role, location, frequency="daily"):
    try:
        client = get_client()
        client.table("job_alerts").upsert(
            {
                "email": email,
                "role": role,
                "location": location,
                "frequency": frequency,
                "active": True,
                "created_at": datetime.now().isoformat(),
            }
        ).execute()
        return True
    except Exception as e:
        print(f"Alert save error: {e}")
        return False


def get_user_alerts(email):
    try:
        client = get_client()
        return (
            client.table("job_alerts")
            .select("*")
            .eq("email", email)
            .eq("active", True)
            .execute()
            .data
        )
    except Exception:
        return []


def delete_alert(alert_id):
    try:
        client = get_client()
        client.table("job_alerts").update({"active": False}).eq("id", alert_id).execute()
        return True
    except Exception:
        return False


def send_job_alert_email(to_email, jobs, role, location, gmail, gmail_pass):
    try:
        msg = MIMEMultipart()
        msg["From"] = gmail
        msg["To"] = to_email
        msg["Subject"] = f"🎯 {len(jobs)} New Jobs: {role} in {location}"

        job_lines = ""
        for job in jobs[:5]:
            job_lines += f"""
 - {job['title']} at {job['company']} 
   📍 {job['location']} | Score: {job.get('score',0)}/100 
   🔗 {job.get('url','N/A')} 
"""

        body = f"""Hi there, 

 We found {len(jobs)} new matching jobs for "{role}" in {location}: 

 {job_lines} 

 Login to Job Hunt Assistant to view all jobs, generate tailored CVs and apply: 
 https://job-hunt-assistant-public.streamlit.app 

 Happy job hunting! 🎯 
 Job Hunt Assistant Team"""

        msg.attach(MIMEText(body, "plain"))
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail, gmail_pass)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Alert email error: {e}")
        return False


if __name__ == "__main__":
    print("Alerts engine ready ✓")

