from connection import Connection

con = Connection("127.0.0.2", 9000, 5000, False)
con.send(bytes("Testingnggg".encode()), "127.0.0.1", 8000)