from google import genai

client = genai.Client(api_key="AIzaSyAn5CTruGqWrtlZilcFs6JNwVvsXFEYF2g")

print("Here are the models you can use:")
for model in client.models.list():
    print(model.name)