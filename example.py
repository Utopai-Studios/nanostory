import os
import time  
from dotenv import load_dotenv
from byteplussdkarkruntime import Ark

# Load environment variables from .env file
load_dotenv()

# Initialize the Ark client to read your API Key from environment variable
client = Ark(
    base_url=os.getenv("ARK_BASE_URL"),
    api_key=os.getenv("ARK_API_KEY"),
)

if __name__ == "__main__":
    print("----- create request -----")
    create_result = client.content_generation.tasks.create(
        model="seedance-1-5-pro-251215", # Model ID
        content=[
            {
                # Combination of text prompt and parameters
                "type": "text",
                "text": "A character is struck by a gunshot, his body jerks violently as dark blood bursts outward, splattering across the surrounding space in a sudden, shocking moment.  --duration 5 --camerafixed false"
            },
            # {
            #     # The URL of the first frame image
            #     "type": "image_url",
            #     "image_url": {
            #         "url": "https://ark-doc.tos-ap-southeast-1.bytepluses.com/seepro_i2v%20.png" 
            #     }
            # }
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