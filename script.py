import json
import urllib.parse
from datetime import datetime

import pandas as pd
import requests

import re

data_list = []

# url = "https://chatgpt.com/g/g-23B7QDQzF-ai-coupon-code-finder-smart-shopping-companion"
url = "https://chatgpt.com/g/g-GbLbctpPz-universal-primer"

# Fetch the webpage content
response = requests.get(url, verify=False)
content = response.text

# Find the start and end of the JSON part
json_start = content.find('"gizmo":')
# json_end = content.find('</script>', json_start)
json_end = content.find('}}}}', json_start)

json_content = "{" + content[json_start:json_end] + "}}}}"

# Parse the JSON content
parsed_json = json.loads(json_content)

# Get the current date and time
current_datetime = datetime.now()
retrieved_date = current_datetime.strftime('%Y-%m-%d')
retrieved_time = current_datetime.strftime('%H:%M:%S')

# Extract Image URL and process it

image_url = parsed_json['gizmo']['gizmo']['display']['profile_picture_url']

# URL을 파싱하여 쿼리 파라미터 추출
parsed_url = urllib.parse.urlparse(image_url)
query_params = urllib.parse.parse_qs(parsed_url.query)

# 파일 이름 추출 (URL 인코딩 해제)
filename = urllib.parse.unquote(query_params['rscd'][0].split('filename=')[1])

# Check if "DALL" is in the filename
dall_e_field = "Yes" if "DALL" in filename else "No"

# Extract the date and time after "DALL-E"
image_creation_date = ""
dall_e_prompt = ""

if dall_e_field == "Yes":
    a_splt = filename.split(' - ')
    match = re.search(r'\d{4}-\d{2}-\d{2} \d{2}\.\d{2}\.\d{2}', a_splt[0])
    if match:
        image_creation_date = match.group()

    dall_e_prompt = a_splt[1]

linkedIn_link = ""
github_link = ""
x_link = ""

for social in parsed_json["gizmo"]["gizmo"]["author"]["display_socials"]:
    if social.get("type", "").lower() == "linkedin":
        linkedIn_link = social["verified_data"].get("link_to", "")
    elif social.get("type", "").lower() == "github":
        github_link = social["verified_data"].get("link_to", "")
    elif social.get("type", "").lower() in ["twitter", "x"]:
        x_link = social["verified_data"].get("link_to", "")

# Extract and structure data
sample_messages = parsed_json["gizmo"]["gizmo"]["display"]["prompt_starters"]

data = {
    "Retrieved Date": retrieved_date,
    "Retrieved Time": retrieved_time,
    "URL": url,
    "Image": image_url,
    "DALL-E": dall_e_field,
    "DALL-E Prompt": dall_e_prompt,
    "Image Creation": image_creation_date,
    "Title": parsed_json['gizmo']['gizmo']['display']['name'],
    "Creator": parsed_json['gizmo']['gizmo']['author']['display_name'],
    "Creator Link Website": parsed_json["gizmo"]["gizmo"]["author"]["link_to"],
    "Creator Link LinkedIn": linkedIn_link,
    "Creator Link GitHub": github_link,
    "Creator Link X": x_link,
    "Description": parsed_json["gizmo"]["gizmo"]["display"]["description"],
    "Sample Message 1": sample_messages[0] if len(sample_messages) > 0 else "",
    "Sample Message 2": sample_messages[1] if len(sample_messages) > 1 else "",
    "Sample Message 3": sample_messages[2] if len(sample_messages) > 2 else "",
    "Sample Message 4": sample_messages[3] if len(sample_messages) > 3 else "",
}

# Append data to the list
data_list.append(data)

# Create a pandas DataFrame with the collected data
df = pd.DataFrame(data_list)

# Define the output file name
output_file = 'output.xlsx'

# Write data to the output Excel file
df.to_excel(output_file, index=False)

print(f"Data extracted and saved to {output_file}.")
