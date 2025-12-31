import os
import time
from dotenv import load_dotenv
from byteplussdkarkruntime import Ark

# Load environment variables from .env file
load_dotenv()

# Initialize the Ark client
_client = Ark(
    base_url=os.getenv("ARK_BASE_URL"),
    api_key=os.getenv("ARK_API_KEY"),
)

DEFAULT_MODEL = "seedance-1-5-pro-251215"
VIDEO_EXTEND_MODEL = "seedance-1-5-pro-video-extend"


def generate_video(
    prompt: str,
    reference_image_url: str = None,
    duration: int = 5,
    camera_fixed: bool = False,
    model: str = DEFAULT_MODEL,
    poll_interval: float = 1.0,
) -> dict:
    """
    Generate a video using Seedance API.
    
    Args:
        prompt: Text description for the video
        reference_image_url: Optional URL of reference image for image-to-video generation
        duration: Video duration in seconds (default: 5)
        camera_fixed: Whether to fix camera position (default: False)
        model: Model ID to use (default: seedance-1-5-pro-251215)
        poll_interval: Seconds between status polling (default: 1.0)
    
    Returns:
        dict: Task result containing video information
    
    Raises:
        Exception: If video generation fails
    """
    # Build the full prompt with parameters
    full_prompt = f"{prompt}  --duration {duration} --camerafixed {str(camera_fixed).lower()}"
    
    # Build content list
    content = [
        {
            "type": "text",
            "text": full_prompt
        }
    ]
    
    # Add reference image if provided
    if reference_image_url:
        content.append({
            "type": "image_url",
            "image_url": {
                "url": reference_image_url
            }
        })
    
    # Create the generation task
    print("----- Creating video generation task -----")
    create_result = _client.content_generation.tasks.create(
        model=model,
        content=content
    )
    print(f"Task created with ID: {create_result.id}")
    
    # Poll for completion
    print("----- Polling task status -----")
    task_id = create_result.id
    
    while True:
        get_result = _client.content_generation.tasks.get(task_id=task_id)
        status = get_result.status
        
        if status == "succeeded":
            print("----- Task succeeded -----")
            return get_result
        elif status == "failed":
            print("----- Task failed -----")
            raise Exception(f"Video generation failed: {get_result.error}")
        else:
            print(f"Current status: {status}, retrying in {poll_interval}s...")
            time.sleep(poll_interval)


def extend_video(
    video_url: str,
    prompt: str,
    duration: int = 5,
    resolution: str = "1080p",
    aspect_ratio: str = "16:9",
    generate_audio: bool = True,
    model: str = VIDEO_EXTEND_MODEL,
    poll_interval: float = 1.0,
) -> dict:
    """
    Extend a video using Seedance API.
    
    Args:
        video_url: URL of the video to extend
        prompt: Text description for the continuation (e.g., "The camera pulls back to reveal...")
        duration: Extension duration in seconds (default: 5, usually 5 or 10)
        resolution: Output resolution (default: "1080p")
        aspect_ratio: Output aspect ratio (default: "16:9")
        generate_audio: Whether to generate/extend audio (default: True)
        model: Model ID to use (default: seedance-1-5-pro-video-extend)
        poll_interval: Seconds between status polling (default: 1.0)
    
    Returns:
        dict: Task result containing extended video information
    
    Raises:
        Exception: If video extension fails
    """
    # Build the full prompt with parameters
    full_prompt = f"{prompt}  --duration {duration}"
    
    # Build content list
    content = [
        {
            "type": "text",
            "text": full_prompt
        },
        {
            "type": "video_url",
            "video_url": {
                "url": video_url
            }
        }
    ]
    
    # Create the extension task
    print("----- Creating video extension task -----")
    create_result = _client.content_generation.tasks.create(
        model=model,
        content=content
    )
    print(f"Task created with ID: {create_result.id}")
    
    # Poll for completion
    print("----- Polling task status -----")
    task_id = create_result.id
    
    while True:
        get_result = _client.content_generation.tasks.get(task_id=task_id)
        status = get_result.status
        
        if status == "succeeded":
            print("----- Task succeeded -----")
            return get_result
        elif status == "failed":
            print("----- Task failed -----")
            raise Exception(f"Video extension failed: {get_result.error}")
        else:
            print(f"Current status: {status}, retrying in {poll_interval}s...")
            time.sleep(poll_interval)

