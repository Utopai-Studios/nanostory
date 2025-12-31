# Seedance API Guide

Official API documentation for Seedance video generation.

## Setup

Install the BytePlus SDK:

```bash
pip install --upgrade 'byteplus-python-sdk-v2'
pip install python-dotenv
```

## Usage

This project provides a simplified wrapper. See `videogen.py` for examples:

```python
from seedance_provider import generate_video

# Text-to-video
result = generate_video(
    prompt="A serene sunset over the ocean",
    duration=5,
    camera_fixed=False,
)

# Image-to-video
result = generate_video(
    prompt="A gentle breeze moves through the scene",
    reference_image_url="https://your-image-url.com/image.png",
    duration=5,
)
```

## Raw API Reference

### Python

```python
import os
from byteplussdkarkruntime import Ark

client = Ark(
    base_url="https://ark.ap-southeast.bytepluses.com/api/v3",
    api_key=os.environ.get("ARK_API_KEY"),
)

# Create task
create_result = client.content_generation.tasks.create(
    model="seedance-1-5-pro-251215",
    content=[
        {
            "type": "text",
            "text": "Your prompt here  --duration 5 --camerafixed false"
        },
        {
            # Optional: reference image for image-to-video
            "type": "image_url",
            "image_url": {
                "url": "https://your-image-url.com/image.png"
            }
        }
    ]
)

# Poll for result
task_id = create_result.id
get_result = client.content_generation.tasks.get(task_id=task_id)
```

### cURL

**Create a task:**

```bash
curl -X POST https://ark.ap-southeast.bytepluses.com/api/v3/contents/generations/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ARK_API_KEY" \
  -d '{
    "model": "seedance-1-5-pro-251215",
    "content": [
        {
            "type": "text",
            "text": "Your prompt here  --duration 5 --camerafixed false"
        },
        {
            "type": "image_url",
            "image_url": {
                "url": "https://your-image-url.com/image.png"
            }
        }
    ]
}'
```

**Query a task:**

```bash
curl -X GET https://ark.ap-southeast.bytepluses.com/api/v3/contents/generations/tasks/{task_id} \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ARK_API_KEY"
```

## Links

- [Query task list](https://docs.byteplus.com/en/docs/ModelArk/1520757#query-content-generation-task-list-api)
- [Cancel/delete tasks](https://docs.byteplus.com/en/docs/ModelArk/1520757#cancel-or-delete-content-generation-tasks)

