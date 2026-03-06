# Full-Stack Feature Template

## When to Use This Pattern

✅ **Use when:**
- Building a feature that spans frontend, backend, and tests
- Clear interface contract between layers (API spec, data models)
- Frontend and backend can work in parallel once contract is defined
- Want to accelerate delivery with parallel implementation

❌ **Don't use when:**
- Feature is frontend-only or backend-only
- API contract is unclear or likely to change frequently
- Tight coupling requires constant coordination
- Feature is exploratory (unclear requirements)

## Team Structure

**Lead:** Architect who defines contracts and coordinates integration
**Teammates:** 3 specialists
- **Frontend Engineer:** Builds UI components and API integration
- **Backend Engineer:** Implements API endpoints and business logic
- **Test Engineer:** Writes integration and unit tests for both layers

## File/Directory Boundaries

**Critical:** Clear boundaries prevent merge conflicts.

```
frontend/
  src/components/[feature]/    # Frontend engineer owns this
  src/services/[feature]-api.ts # Frontend engineer owns this

backend/
  src/controllers/[feature].ts  # Backend engineer owns this
  src/services/[feature].ts     # Backend engineer owns this
  src/models/[feature].ts       # Backend engineer owns this

tests/
  integration/[feature].test.ts # Test engineer owns this
  unit/[feature]-*.test.ts      # Test engineer owns this

docs/
  api-contract-[feature].md     # Lead creates, all read
```

## Spawn Prompt (Copy-Paste Ready)

```markdown
I need to build a full-stack feature: [FEATURE NAME - e.g., "User profile editing"]

**Requirements:**
- [REQUIREMENT 1 - e.g., "Users can edit name, email, bio"]
- [REQUIREMENT 2 - e.g., "Email must be unique and validated"]
- [REQUIREMENT 3 - e.g., "Profile photo upload (max 5MB)"]
- [SUCCESS CRITERIA - e.g., "Profile updates appear immediately on refresh"]

**Tech stack:**
- Frontend: [e.g., "React 18 + TypeScript + TailwindCSS"]
- Backend: [e.g., "FastAPI + Python 3.11 + PostgreSQL"]
- Testing: [e.g., "Playwright + pytest"]

First, I will define the API contract. Wait for my signal before teammates start implementation.

---

**[AFTER DEFINING CONTRACT]**

API contract is defined in `docs/api-contract-profile-edit.md`. Now spawn 3 teammates using Sonnet:

1. **Frontend Engineer**
   - Name: frontend-engineer
   - Owns: `frontend/src/components/profile/`, `frontend/src/services/profile-api.ts`
   - Output: Working React components + API integration
   - Tasks:
     * Implement ProfileEditForm component (name, email, bio inputs)
     * Add form validation (client-side)
     * Integrate with API via profile-api.ts service
     * Handle loading, success, error states
     * Add photo upload with preview
     * Style with TailwindCSS

2. **Backend Engineer**
   - Name: backend-engineer
   - Owns: `backend/src/controllers/profile.ts`, `backend/src/services/profile.ts`, `backend/src/models/profile.ts`
   - Output: Working API endpoint + business logic
   - Tasks:
     * Implement PUT /api/profile endpoint
     * Add validation (email format, uniqueness)
     * Implement photo upload to S3 with size validation (max 5MB)
     * Update database with new profile data
     * Return updated profile JSON
     * Add error handling (400, 409, 500)

3. **Test Engineer**
   - Name: test-engineer
   - Owns: `tests/integration/profile-edit.test.ts`, `tests/unit/profile-*.test.ts`
   - Output: Comprehensive test suite
   - Tasks:
     * Write integration test: full flow (form submit → API → database → UI update)
     * Write unit tests for frontend: form validation logic
     * Write unit tests for backend: email uniqueness check, photo upload validation
     * Test error cases: invalid email, duplicate email, oversized photo
     * Verify success message displays correctly

**Coordination rules:**
- Use delegate mode: I define contracts and coordinate, teammates implement
- Frontend reads API contract (doesn't modify it)
- Backend implements API contract exactly as specified
- Test engineer verifies contract is implemented correctly
- No cross-boundary edits (frontend doesn't touch backend files)
- Teammates can ask clarifying questions about contract via messages

**Integration checkpoint:**
After all teammates finish:
1. Run integration tests (test engineer's suite)
2. If tests pass → feature complete
3. If tests fail → debug integration issues together

**Boundaries to prevent conflicts:**
- Frontend engineer: Only edit files under `frontend/src/components/profile/` and `frontend/src/services/profile-api.ts`
- Backend engineer: Only edit files under `backend/src/controllers/profile.ts`, `backend/src/services/profile.ts`, `backend/src/models/profile.ts`
- Test engineer: Only edit files under `tests/`
- Nobody edits API contract after teammates start (lead created it upfront)
```

## Expected Outcomes

### 1. API Contract (Lead creates first)

**docs/api-contract-profile-edit.md:**
```markdown
# Profile Edit API Contract

## Endpoint
PUT /api/profile

## Request

### Headers
```
Authorization: Bearer {jwt_token}
Content-Type: multipart/form-data (if photo included) or application/json
```

### Body (JSON or multipart)
```json
{
  "name": "string (1-100 chars, required)",
  "email": "string (valid email format, required)",
  "bio": "string (0-500 chars, optional)",
  "photo": "file (image/jpeg or image/png, max 5MB, optional)"
}
```

## Response

### Success (200)
```json
{
  "id": "uuid",
  "name": "string",
  "email": "string",
  "bio": "string",
  "photo_url": "string (S3 URL)",
  "updated_at": "ISO 8601 timestamp"
}
```

### Validation Error (400)
```json
{
  "error": "validation_error",
  "details": {
    "email": ["Invalid email format"],
    "photo": ["File size exceeds 5MB"]
  }
}
```

### Conflict (409)
```json
{
  "error": "conflict",
  "message": "Email already in use"
}
```

### Server Error (500)
```json
{
  "error": "internal_server_error",
  "message": "Failed to upload photo"
}
```

## Validation Rules
- Name: 1-100 characters, required
- Email: Valid format (RFC 5322), unique in database, required
- Bio: 0-500 characters, optional
- Photo: image/jpeg or image/png, max 5MB, optional

## Business Logic
1. Validate input fields
2. Check email uniqueness (exclude current user)
3. Upload photo to S3 (if provided)
4. Update database
5. Return updated profile
```

### 2. Frontend Implementation

**frontend/src/components/profile/ProfileEditForm.tsx:**
```typescript
// Frontend engineer implements React component
// - Form with controlled inputs (name, email, bio)
// - Photo upload with preview
// - Client-side validation
// - API integration via profile-api.ts
// - Loading/success/error states
```

**frontend/src/services/profile-api.ts:**
```typescript
// API service layer
export async function updateProfile(data: ProfileUpdateData): Promise<Profile> {
  const formData = new FormData();
  formData.append('name', data.name);
  formData.append('email', data.email);
  if (data.bio) formData.append('bio', data.bio);
  if (data.photo) formData.append('photo', data.photo);

  const response = await fetch('/api/profile', {
    method: 'PUT',
    headers: { Authorization: `Bearer ${getToken()}` },
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new ProfileUpdateError(error);
  }

  return response.json();
}
```

### 3. Backend Implementation

**backend/src/controllers/profile.ts:**
```python
# Backend engineer implements FastAPI endpoint
@router.put("/api/profile")
async def update_profile(
    name: str = Form(...),
    email: EmailStr = Form(...),
    bio: Optional[str] = Form(None),
    photo: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user)
):
    # Validate photo size
    if photo and photo.size > 5 * 1024 * 1024:
        raise HTTPException(400, {"photo": ["File size exceeds 5MB"]})
    
    # Check email uniqueness
    if await user_service.email_exists(email, exclude=current_user.id):
        raise HTTPException(409, "Email already in use")
    
    # Upload photo to S3
    photo_url = await s3_service.upload(photo) if photo else current_user.photo_url
    
    # Update database
    updated_profile = await user_service.update_profile(
        current_user.id, name, email, bio, photo_url
    )
    
    return updated_profile
```

### 4. Test Implementation

**tests/integration/profile-edit.test.ts:**
```typescript
// Test engineer implements integration test
describe('Profile Edit Flow', () => {
  it('successfully updates profile with all fields', async () => {
    // 1. Login and navigate to profile edit page
    await page.goto('/profile/edit');
    
    // 2. Fill form
    await page.fill('[name="name"]', 'John Updated');
    await page.fill('[name="email"]', 'john.updated@example.com');
    await page.fill('[name="bio"]', 'New bio text');
    await page.setInputFiles('[name="photo"]', 'fixtures/test-photo.jpg');
    
    // 3. Submit
    await page.click('button[type="submit"]');
    
    // 4. Verify success message
    await expect(page.locator('.success-message')).toContainText('Profile updated');
    
    // 5. Verify database updated
    const profile = await db.users.findOne({ email: 'john.updated@example.com' });
    expect(profile.name).toBe('John Updated');
    expect(profile.bio).toBe('New bio text');
    expect(profile.photo_url).toMatch(/s3\.amazonaws\.com/);
  });
  
  it('shows error for duplicate email', async () => {
    // ... test conflict case
  });
  
  it('shows error for oversized photo', async () => {
    // ... test validation case
  });
});
```

## Timing

**Sequential implementation:** ~90-120 minutes (30-40 min per layer)
**Parallel implementation:** ~35-45 minutes (all layers simultaneously)

**Speedup:** ~2.5-3x faster

## Cost Estimate

**Team:** 1 Opus lead + 3 Sonnet specialists
**Duration:** ~40 minutes
**Estimated cost:** $20-30

## Integration Checklist

After teammates finish, lead verifies:

- [ ] Frontend compiles without errors
- [ ] Backend starts without errors
- [ ] Integration tests pass
- [ ] API contract matches implementation (request/response formats)
- [ ] Error handling works (400, 409, 500 cases)
- [ ] File boundaries respected (no cross-boundary edits)

## Common Integration Issues

### Issue: Request/response format mismatch
**Symptom:** Frontend sends `userName` but backend expects `name`
**Prevention:** Define contract first, both sides implement exactly as specified
**Fix:** Update implementation to match contract (don't change contract mid-stream)

### Issue: Merge conflicts
**Symptom:** Git conflicts when merging branches
**Prevention:** Strict file boundaries (frontend/backend/tests don't overlap)
**Fix:** Review boundaries, ensure each teammate owns distinct files

### Issue: Tests fail due to missing setup
**Symptom:** Integration tests fail because database or S3 mock not configured
**Prevention:** Test engineer documents required setup in test README
**Fix:** Add setup script or fixture data

## Success Metrics

✅ **Successful if:**
- All teammates complete within 45 minutes
- Integration tests pass on first run (or after minor fixes)
- No merge conflicts due to file boundary violations
- API contract was defined upfront and followed exactly
- Feature meets all requirements

❌ **Red flags:**
- Teammates editing same files (boundary violation)
- API contract changed after implementation started
- Integration tests not written until after implementation
- Lead implementing instead of coordinating

## Variations

### Two-Specialist Variant (Budget-Conscious)
- Frontend engineer writes frontend + frontend tests
- Backend engineer writes backend + backend tests
- Lead writes integration tests

**Cost savings:** ~30% less, but slower (less parallelization)

### Four-Specialist Variant (Complex Features)
Add:
- **Database Engineer:** Migrations, indexes, query optimization
- Use when feature requires significant database work

## Follow-Up Actions

After feature complete:
1. Manual QA (edge cases not covered by tests)
2. Code review (security, performance, style)
3. Deploy to staging
4. Smoke test in production-like environment
5. Merge to main
