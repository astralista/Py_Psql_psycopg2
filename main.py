import psycopg2

def create_db(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE clients (
                id SERIAL PRIMARY KEY,
                first_name VARCHAR(50),
                last_name VARCHAR(50),
                email VARCHAR(50),
                phones VARCHAR(255)[] );
            """)
        conn.commit()

def add_client(conn, first_name, last_name, email, phones=None):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO clients (first_name, last_name, email, phones)
            VALUES (%s, %s, %s, %s);
            """, (first_name, last_name, email, phones or []))
        conn.commit()

def add_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE clients
            SET phones = array_append(phones, %s)
            WHERE id = %s;
            """, (phone, client_id))
        conn.commit()

def change_client(conn, client_id, first_name=None, last_name=None, email=None, phones=None):
    with conn.cursor() as cur:
        if first_name:
            cur.execute("""
                UPDATE clients
                SET first_name = %s
                WHERE id = %s;
                """, (first_name, client_id))
        if last_name:
            cur.execute("""
                UPDATE clients
                SET last_name = %s
                WHERE id = %s;
                """, (last_name, client_id))
        if email:
            cur.execute("""
                UPDATE clients
                SET email = %s
                WHERE id = %s;
                """, (email, client_id))
        if phones is not None:
            cur.execute("""
                UPDATE clients
                SET phones = %s
                WHERE id = %s;
                """, (phones or [], client_id))
        conn.commit()

def delete_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE clients
            SET phones = array_remove(phones, %s)
            WHERE id = %s;
            """, (phone, client_id))
        conn.commit()

def delete_client(conn, client_id):
    with conn.cursor() as cur:
        cur.execute("""
            DELETE FROM clients
            WHERE id = %s;
            """, (client_id,))
        conn.commit()

def find_client(conn, first_name=None, last_name=None, email=None, phone=None):
    with conn.cursor() as cur:
        query = """
            SELECT * FROM clients
            WHERE """
        conditions = []
        params = []
        if first_name:
            conditions.append("first_name = %s")
            params.append(first_name)
        if last_name:
            conditions.append("last_name = %s")
            params.append(last_name)
        if email:
            conditions.append("email = %s")
            params.append(email)
        if phone:
            conditions.append("%s = ANY (phones)")
            params.append(phone)
        if conditions:
            query += " AND ".join(conditions)
            cur.execute(query, tuple(params))
        else:
            cur.execute("SELECT * FROM clients")
        clients = cur.fetchall()
        return clients

with psycopg2.connect(database="clients_db", user="postgres", password="postgres") as conn:
    create_db(conn)
    add_client(conn, "Иван", "Иванов", "ivanov@mail.ru", ["123-456-789", "234-567-890"])
    add_phone(conn, 1, "345-678-901")
    change_client(conn, 1, first_name="Петр")
    delete_phone(conn, 2, "234-567-890")
    delete_client(conn, 1)
    clients = find_client(conn, last_name="Иванов")
    print(clients)

conn.close()