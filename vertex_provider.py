import os
from dotenv import load_dotenv
from google import genai
from google.genai.types import GenerateContentConfig

# Load environment variables from .env file
load_dotenv()

# Initialize Vertex AI client
_project_id = os.getenv("VERTEX_PROJECT_ID")
_location = os.getenv("VERTEX_LOCATION", "global")

# Override to global for Gemini 3 models (required)
_location = "global"

_client = genai.Client(
    vertexai=True,
    project=_project_id,
    location=_location,
)

# Gemini 3 Pro model
DEFAULT_MODEL = "gemini-3-pro-preview"


def generate_text(
    prompt: str,
    image_path: str = None,
    image_url: str = None,
    image_bytes: bytes = None,
    model: str = DEFAULT_MODEL,
    max_output_tokens: int = 8192,
    temperature: float = 1.0,
    system_instruction: str = None,
) -> str:
    """
    Generate text using Vertex AI Gemini model.
    
    Args:
        prompt: Text prompt/question
        image_path: Optional local file path of an image
        image_url: Optional URL of an image (for vision tasks)
        image_bytes: Optional raw image bytes
        model: Model ID to use (default: gemini-3-pro-preview)
        max_output_tokens: Maximum tokens in response (default: 8192)
        temperature: Sampling temperature (default: 1.0)
        system_instruction: Optional system instruction
    
    Returns:
        str: Generated text response
    
    Note: Only one of image_path, image_url, or image_bytes should be provided.
    """
    from PIL import Image
    import io
    
    # Build content parts
    content_parts = []
    
    # Add image if provided
    if image_path:
        pil_image = Image.open(image_path)
        content_parts.append(pil_image)
    elif image_url:
        import urllib.request
        with urllib.request.urlopen(image_url) as response:
            img_bytes = response.read()
        pil_image = Image.open(io.BytesIO(img_bytes))
        content_parts.append(pil_image)
    elif image_bytes:
        pil_image = Image.open(io.BytesIO(image_bytes))
        content_parts.append(pil_image)
    
    # Add text prompt
    content_parts.append(prompt)
    
    # Build config
    config = {
        "max_output_tokens": max_output_tokens,
        "temperature": temperature,
    }
    if system_instruction:
        config["system_instruction"] = system_instruction
    
    # Generate response
    response = _client.models.generate_content(
        model=model,
        contents=content_parts if len(content_parts) > 1 else prompt,
        config=config,
    )
    
    if response is None or not response.text:
        raise Exception("Empty response from Vertex AI")
    
    return response.text


def _get_mime_type(url: str) -> str:
    """Infer MIME type from URL extension."""
    url_lower = url.lower()
    if url_lower.endswith(".png"):
        return "image/png"
    elif url_lower.endswith(".gif"):
        return "image/gif"
    elif url_lower.endswith(".webp"):
        return "image/webp"
    else:
        return "image/jpeg"


# Convenience function for text-only generation
def chat(prompt: str, model: str = DEFAULT_MODEL, system_instruction: str = None) -> str:
    """
    Simple text-to-text generation.
    
    Args:
        prompt: Text prompt/question
        model: Model ID to use
        system_instruction: Optional system instruction
    
    Returns:
        str: Generated text response
    """
    return generate_text(
        prompt=prompt,
        model=model,
        system_instruction=system_instruction,
    )


# Convenience function for image analysis
def analyze_image(
    image_path: str = None,
    image_url: str = None,
    prompt: str = "Describe this image in detail.",
    model: str = DEFAULT_MODEL,
) -> str:
    """
    Analyze an image and generate a text description.
    
    Args:
        image_path: Local path to image file
        image_url: URL of the image
        prompt: Question/instruction about the image
        model: Model ID to use
    
    Returns:
        str: Generated text response about the image
    """
    return generate_text(
        prompt=prompt,
        image_path=image_path,
        image_url=image_url,
        model=model,
    )
