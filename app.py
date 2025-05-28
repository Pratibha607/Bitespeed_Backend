from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# MySQL connection
db = mysql.connector.connect(
    host=os.getenv("NEWAWSENDPOINT"),
    user="admin",
    password=os.getenv("AWSPASSWORD"),
    database="bitespeeddb",
    port=3306
)
cursor = db.cursor(dictionary=True)

# Pydantic model for request
class IdentifyRequest(BaseModel):
    email: Optional[str]
    phoneNumber: Optional[str]

# Helper function to find all connected contacts recursively
def find_all_connected_contacts(email, phone):
    conditions = []
    values = []

    if email:
        conditions.append("email = %s")
        values.append(email)
    if phone:
        conditions.append("phoneNumber = %s")
        values.append(phone)

    where_clause = " OR ".join(conditions)
    query = f"SELECT * FROM Contact WHERE {where_clause} AND deletedAt IS NULL"
    cursor.execute(query, tuple(values))
    initial_results = cursor.fetchall()

    if not initial_results:
        return []

    all_contacts = {c["id"]: c for c in initial_results}
    queue = [c["id"] for c in initial_results]

    while queue:
        current_id = queue.pop(0)
        cursor.execute(
            "SELECT * FROM Contact WHERE (linkedId = %s OR id = %s) AND deletedAt IS NULL",
            (current_id, current_id)
        )
        new_contacts = cursor.fetchall()
        for contact in new_contacts:
            if contact["id"] not in all_contacts:
                all_contacts[contact["id"]] = contact
                queue.append(contact["id"])

    return list(all_contacts.values())

@app.post("/identify")
def identify(request: IdentifyRequest):
    email = request.email
    phone = request.phoneNumber
    now = datetime.now()

    if not email and not phone:
        raise HTTPException(status_code=400, detail="Either email or phoneNumber is required")

    all_contacts = find_all_connected_contacts(email, phone)

    if not all_contacts:
        # New user
        cursor.execute(
            """
            INSERT INTO Contact (email, phoneNumber, linkPrecedence, createdAt, updatedAt)
            VALUES (%s, %s, 'primary', %s, %s)
            """,
            (email, phone, now, now)
        )
        db.commit()
        new_id = cursor.lastrowid
        return {
            "contact": {
                "primaryContatctId": new_id,
                "emails": [email] if email else [],
                "phoneNumbers": [phone] if phone else [],
                "secondaryContactIds": []
            }
        }

    # Sort to find primary
    all_contacts.sort(key=lambda x: x["createdAt"])
    primary_contact = next((c for c in all_contacts if c["linkPrecedence"] == "primary"), all_contacts[0])
    primary_id = primary_contact["id"]

    # Merge required?
    existing_emails = {c["email"] for c in all_contacts if c["email"]}
    existing_phones = {c["phoneNumber"] for c in all_contacts if c["phoneNumber"]}
    new_info = False

    if email and email not in existing_emails:
        new_info = True
    if phone and phone not in existing_phones:
        new_info = True

    if new_info:
        cursor.execute(
            """
            INSERT INTO Contact (email, phoneNumber, linkedId, linkPrecedence, createdAt, updatedAt)
            VALUES (%s, %s, %s, 'secondary', %s, %s)
            """,
            (email, phone, primary_id, now, now)
        )
        db.commit()
        new_contact = {
            "id": cursor.lastrowid,
            "email": email,
            "phoneNumber": phone,
            "linkedId": primary_id,
            "linkPrecedence": "secondary",
            "createdAt": now,
            "updatedAt": now
        }
        all_contacts.append(new_contact)

    # Rebuild the consolidated response
    emails = []
    phoneNumbers = []
    secondaryContactIds = []

    for c in all_contacts:
        if c["linkPrecedence"] == "primary" and c["id"] == primary_id:
            if c["email"]: emails.insert(0, c["email"])
            if c["phoneNumber"]: phoneNumbers.insert(0, c["phoneNumber"])
        else:
            if c["email"] and c["email"] not in emails: emails.append(c["email"])
            if c["phoneNumber"] and c["phoneNumber"] not in phoneNumbers: phoneNumbers.append(c["phoneNumber"])
            if c["id"] != primary_id:
                secondaryContactIds.append(c["id"])

    return {
        "contact": {
            "primaryContatctId": primary_id,
            "emails": emails,
            "phoneNumbers": phoneNumbers,
            "secondaryContactIds": secondaryContactIds
        }
    }
