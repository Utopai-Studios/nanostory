# Python

1. Please install the environment using the following commands:

```
pip install --upgrade 'byteplus-python-sdk-v2'
```

2. For service calling, refer to the following sample code.

```
import os
import time  
from byteplussdkarkruntime import Ark

# Make sure that you have stored the API Key in the environment variable ARK_API_KEY
# Initialize the Ark client to read your API Key from an environment variable
client = Ark(
    # This is the default path. You can configure it based on the service location
    base_url="https://ark.ap-southeast.bytepluses.com/api/v3",
    # Get your Key authentication from the environment variable. This is the default mode and you can modify it as required
    api_key=os.environ.get("ARK_API_KEY"),
)

if __name__ == "__main__":
    print("----- create request -----")
    create_result = client.content_generation.tasks.create(
        model="seedance-1-5-pro-251215", # Model ID
        content=[
            {
                # Combination of text prompt and parameters
                "type": "text",
                "text": "At breakneck speed, drones thread through intricate obstacles or stunning natural wonders, delivering an immersive, heart-pounding flying experience.  --duration 5 --camerafixed false"
            },
            {
                # The URL of the first frame image
                "type": "image_url",
                "image_url": {
                    "url": "https://ark-doc.tos-ap-southeast-1.bytepluses.com/seepro_i2v%20.png" 
                }
            }
        ]
    )
    print(create_result)

    # Polling query section
    print("----- polling task status -----")
    task_id = create_result.id
    while True:
        get_result = client.content_generation.tasks.get(task_id=task_id)
        status = get_result.status
        if status == "succeeded":
            print("----- task succeeded -----")
            print(get_result)
            break
        elif status == "failed":
            print("----- task failed -----")
            print(f"Error: {get_result.error}")
            break
        else:
            print(f"Current status: {status}, Retrying after 1 seconds...")
            time.sleep(1)
# Please refer to following links for more operations
# Query video generation tasks list：https://docs.byteplus.com/en/docs/ModelArk/1520757#query-content-generation-task-list-api
# Cancel or delete video generation tasks：https://docs.byteplus.com/en/docs/ModelArk/1520757#cancel-or-delete-content-generation-tasks
```

# curl

1. Create a task

```
# Create an image-to-video task
curl -X POST https://ark.ap-southeast.bytepluses.com/api/v3/contents/generations/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ARK_API_KEY" \
  -d '{
    "model": "seedance-1-5-pro-251215",
    "content": [
        {
            "type": "text",
            "text": "At breakneck speed, drones thread through intricate obstacles or stunning natural wonders, delivering an immersive, heart-pounding flying experience.  --duration 5 --camerafixed false"
        },
        {
            "type": "image_url",
            "image_url": {
                "url": "https://ark-doc.tos-ap-southeast-1.bytepluses.com/seepro_i2v%20.png"
            }
        }
    ]
}'
```

2. Query a task

```
# Query a task (please fill in the id returned by step 1)
curl -X GET https://ark.ap-southeast.bytepluses.com/api/v3/contents/generations/tasks/{id} \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ARK_API_KEY"
```