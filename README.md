# Bitespeed Identity Resolution API

This project implements a backend service to resolve contact identities based on shared `email` and `phoneNumber`. It was created as a solution to the Bitespeed Backend Task.

## 🚀 Tech Stack

- **Framework**: FastAPI
- **Database**: MySQL
- **ORM**: Raw SQL (MySQL Connector)
- **Environment Management**: python-dotenv

---

## 📬 Problem Statement

You're given a table that stores customer contact information (email, phone number). Multiple entries may exist for the same user. You need to:

- Identify if a given contact is new or already exists.
- Merge contacts into a unified identity.
- Track primary and secondary contacts.

### Endpoint

#### `POST /identify`

**Request Body:**

```json
{
  "email": "john@example.com",
  "phoneNumber": "1234567890"
}
```

### Response Format

```json
{
  "contact": {
    "primaryContatctId": 1,
    "emails": ["john@example.com"],
    "phoneNumbers": ["1234567890"],
    "secondaryContactIds": [2, 3]
  }
}
```

### 🛠 How to Run Locally
Clone the repo:

```
git clone https://github.com/your-username/Bitespeed_Backend.git
cd Bitespeed_Backend
```
Set up .env:
```
DB_HOST=your_db_host
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_NAME=your_db_name
```

Install dependencies:
```
pip install -r requirements.txt
```

Start the server:
```
uvicorn app:app --reload
```
