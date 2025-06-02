import io
import pandas as pd
import smtplib
from email.message import EmailMessage

# Define the expected team members
EXPECTED_MEMBERS = ["Vivek","Sindhu","Ayan","Hritwij","Madivarman","Haindavi",]

def all_members_done(df):
    """
    Check if all expected team members have submitted their updates.
    """
    return all(member in df["Name"].unique().tolist() for member in EXPECTED_MEMBERS)

def send_email_with_excel(df, sender_email, sender_password, recipient_email):
    """
    Convert the dataframe to an Excel file and email it using Outlook SMTP.
    """
    try:
        # Create in-memory Excel file
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Team Status")
        excel_data = output.getvalue()

        # Create the email
        msg = EmailMessage()
        msg["Subject"] = "📊 Weekly Team Status Report"
        msg["From"] = sender_email
        msg["To"] = recipient_email
        msg.set_content(
            "Hi,\n\nAll 7 team members have submitted their updates."
            "\nPlease find the attached report.\n\nRegards,\nStreamlit Bot"
        )

        msg.add_attachment(
            excel_data,
            maintype="application",
            subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename="team_status.xlsx"
        )

        # Send the email via Outlook SMTP
        with smtplib.SMTP("smtp.office365.com", 587) as smtp:
            smtp.starttls()
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)

        return True

    except Exception as e:
        import streamlit as st
        st.error(f"❌ Failed to send email: {e}")
        return False
