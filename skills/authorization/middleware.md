# Framework Middleware — Authorization

## Express.js

```typescript
// middleware/authorize.ts
export function authorize(action: string) {
  return async (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({ error: 'Unauthenticated' });
    }

    // Get resource from request if needed
    const resource = req.resource || null;

    if (!await can(req.user, action, resource)) {
      return res.status(403).json({ 
        error: 'Forbidden',
        required: action 
      });
    }

    next();
  };
}

// Usage
app.delete('/documents/:id', 
  requireAuth,
  loadDocument, // Sets req.resource
  authorize('documents:delete'),
  deleteDocumentHandler
);
```

---

## NestJS

```typescript
// decorators/permissions.decorator.ts
export const RequirePermissions = (...permissions: string[]) =>
  SetMetadata('permissions', permissions);

// guards/authorization.guard.ts
@Injectable()
export class AuthorizationGuard implements CanActivate {
  constructor(
    private reflector: Reflector,
    private authService: AuthService,
  ) {}

  async canActivate(context: ExecutionContext): Promise<boolean> {
    const permissions = this.reflector.get<string[]>(
      'permissions',
      context.getHandler(),
    );
    
    if (!permissions) return true;

    const request = context.switchToHttp().getRequest();
    const user = request.user;

    for (const permission of permissions) {
      if (!await this.authService.can(user, permission)) {
        throw new ForbiddenException(`Missing permission: ${permission}`);
      }
    }

    return true;
  }
}

// Usage
@Controller('documents')
export class DocumentsController {
  @Delete(':id')
  @RequirePermissions('documents:delete')
  async delete(@Param('id') id: string) {
    // ...
  }
}
```

---

## Next.js (App Router)

```typescript
// lib/authorize.ts
export async function authorize(
  user: User | null,
  action: string,
  resource?: any
) {
  if (!user) {
    redirect('/login');
  }

  if (!await can(user, action, resource)) {
    notFound(); // Or throw custom error
  }
}

// app/documents/[id]/edit/page.tsx
export default async function EditDocument({ params }) {
  const session = await getServerSession();
  const document = await getDocument(params.id);
  
  await authorize(session?.user, 'documents:write', document);
  
  return <DocumentEditor document={document} />;
}

// API Routes
// app/api/documents/[id]/route.ts
export async function DELETE(request, { params }) {
  const session = await getServerSession();
  const document = await getDocument(params.id);
  
  if (!await can(session?.user, 'documents:delete', document)) {
    return Response.json({ error: 'Forbidden' }, { status: 403 });
  }
  
  await deleteDocument(params.id);
  return Response.json({ success: true });
}
```

---

## Laravel

```php
// Policies/DocumentPolicy.php
class DocumentPolicy
{
    public function delete(User $user, Document $document): bool
    {
        // Owner can delete
        if ($document->user_id === $user->id) {
            return true;
        }
        
        // Admin can delete
        if ($user->hasPermission('documents:delete:all')) {
            return true;
        }
        
        return false;
    }
}

// Controller
class DocumentController extends Controller
{
    public function destroy(Document $document)
    {
        $this->authorize('delete', $document);
        
        $document->delete();
        return response()->noContent();
    }
}

// Or inline
public function destroy(Document $document)
{
    if ($user->cannot('delete', $document)) {
        abort(403);
    }
    // ...
}
```

---

## Django

```python
# permissions.py
from rest_framework.permissions import BasePermission

class CanDeleteDocument(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Owner
        if obj.owner == request.user:
            return True
        
        # Admin
        if request.user.has_perm('documents.delete_any'):
            return True
            
        return False

# views.py
class DocumentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, CanDeleteDocument]
    
    def destroy(self, request, pk=None):
        document = self.get_object()  # Triggers permission check
        document.delete()
        return Response(status=204)
```

---

## Ruby on Rails (Pundit)

```ruby
# app/policies/document_policy.rb
class DocumentPolicy < ApplicationPolicy
  def destroy?
    # Owner
    record.user_id == user.id ||
    # Admin
    user.has_permission?('documents:delete:all')
  end
  
  class Scope < Scope
    def resolve
      if user.admin?
        scope.all
      else
        scope.where(user_id: user.id)
             .or(scope.where(team_id: user.team_ids))
      end
    end
  end
end

# app/controllers/documents_controller.rb
class DocumentsController < ApplicationController
  def destroy
    @document = Document.find(params[:id])
    authorize @document
    
    @document.destroy
    head :no_content
  end
  
  def index
    @documents = policy_scope(Document)
    render json: @documents
  end
end
```

---

## Common Middleware Pattern

All frameworks follow the same flow:

```
Request → Auth Middleware → Load Resource → Authorization Check → Handler
              ↓                   ↓                 ↓
         Set user on       Set resource on    Check can(user,
           request           request          action, resource)
```

**Key points:**
1. Auth first (who are you?)
2. Load resource (what are you accessing?)
3. Authorize (can you do this to it?)
4. Handle (execute the action)
