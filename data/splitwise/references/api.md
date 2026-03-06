# Splitwise API Reference

## Authentication
The Splitwise API uses OAuth2. For simple scripts, a Long-lived User Token can be generated in the [Splitwise Developer Console](https://secure.splitwise.com/apps).

Base URL: `https://secure.splitwise.com/api/v3.0/`

## Endpoints

### Create Expense
`POST /create_expense`

Required Parameters:
- `cost`: The total amount of the expense.
- `description`: A short description of the expense.
- `group_id` (optional): The group to add the expense to.
- `users__0__user_id`: The ID of the person who paid.
- `users__0__paid_share`: The amount the person paid.
- `users__0__owed_share`: The amount the person owes.
- `users__1__user_id`: The ID of the other person.
- `users__1__paid_share`: 0
- `users__1__owed_share`: The amount they owe.

Example for a 50/50 split of $10:
- `cost`: 10
- `users__0__user_id`: (Payer ID)
- `users__0__paid_share`: 10
- `users__0__owed_share`: 5
- `users__1__user_id`: (Other ID)
- `users__1__paid_share`: 0
- `users__1__owed_share`: 5

### Get Current User
`GET /get_current_user`
Useful for finding your own `user_id`.

### Get Groups
`GET /get_groups`
Useful for finding `group_id`s.
