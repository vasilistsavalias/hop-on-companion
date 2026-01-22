# Administrator's Guide

This guide explains how to manage users in HopOn. You can use the built-in **Web Console** or the **Command Line Interface (CLI)**.

## Web-Based Admin Console (Recommended)

Admin users have access to a dedicated **User Management** panel directly in the application.

1.  **Log in** with an Admin account.
2.  Navigate to **User Management** in the sidebar.
3.  **Manage Users:** View list, change Roles (User/Admin), or Delete users.
4.  **Add User:** Create new accounts instantly.

## CLI User Management

For automated tasks or initial setup, use the `scripts/manage_users.py` script.

**Prerequisite:** Ensure your virtual environment is activated.

### 1. List Users

To see all registered users:

```bash
python scripts/manage_users.py list
```

**Output:**

```table
ID    Username             Name
--------------------------------------------------
1     admin                admin
2     researcher           researcher
```

### 2. Add a User

To create a new user (Username and Password are required):

```bash
python scripts/manage_users.py add <username> <password>
```

**Example:**

```bash
python scripts/manage_users.py add admin mysecurepassword
```

### 3. Edit a User

To update a user's username or password:

```bash
python scripts/manage_users.py edit <current_username> [--new-username <name>] [--new-password <pass>]
```

**Examples:**

```bash
# Change Password
python scripts/manage_users.py edit admin --new-password newsecret

# Change Username
python scripts/manage_users.py edit admin --new-username superadmin
```

### 4. Delete a User

To delete a user and their data:

```bash
python scripts/manage_users.py delete <username>
```

**Example:**

```bash
python scripts/manage_users.py delete admin
```

*(You will be asked to confirm unless you add `-y`)*

## Database Migrations

If you modify the database schema (models), you must run migrations:

```bash
# Apply pending migrations
alembic upgrade head
```
