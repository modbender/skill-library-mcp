# Pattern: Search

## Problem / Context

Search interfaces require debounced input handling, loading states during server requests, and clear result presentation. Poor implementation leads to excessive API calls and janky UX.

## When to Use

- Global search across content
- Filter panels with search
- Real-time suggestions (autocomplete)
- Search within large datasets

## When NOT to Use

- Small static lists (client-side filter)
- Simple select dropdowns
- Exact-match lookups

## AntD Components Involved

- `Input.Search` - Search input with button
- `AutoComplete` - Suggestions dropdown
- `List` / `Table` - Results display
- `Empty` - No results state
- `Spin` - Loading indicator

## React Implementation Notes

### Debounced Search Pattern

```tsx
import { useDebounce } from 'use-debounce';

const [query, setQuery] = useState('');
const [debouncedQuery] = useDebounce(query, 300);
const [results, setResults] = useState([]);
const [loading, setLoading] = useState(false);

useEffect(() => {
  if (!debouncedQuery) {
    setResults([]);
    return;
  }
  
  setLoading(true);
  api.search(debouncedQuery)
    .then(setResults)
    .finally(() => setLoading(false));
}, [debouncedQuery]);
```

### Search Input Component

```tsx
<Input.Search
  placeholder="Search users..."
  value={query}
  onChange={(e) => setQuery(e.target.value)}
  onSearch={setQuery}
  loading={loading}
  allowClear
  enterButton
/>
```

### Results Display

```tsx
{loading && <Spin />}

{!loading && results.length === 0 && debouncedQuery && (
  <Empty description={`No results for "${debouncedQuery}"`} />
)}

{!loading && results.length > 0 && (
  <List
    dataSource={results}
    renderItem={(item) => (
      <List.Item>
        <List.Item.Meta
          title={item.name}
          description={item.description}
        />
      </List.Item>
    )}
  />
)}
```

### Autocomplete Pattern

```tsx
const [options, setOptions] = useState([]);

const handleSearch = async (value: string) => {
  const results = await api.suggest(value);
  setOptions(results.map(r => ({ value: r.id, label: r.name })));
};

<AutoComplete
  options={options}
  onSearch={handleSearch}
  onSelect={(value) => navigate(`/items/${value}`)}
  placeholder="Search..."
/>
```

## Accessibility / Keyboard

- Search input has proper `role="search"`
- Results are announced via aria-live
- Keyboard navigation through suggestions
- Clear focus indicators

## Do / Don't

**Do:**
- Debounce input (300ms typical)
- Show loading state immediately
- Allow clearing search
- Persist recent searches

**Don't:**
- Search on every keystroke
- Show "no results" before user stops typing
- Require exact matches
- Forget empty state

## Minimal Code Snippet

```tsx
import { Input, List, Empty, Spin } from 'antd';
import { useState, useEffect } from 'react';
import { useDebounce } from 'use-debounce';

function SearchComponent() {
  const [query, setQuery] = useState('');
  const [debouncedQuery] = useDebounce(query, 300);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!debouncedQuery) return;
    setLoading(true);
    fetch(`/api/search?q=${debouncedQuery}`)
      .then(r => r.json())
      .then(data => {
        setResults(data);
        setLoading(false);
      });
  }, [debouncedQuery]);

  return (
    <div>
      <Input.Search
        placeholder="Search..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        loading={loading}
        allowClear
      />
      {loading && <Spin style={{ marginTop: 16 }} />}
      {!loading && results.length > 0 && (
        <List
          dataSource={results}
          renderItem={(item) => <List.Item>{item.name}</List.Item>}
        />
      )}
      {!loading && query && results.length === 0 && (
        <Empty description="No results" />
      )}
    </div>
  );
}
```
