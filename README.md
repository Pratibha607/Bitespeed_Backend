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
