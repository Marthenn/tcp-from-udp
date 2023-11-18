from connection import Connection

con = Connection("localhost", 8000, 5000, True)
con.listen()