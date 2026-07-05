import requests

# Thay bằng Access Token Telegraph của bạn
ACCESS_TOKEN = "829b74b1920c6338f83418830e90b0b0caf879fa906b026f3890f7b3f4f5"

def create_key_page(key, key_type="FREE", expire="Không giới hạn"):
    url = "https://api.telegra.ph/createPage"

    content = f"""[
        {{
            "tag":"h3",
            "children":["VBTool License"]
        }},
        {{
            "tag":"p",
            "children":["Key: {key}"]
        }},
        {{
            "tag":"p",
            "children":["Loại: {key_type}"]
        }},
        {{
            "tag":"p",
            "children":["Hết hạn: {expire}"]
        }}
    ]"""

    data = {
        "access_token": ACCESS_TOKEN,
        "title": "VBTool License",
        "author_name": "VBTool",
        "content": content,
        "return_content": False
    }

    try:
        r = requests.post(url, data=data, timeout=10)
        result = r.json()

        if result.get("ok"):
            return "https://telegra.ph/" + result["result"]["path"]

        print(result)
        return None

    except Exception as e:
        print(e)
        return None