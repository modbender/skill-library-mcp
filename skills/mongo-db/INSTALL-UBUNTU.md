# Install MongoDB on Ubuntu

Steps to install **MongoDB Community Server** on Ubuntu so the mongo-db skill can connect to a local instance. If you use MongoDB Atlas, you don't need to install the server — just set `MONGO_URI` to your Atlas connection string.

---

## 1. Import the official MongoDB GPG key and add the repo

```bash
# Install prerequisites
sudo apt-get install -y gnupg curl

# Import MongoDB public GPG key
curl -fsSL https://www.mongodb.org/static/pgp/server-8.0.asc | \
   sudo gpg -o /usr/share/keyrings/mongodb-server-8.0.gpg --dearmor

# Add MongoDB repo for your Ubuntu version (e.g. 24.04)
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-8.0.gpg ] https://repo.mongodb.org/apt/ubuntu noble/mongodb-org/8.0 multiverse" | \
   sudo tee /etc/apt/sources.list.d/mongodb-org-8.0.list
```

Replace `noble` with your Ubuntu codename if different:

- **24.04** → `noble`
- **22.04** → `jammy`
- **20.04** → `focal`

---

## 2. Install MongoDB

```bash
sudo apt-get update
sudo apt-get install -y mongodb-org
```

---

## 3. Start and enable the service

```bash
sudo systemctl start mongod
sudo systemctl enable mongod
```

---

## 4. Verify it's running

```bash
sudo systemctl status mongod
```

Or connect with the shell:

```bash
mongosh
```

---

## Service reference

| Action   | Command                          |
|----------|----------------------------------|
| Start    | `sudo systemctl start mongod`    |
| Stop     | `sudo systemctl stop mongod`     |
| Restart  | `sudo systemctl restart mongod`  |
| Status   | `sudo systemctl status mongod`   |
| Shell    | `mongosh`                        |

---

## Using with this skill

After MongoDB is running, configure the skill with a local URI:

- **Environment:** `MONGO_URI=mongodb://localhost:27017` (and optionally `MONGO_DB=mydb`)
- **config.json:** `"uri": "mongodb://localhost:27017"` (see `config.example.json`)

Then run the skill setup and use the client as described in `SKILL.md`.
