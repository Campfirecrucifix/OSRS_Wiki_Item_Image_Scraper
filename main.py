import requests
import json
import os
import time

# Set the base URL for the API and the category name
base_url = "https://oldschool.runescape.wiki/api.php"
category = "Category:Detailed_item_images"

# Set the directory where the images should be saved
save_directory = "item_images"

# Make the directory if it does not already exist
if not os.path.exists(save_directory):
    os.makedirs(save_directory)

# Set the continuation parameter to an empty string
cont = ""

# Set the limit of items per API call to 50
limit = 50

# Set the counter for the number of items processed to 0
count = 0

# Set the flag for continuing the loop to True
continue_loop = True

# Set the flag for finding the start item to False
found_start_item = False

print("If you would like to start at a specific file please enter it below.")
print("Ex: File:Burnt cake detail.png")

# Set the name of the item to start the search from
start_item = input("Please enter file name or leave blank: ")

# Loop until the start item is found or the continuation parameter is an empty string
while continue_loop:
    # Set the parameter for the action to query
    params = {
        "action": "query",
        # Set the list to categorymembers
        "list": "categorymembers",
        # Set the cmtitle to the category name
        "cmtitle": category,
        # Set the format to json
        "format": "json",
        # Set the cmlimit to the limit
        "cmlimit": str(limit),
        # Set the cmcontinue parameter to the continuation parameter
        "cmcontinue": cont
    }

    # Make the API call
    res = requests.get(base_url, params=params)

    # Convert the response to JSON
    data = json.loads(res.text)

    # Get the continuation parameter for the next API call
    cont = data.get("continue", {}).get("cmcontinue", "")

    # Set the 'continue' flag to False if the continuation parameter is an empty string
    if cont == "":
        continue_loop = False

    # Get the list of items
    items = data["query"]["categorymembers"]

    # Loop through the items
    for item in items:
        # Increment the count
        count += 1

        # Get the title and file name of the item
        title = item["title"]
        file_name = title.replace("File:", "").replace(" ", "_").replace("?", "_")

        # Remove the duplicate extension from the file name
        file_name = file_name[:-4] if file_name.endswith(".png") else file_name

        # Set the parameters for the image info API call
        params = {
            "action": "query",
            "titles": title,
            "format": "json",
            "prop": "imageinfo",
            "iiprop": "url",
            "iiurlwidth": "512"
        }

        if start_item == "":
            start_item = title

        # If the found_start_item flag is True, download the image
        if found_start_item or title == start_item:
            found_start_item = True
            # Try the request a maximum of 3 times
            for i in range(3):
                try:
                    # Make the API call
                    res = requests.get(base_url, params=params)

                    # Convert the response to JSON
                    data = json.loads(res.text)

                    # Get the URL of the image
                    image_url = list(data["query"]["pages"].values())[0]["imageinfo"][0]["url"]

                    # Download the image
                    image = requests.get(image_url)

                    # Save the image to the save directory
                    open(f"{save_directory}/{file_name}.png", "wb").write(image.content)

                    # Break out of the loop if the request was successful
                    break

                except Exception as e:
                    # Print an error message if the request failed
                    print(f"Error downloading {title}: {e}")

                    # Wait 2 seconds before trying again
                    time.sleep(2)

            else:
                # Print a message if the request failed after the maximum number of attempts
                print(f"Unable to download {title}")

        # If the found_start_item flag is False, skip the item
        else:
            # Print a message that the item is being skipped
            print(f"Skipping {title}")

    # Print the number of items processed
    print(f"Number of items processed: {count}")
