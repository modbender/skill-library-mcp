# Ant Design React — Page Recipes

## CRUD List (Table + Filters + Modal)

### Layout skeleton
- Title row: `Typography.Title` + `Button type=primary`
- Filters: `Form layout="inline"` (or `vertical` if complex)
- Table: `Table` with server-side pagination

### Components
- `Form`, `Input`, `Select`, `DatePicker`, `Button`, `Table`, `Modal`, `Popconfirm`, `Space`

### Key tips
- Always set `rowKey`
- Keep actions in a right-aligned column
- Use `message.success/error` after mutations

## Settings Page (Card + Form)

### Components
- `Card`, `Form`, `Input`, `Switch`, `Divider`, `Typography`

### Key tips
- Split into sections with `Divider`
- Keep save button sticky if page is long

## Wizard (Steps)

### Components
- `Steps`, `Form`, `Button`, `Card`

### Key tips
- Validate per step using `form.validateFields()`
- Persist step data in state

## Feedback / Empty / Loading
- Loading: `Spin` or skeletons
- Empty: `Empty`
- Errors: `Alert`, `message`, `notification`
