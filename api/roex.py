import requests

url = "https://tonn.roexaudio.com/multitrackmix"

querystring = {"key":"AIzaSyAzMhnWIYscIFkR2sAPvZlokyJc3cEky8w"}

payload = {"multitrackData": {
        "trackData": [
            {
                "trackURL": "https://storage.googleapis.com/test-bucket-api-roex/test_mix/Guitar_01.wav",
                "instrumentGroup": "E_GUITAR_GROUP",
                "presenceSetting": "NORMAL",
                "isStem": False,
                "panPreference": "NO_PREFERENCE",
                "reverbPreference": "NONE"
            },
            {
                "trackURL": "https://storage.googleapis.com/test-bucket-api-roex/test_mix/drum_mix.wav",
                "instrumentGroup": "DRUMS_GROUP",
                "presenceSetting": "NORMAL",
                "isStem": True,
                "panPreference": "CENTRE",
                "reverbPreference": "NONE"
            },
            {
                "trackURL": "https://storage.googleapis.com/test-bucket-api-roex/test_mix/fx_mix.wav",
                "instrumentGroup": "FX_GROUP",
                "presenceSetting": "NORMAL",
                "isStem": True,
                "panPreference": "NO_PREFERENCE",
                "reverbPreference": "NONE"
            },
            {
                "trackURL": "https://storage.googleapis.com/test-bucket-api-roex/test_mix/synth_mix.wav",
                "instrumentGroup": "SYNTH_GROUP",
                "presenceSetting": "NORMAL",
                "isStem": True,
                "panPreference": "NO_PREFERENCE",
                "reverbPreference": "NONE"
            },
            {
                "trackURL": "https://storage.googleapis.com/test-bucket-api-roex/test_mix/vox_mix.wav",
                "instrumentGroup": "VOCAL_GROUP",
                "presenceSetting": "LEAD",
                "isStem": True,
                "panPreference": "CENTRE",
                "reverbPreference": "LOW"
            }
        ],
        "musicalStyle": "POP",
        "returnUnmixedTrack": False
    }}
headers = {"Content-Type": "application/json"}

response = requests.request("POST", url, json=payload, headers=headers, params=querystring)

print(response.text)