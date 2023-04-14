import requests

url = "https://tonn.roexaudio.com/multitrackstatus/c86b902a-27f8-4adc-a392-73398b9edcb0"

querystring = {"key":"AIzaSyAzMhnWIYscIFkR2sAPvZlokyJc3cEky8w"}

headers = {"Content-Type": "application/json"}

response = requests.request("GET", url, headers=headers, params=querystring)

print(response.text)