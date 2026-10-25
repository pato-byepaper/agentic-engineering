# Backend Developer: API & Domain Design Checklist

This reference defines engineering standards for robust, scalable, and secure backend APIs.

---

## 1. RESTful Conventions & HTTP Semantics

- **Standard Status Codes**:
  - `200 OK`: Successful retrieval or synchronous update.
  - `201 Created`: Successful resource creation (include `Location` header or resource representation).
  - `204 No Content`: Successful action with no body returned (e.g., DELETE).
  - `400 Bad Request`: Malformed syntax, invalid parameters.
  - `401 Unauthorized`: Missing or invalid authentication token.
  - `403 Forbidden`: Authenticated, but lacking permission/role.
  - `404 Not Found`: Resource does not exist (or concealed for security).
  - `422 Unprocessable Entity`: Syntactically valid request failing business validation rules.
  - `500 Internal Server Error`: Unhandled crash (log stack trace internally, return clean error to client).

---

## 2. Standardized Error Response Format

Always return consistent, machine-readable JSON errors:

```json
{
  "error": {
    "code": "INVALID_DISCOUNT_CODE",
    "message": "The provided promo code 'FOO' is expired or invalid.",
    "field": "discount_code",
    "details": []
  }
}
```

---

## 3. Security & Validation

- [ ] **Input Validation**: Validate every input at the boundary (DTO / schema validator like Pydantic, Zod, or Joi). Never pass raw user input into domain services or SQL queries.
- [ ] **Authentication & Authorization**: Verify permissions explicitly before executing business logic.
- [ ] **Rate Limiting & DoS Protection**: Enforce rate limits on resource-intensive and public endpoints.
- [ ] **Idempotency**: Use `Idempotency-Key` headers for payment or critical mutation endpoints.

---

## 4. Test-Driven Development (TDD) Workflow

1. Write unit tests for domain business logic covering:
   - Happy path.
   - Boundary/edge cases (nulls, empty collections, zero values, negative values).
   - Expected error conditions and status codes.
2. Run test and verify it fails with the expected failure message.
3. Implement minimal code to satisfy the test.
4. Run the entire test suite and verify all tests pass.
