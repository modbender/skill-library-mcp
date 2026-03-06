# Vue 3 Modernization

## Composition API

```vue
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

// Reactive state
const count = ref(0)
const users = ref<User[]>([])

// Computed
const doubleCount = computed(() => count.value * 2)

// Methods
function increment() {
  count.value++
}

// Lifecycle
onMounted(async () => {
  users.value = await fetchUsers()
})
</script>

<template>
  <div>
    <p>Count: {{ count }}</p>
    <p>Double: {{ doubleCount }}</p>
    <button @click="increment">Add</button>
  </div>
</template>
```

## State Management (Pinia)

```typescript
// stores/user.ts
import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
  state: () => ({
    user: null as User | null,
    isAuthenticated: false,
  }),
  
  getters: {
    userName: (state) => state.user?.name ?? 'Guest',
  },
  
  actions: {
    async login(credentials: Credentials) {
      const user = await api.login(credentials)
      this.user = user
      this.isAuthenticated = true
    },
    
    logout() {
      this.user = null
      this.isAuthenticated = false
    },
  },
})
```

## Component Architecture

```
components/
├── Base/          # Button, Input, Card
├── Layout/        # Header, Sidebar, Footer
├── Features/      # Feature-specific components
└── Shared/        # Reusable across features
```

## Checklist

- [ ] Migrate to Composition API
- [ ] Set up Pinia for state
- [ ] Implement composables
- [ ] Add TypeScript
- [ ] Set up Vue Router
- [ ] Implement code splitting
