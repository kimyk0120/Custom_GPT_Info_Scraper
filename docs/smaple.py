import requests
import json
import pandas as pd
from google.colab import files
import time
import logging
from datetime import datetime
import urllib.parse

# Upload the input Excel file
uploaded = files.upload()

# Assume that the user uploads only one file and get the file name
input_file = list(uploaded.keys())[0]

# Read URLs from the uploaded Excel file
urls_df = pd.read_excel(input_file)

# Initialize a list to store data for each URL
data_list = []

# Loop through each URL in the DataFrame
for index, row in urls_df.iterrows():
    url = row['URLs']  # Replace 'URLs' with the actual column name in your Excel file

    # Fetch the webpage content
    response = requests.get(url)
    content = response.text

    # Find the start and end of the JSON part
    json_start = content.find('{"props":{"pageProps"')
    json_end = content.find('</script>', json_start)

    if json_start != -1 and json_end != -1:
        json_content = content[json_start:json_end]

        try:
            # Parse the JSON content
            parsed_json = json.loads(json_content)

            # Get the current date and time
            current_datetime = datetime.now()
            retrieved_date = current_datetime.strftime('%Y-%m-%d')
            retrieved_time = current_datetime.strftime('%H:%M:%S')

            # Extract LinkedIn, GitHub, and X links from verified_data
            linkedIn_link = ""
            github_link = ""
            x_link = ""
            for social in parsed_json["props"]["pageProps"]["gizmo"]["gizmo"]["author"]["display_socials"]:
                if social.get("type", "").lower() == "linkedin":
                    linkedIn_link = social["verified_data"].get("link_to", "")
                elif social.get("type", "").lower() == "github":
                    github_link = social["verified_data"].get("link_to", "")
                elif social.get("type", "").lower() in ["twitter", "x"]:
                    x_link = social["verified_data"].get("link_to", "")

            # Extract Image URL and process it
            image_url = parsed_json["props"]["pageProps"]["gizmo"]["gizmo"]["display"]["profile_picture_url"]

            # Decode the URL to access the filename
            decoded_url = urllib.parse.unquote(image_url)
            filename_marker = "filename="
            filename_start = decoded_url.find(filename_marker) + len(filename_marker)
            filename_end = decoded_url.find(".png", filename_start)
            filename = decoded_url[filename_start:filename_end]

            # Check if "DALL" is in the filename
            dall_e_field = "Yes" if "DALL" in filename else "No"

            # Extract the date and time after "DALL-E"
            image_creation_date = ""
            if dall_e_field == "Yes":
                # Locate the start of the date after "DALL-E"
                date_time_start = filename.find("DALL") + len("DALL") + 10
                image_creation_date = filename[date_time_start:date_time_start+21].replace("%20", " ")

            # Extract and structure data
            sample_messages = parsed_json["props"]["pageProps"]["gizmo"]["gizmo"]["display"]["prompt_starters"]
            data = {
                "Retrieved Date": retrieved_date,
                "Retrieved Time": retrieved_time,
                "URL": url,
                "Image": image_url,
                "DALL-E": dall_e_field,
                "Image Creation": image_creation_date,
                "Title": parsed_json["props"]["pageProps"]["gizmo"]["gizmo"]["display"]["name"],
                "Creator": parsed_json["props"]["pageProps"]["gizmo"]["gizmo"]["author"]["display_name"],
                "Creator Link Website": parsed_json["props"]["pageProps"]["gizmo"]["gizmo"]["author"]["link_to"],
                "Creator Link LinkedIn": linkedIn_link,
                "Creator Link GitHub": github_link,
                "Creator Link X": x_link,
                "Description": parsed_json["props"]["pageProps"]["gizmo"]["gizmo"]["display"]["description"],
                "Sample Message 1": sample_messages[0] if len(sample_messages) > 0 else "",
                "Sample Message 2": sample_messages[1] if len(sample_messages) > 1 else "",
                "Sample Message 3": sample_messages[2] if len(sample_messages) > 2 else "",
                "Sample Message 4": sample_messages[3] if len(sample_messages) > 3 else "",
            }

            # Append data to the list
            data_list.append(data)

        except json.JSONDecodeError:
            print(f"The extracted content from {url} is not valid JSON.")
        except KeyError as e:
            print(f"Missing key in JSON for {url}: {e}")
    else:
        print(f"JSON part or closing </script> tag not found in the response for {url}.")

# Create a pandas DataFrame with the collected data
df = pd.DataFrame(data_list)

# Define the output file name
output_file = 'output.xlsx'

# Write data to the output Excel file
df.to_excel(output_file, index=False)

print(f"Data extracted and saved to {output_file}.")

# Download the output Excel file
files.download(output_file)