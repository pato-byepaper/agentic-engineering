# API Endpoint Specification: <Endpoint Name>

- **Method**: `[GET | POST | PUT | PATCH | DELETE]`
- **Route**: `/api/v1/<resource>`
- **Auth Required**: Yes (`Bearer <token>`) | No
- **Rate Limit**: 60 req/min

---

## 1. Description
Brief overview of what this endpoint does and expected consumer.

## 2. Request Parameters / Body

### Headers
| Header | Type | Description |
| :--- | :--- | :--- |
| `Authorization` | string | Bearer token |
| `Content-Type` | string | `application/json` |

### JSON Body Example
```json
{
  "name": "Example Item",
  "quantity": 2
}
```

---

## 3. Responses

### `200 OK` / `201 Created`
```json
{
  "id": "item_123",
  "name": "Example Item",
  "quantity": 2,
  "createdAt": "2026-10-24T20:00:00Z"
}
```

### `400 Bad Request` / `422 Unprocessable`
```json
{
  "error": {
    "code": "INVALID_PAYLOAD",
    "message": "Field 'quantity' must be greater than zero."
  }
}
```
