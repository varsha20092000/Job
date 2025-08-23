import psycopg2

try:
    conn = psycopg2.connect(
        dbname="job365_newdb",
        user="job365_newdb_user",
        password="b4Fx1MQd8qQ6bb82eirmzqf1i16u8Wakb",
        host="dpg-d2heeu8d13ps738840p0-a.singapore-postgres.render.com",
        port="5432",
        sslmode="disable"  # <- only for testing
    )
    print("Connection successful without SSL!")
    conn.close()
except Exception as e:
    print("Connection failed:", e)
