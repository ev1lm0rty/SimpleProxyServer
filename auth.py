import json
import time

#Ths code be used to create the authorization json file
print("Creating Credentials")
time.sleep(2)
auth={
    "dixit": ["1234", 1],
    "arya": ["qwerty", 2],
    "shikhar": ["shukla", 3],
    "tanish": ["katyal", 1]
}

with open("auth.json","w") as file:
    json.dump(auth,file)
print("Credentials dumped successfully")

