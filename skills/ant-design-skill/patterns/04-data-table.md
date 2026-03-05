# Pattern: Data Table

## Problem / Context

Data tables need to handle pagination, sorting, filtering, and row actions while maintaining performance and usability. Loading states and empty states must be handled gracefully.

## When to Use

- Listing large datasets
- Admin data management
- Report views with sortable columns
- Multi-select operations

## When NOT to Use

- Small datasets (< 10 items, use List)
- Complex hierarchical data (use Tree)
- Mobile-first designs (consider Cards)

## AntD Components Involved

- `Table` - Main data display
- `Pagination` - For large datasets
- `Tag` / `Badge` - Cell decorations
- `Dropdown` / `Button` - Row actions
- `Skeleton` / `Spin` - Loading states
- `Empty` - No data state

## React Implementation Notes

### Server-Side Data Fetching

```tsx
const [data, setData] = useState([]);
const [loading, setLoading] = useState(false);
const [pagination, setPagination] = useState({
  current: 1,
  pageSize: 10,
  total: 0,
});
const [filters, setFilters] = useState({});
const [sorter, setSorter] = useState({});

const fetchData = useCallback(async () => {
  setLoading(true);
  const result = await api.getData({
    page: pagination.current,
    pageSize: pagination.pageSize,
    ...filters,
    sortField: sorter.field,
    sortOrder: sorter.order,
  });
  setData(result.data);
  setPagination(prev => ({ ...prev, total: result.total }));
  setLoading(false);
}, [pagination.current, pagination.pageSize, filters, sorter]);

useEffect(() => { fetchData(); }, [fetchData]);
```

### Table Configuration

```tsx
const columns = [
  {
    title: 'Name',
    dataIndex: 'name',
    sorter: true,
    filters: [
      { text: 'Active', value: 'active' },
      { text: 'Inactive', value: 'inactive' },
    ],
  },
  {
    title: 'Status',
    dataIndex: 'status',
    render: (status) => (
      <Tag color={status === 'active' ? 'green' : 'red'}>
        {status}
      </Tag>
    ),
  },
  {
    title: 'Actions',
    key: 'actions',
    render: (_, record) => (
      <Space>
        <Button onClick={() => handleEdit(record)}>Edit</Button>
        <Button danger onClick={() => handleDelete(record)}>Delete</Button>
      </Space>
    ),
  },
];
```

### Row Selection

```tsx
const [selectedRows, setSelectedRows] = useState([]);

const rowSelection = {
  selectedRowKeys: selectedRows.map(r => r.id),
  onChange: (keys, rows) => setSelectedRows(rows),
};
```

## Accessibility / Keyboard

- Tables have proper `role="table"` semantics
- Sortable columns announce sort state
- Row actions are keyboard accessible
- Focus visible on interactive elements

## Do / Don't

**Do:**
- Use fixed columns for many fields
- Show loading overlay during data fetch
- Persist table state in URL query params
- Use appropriate column widths

**Don't:**
- Put too many columns (horizontal scroll is bad)
- Use tables for layout
- Fetch all data client-side for large sets
- Hide actions behind hover-only tooltips

## Minimal Code Snippet

```tsx
import { Table, Tag, Space, Button } from 'antd';
import { useState, useEffect } from 'react';

function UserTable() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [pagination, setPagination] = useState({ current: 1, pageSize: 10 });

  useEffect(() => {
    setLoading(true);
    fetch('/api/users')
      .then(r => r.json())
      .then(data => {
        setData(data);
        setLoading(false);
      });
  }, [pagination.current]);

  const columns = [
    { title: 'Name', dataIndex: 'name' },
    { 
      title: 'Status', 
      dataIndex: 'status',
      render: (s) => <Tag color={s === 'active' ? 'green' : 'red'}>{s}</Tag>
    },
    {
      title: 'Actions',
      render: (_, record) => (
        <Space>
          <Button size="small">Edit</Button>
          <Button size="small" danger>Delete</Button>
        </Space>
      ),
    },
  ];

  return (
    <Table
      columns={columns}
      dataSource={data}
      loading={loading}
      pagination={pagination}
      onChange={setPagination}
      rowKey="id"
    />
  );
}
```
