import requests


def verify_instagram(username):

	appId="936619743392459"

	headers = {
		# 'User-Agent':'Instagram 76.0.0.15.395 Android (24/7.0; 640dpi; 1440x2560; samsung; SM-G930F; herolte; samsungexynos8890; en_US; 138226743)',
		'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1',
		"x-ig-app-id": appId,

	}

	
	response=requests.get("https://i.instagram.com/api/v1/users/web_profile_info/?username="+username, headers=headers, proxies=proxies)

	print(response.status_code)
	print(response.text)
	
	if response.status_code==404:
		return False
		
	else:
		return True

if __name__=='__main__':

	global proxies
	
	proxies = {
		"proxy": "http://scraperapi:7fd256cb935efe83634cbc7170ae92d1@proxy-server.scraperapi.com:8003",
		"http": "http://scraperapi:7fd256cb935efe83634cbc7170ae92d1@proxy-server.scraperapi.com:8002"
	}
		
	
	username="3434534456"
	
	status=verify_instagram(username)
	
	if status:
		print(" username exists")
	else:
		print(" username doesn't exist")