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

## 4. Verification & Testing Separation Workflow

1. **STRICT INVARIANT**: Backend Developers NEVER write or run unit, integration, or E2E tests. Only the `tester` subagent writes and executes tests so that no developer can self-certify passing tests.
2. Verify static type safety and compilation only (e.g., `npx tsc --noEmit`).
3. In your handoff notes to the `tester`, clearly list:
   - Happy path payload examples and expected status codes.
   - Boundary/edge cases (nulls, empty collections, zero values, negative values) that the `tester` should target.
   - Expected error codes and validation failure scenarios.
