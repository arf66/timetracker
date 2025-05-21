import sqlite3
from sqlite3 import Error
from constants import DATABASE, DEBUG


def debugprint(s):
    if DEBUG:
        print(s)


class TrelloDatabase:

    def __init__(self, db_file):
        """Initialize the database connection."""
        self.connection = None
        try:
            self.connection = sqlite3.connect(db_file)
            debugprint(f"Connected to database {db_file}")
            self.create_table()
        except Error as e:
            debugprint(f"Error connecting to database: {e}")

    def create_table(self):
        """Create the users table if it doesn't exist."""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS users (
            username TEXT UNIQUE,
            password TEXT,
            role TEXT,
            usertz TEXT
        );
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(create_table_sql)
            self.connection.commit()
            debugprint("Users table created or verified.")
        except Error as e:
            debugprint(f"Error creating table: {e}")

    def create_user(self, username, password, role, usertz):
        """Insert a new user into the users table."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("INSERT INTO users (username, password, role, usertz) VALUES (?, ?, ?, ?)",
                           (username, password, role, usertz))
            self.connection.commit()
            debugprint("User created successfully.")
            return True
        except Error as e:
            debugprint(f"Error creating user: {e}")
            return False

    def get_user(self, username):
        """Fetch a user from the users table by username."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()
            return user
        except Error as e:
            debugprint(f"Error fetching user: {e}")
            return None

    def update_user(self, username, password=None, role=None):
        """Update a user's password and/or role."""
        try:
            cursor = self.connection.cursor()
            if password and role:
                cursor.execute("UPDATE users SET password = ?, role = ? WHERE username = ?",
                               (password, role, username))
            elif password:
                cursor.execute("UPDATE users SET password = ? WHERE username = ?",
                               (password, username))
            elif role:
                cursor.execute("UPDATE users SET role = ? WHERE username = ?",
                               (role, username))
            self.connection.commit()
            debugprint("User updated successfully.")
        except Error as e:
            debugprint(f"Error updating user: {e}")

    def delete_user(self, username):
        """Delete a user from the users table."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM users WHERE username = ?", (username,))
            self.connection.commit()
            debugprint("User deleted successfully.")
        except Error as e:
            debugprint(f"Error deleting user: {e}")

    def check_user(self, usr, pwd):
        """Check if a user exist with the given password"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT * FROM users WHERE username = '{usr}' and password = '{pwd}';")
            rows = cursor.fetchall()
            return len(rows)>0
        except Error as e:
            debugprint(f"Error checking user: {e}")
            return False

    def close_connection(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            debugprint("Database connection closed.")

class Tasks:
    def __init__(self, db_name=DATABASE, user=None):
        self.db_name = db_name
        self.username= user
        self.connection = sqlite3.connect(self.db_name)
        self.create_table()

    def create_table(self):
        with self.connection:
            self.connection.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    user TEXT NOT NULL,
                    title TEXT NOT NULL,
                    tag TEXT NOT NULL,
                    customer TEXT,
                    created REAL NOT NULL,
                    status TEXT NOT NULL,
                    due_time REAL NOT NULL,
                    begin_time REAL,
                    last_begin_time REAL,
                    end_time REAL,
                    duration REAL
                )
            ''')

    def create_task(self, id, user, title, tag, customer, created_time, status, due_time, begin_time, last_begin_time, end_time, duration):
        try:
            with self.connection:
                cursor = self.connection.execute('''
                    INSERT INTO tasks (id, user, title, tag, customer, created, status, due_time, begin_time, last_begin_time, end_time, duration)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (id, user, title, tag, customer, created_time, status, due_time, begin_time, last_begin_time, end_time, duration))
            return True
        except:
            return False

    def read_task(self, task_id):
        cursor = self.connection.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
        return cursor.fetchone()

    def read_all_tasks(self, user):
        cursor = self.connection.execute("SELECT * FROM tasks WHERE user=?", (user,))
        return cursor.fetchall()

    def read_all_active_tasks(self, user):
        cursor = self.connection.execute("SELECT id, user, title, tag, customer, created, status, due_time, begin_time, last_begin_time, end_time, duration FROM tasks WHERE user=? and status not in ('Deleted', 'Archived')", (user,))
        return cursor.fetchall()

    def read_stats_by_tag(self, fromepoch, toepoch, user=None):
        if user is not None:
            statement="SELECT SUM(duration) as value, tag as name FROM tasks WHERE ? <= end_time AND end_time < ? and user = ? GROUP BY tag ORDER BY value DESC"
            parameters=(fromepoch, toepoch, user)
        else:
            statement="SELECT SUM(duration) as value, tag as name FROM tasks WHERE ? <= end_time AND end_time < ? GROUP BY tag ORDER BY value DESC"
            parameters=(fromepoch, toepoch)
        cursor = self.connection.execute(statement, parameters)
        return cursor.fetchall()

    def read_stats_by_customer(self, fromepoch, toepoch, user=None):
        if user is not None:
            statement="SELECT SUM(duration) as value, customer as name FROM tasks WHERE ? <= end_time AND end_time < ? and user = ? GROUP BY customer ORDER BY value DESC"
            parameters=(fromepoch, toepoch, user)
        else:
            statement="SELECT SUM(duration) as value, customer as name FROM tasks WHERE ? <= end_time AND end_time < ? GROUP BY customer ORDER BY value DESC"
            parameters=(fromepoch, toepoch)
        cursor = self.connection.execute(statement, parameters)
        return cursor.fetchall()


    def read_stats_by_day_month(self, fromepoch, toepoch, user=None):
        if user is not None:
            statement="SELECT duration as value, end_time as time FROM tasks WHERE ? <= end_time AND end_time < ? and user = ?"
            parameters=(fromepoch, toepoch, user)
        else:
            statement="SELECT duration as value, end_time as time FROM tasks WHERE ? <= end_time AND end_time < ?"
            parameters=(fromepoch, toepoch)
        cursor = self.connection.execute(statement, parameters)
        return cursor.fetchall()

    def read_completed_tasks(self, fromepoch, toepoch, user=None):
        if user is not None:
            statement="SELECT end_time, title, tag, customer, duration FROM tasks WHERE ? <= end_time AND end_time < ? and user = ? and status in ('Done', 'Archived') ORDER BY end_time"
            parameters=(fromepoch, toepoch, user)
        else:
            statement="SELECT user, end_time, title, tag, customer, duration FROM tasks WHERE ? <= end_time AND end_time < ? and status='Done' ORDER BY end_time"
            parameters=(fromepoch, toepoch)
        cursor = self.connection.execute(statement, parameters)
        return cursor.fetchall()

    def update_task(self, task_id, title=None, tag=None, customer=None, status=None, due_time=None, begin_time=None, 
                        last_begin_time=None, end_time=None, duration=None):
        updated_fields = []
        params = []
        
        if title is not None:
            updated_fields.append("title = ?")
            params.append(title)
        
        if tag is not None:
            updated_fields.append("tag = ?")
            params.append(tag)
        
        if customer is not None:
            updated_fields.append("customer = ?")
            params.append(customer)

        if status is not None:
            updated_fields.append("status = ?")
            params.append(status)

        if due_time is not None:
            updated_fields.append("due_time = ?")
            params.append(due_time)

        if begin_time is not None:
            updated_fields.append("begin_time = ?")
            params.append(begin_time)

        if last_begin_time is not None:
            updated_fields.append("last_begin_time = ?")
            params.append(last_begin_time)

        if end_time is not None:
            updated_fields.append("end_time = ?")
            params.append(end_time)

        if duration is not None:
            updated_fields.append("duration = ?")
            params.append(duration)

        if updated_fields:
            params.append(task_id)
            query = f"UPDATE tasks SET {', '.join(updated_fields)} WHERE id = ?"
            print(query)
            with self.connection:
                self.connection.execute(query, params)

    def delete_task(self, task_id):
        with self.connection:
            self.connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

    def delete_user_tasks(self, user):
        with self.connection:
            self.connection.execute("DELETE FROM tasks WHERE user = ?", (user,))

    def delete_user_tasks_from_tuple(self, inlist):
        with self.connection:
            if len(inlist) == 0:
                return
            if len(inlist) == 1:
                statement = f"DELETE FROM tasks WHERE id in ('{str(inlist[0])}')"
            else:
                statement = f"DELETE FROM tasks WHERE id in {inlist}"
            self.connection.execute(statement)

    def close_connection(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            print("Database connection closed.")

    def __del__(self):
        self.connection.close()

# Globals
userDB: TrelloDatabase = None
taskDB: Tasks = None
