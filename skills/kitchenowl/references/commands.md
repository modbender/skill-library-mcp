# KitchenOwl CLI Command Reference

Install:

```bash
pipx install kitchenowl-cli
```

## Auth

```bash
kitchenowl auth login --server https://kitchenowl.example.com
kitchenowl auth status
kitchenowl auth logout
```

## Server settings

```bash
kitchenowl config server-settings
kitchenowl config server-settings --json
```

## Household

```bash
kitchenowl household list
kitchenowl household get 8
kitchenowl household member list --household-id 8
```

## Shopping list

```bash
kitchenowl shoppinglist list --household-id 8
kitchenowl shoppinglist create "Weekly" --household-id 8
kitchenowl shoppinglist add-item-by-name 12 Milk --description "2L"
kitchenowl shoppinglist remove-item 12 456 -y
```

## Recipe

```bash
kitchenowl recipe list --household-id 8
kitchenowl recipe get 123
kitchenowl recipe add --household-id 8 --name "Tomato Soup" --yields 2 --time 25
kitchenowl recipe edit 123 --description "Updated"
kitchenowl recipe delete 123
```

## User admin

```bash
kitchenowl user list
kitchenowl user get 3
kitchenowl user search andreas
```
