import bcrypt


stored_hash = "$2b$12$0aaULpk/L.Ex9hRDsPIqmuOdEdMBdG7k7eUlw6uUDbTEnFQTZDLJm"  # Let's say this is "$2b$12$etnT5ERk27j52V9pzIeAXOuuaEJWwZgDoSvLrUbHDst5g5Auvbq9C"

# The password entered by the user
entered_password = "abi"

# Convert entered password to bytes and compare with stored hash
match = bcrypt.checkpw(entered_password.encode('utf-8'), stored_hash.encode('utf-8'))

if match:
    print("Password is correct.")
else:
    print("Incorrect password.")
