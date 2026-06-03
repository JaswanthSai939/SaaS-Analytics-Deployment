from pymongo import MongoClient
import certifi

uri = "mongodb+srv://saasadmin:Saas%40123456@cluster0.mtv0z8k.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

try:
    client = MongoClient(
        uri,
        tls=True,
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=5000
    )

    print(client.admin.command("ping"))
    print("Connected Successfully!")

except Exception as e:
    print("ERROR:")
    print(e)