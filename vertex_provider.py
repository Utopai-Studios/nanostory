import os
from dotenv import load_dotenv
import vertexai
from vertexai.generative_models import GenerativeModel, Part, Image

# Load environment variables from .env file
load_dotenv()

# Initialize Vertex AI
_project_id = os.getenv("VERTEX_PROJECT_ID")
_location = os.getenv("VERTEX_LOCATION")

vertexai.init(project=_project_id, location=_location)

# Latest Gemini 3 Pro model
DEFAULT_MODEL = "gemini-3-pro-preview"


def generate_text(
    prompt: str,
    image_url: str = None,
    image_path: str = None,
    image_bytes: bytes = None,
    model: str = DEFAULT_MODEL,
    max_output_tokens: int = 8192,
    temperature: float = 1.0,
) -> str:
    """
    Generate text using Vertex AI Gemini model.
    
    Args:
        prompt: Text prompt/question
        image_url: Optional URL of an image (for vision tasks)
        image_path: Optional local file path of an image
        image_bytes: Optional raw image bytes
        model: Model ID to use (default: gemini-3-pro-preview)
        max_output_tokens: Maximum tokens in response (default: 8192)
        temperature: Sampling temperature (default: 1.0)
    
    Returns:
        str: Generated text response
    
    Note: Only one of image_url, image_path, or image_bytes should be provided.
    """
    # Initialize the model
    gemini_model = GenerativeModel(model)
    
    # Build content parts
    content_parts = []
    
    # Add image if provided
    if image_url:
        content_parts.append(Part.from_uri(image_url, mime_type=_get_mime_type(image_url)))
    elif image_path:
        content_parts.append(Part.from_image(Image.load_from_file(image_path)))
    elif image_bytes:
        content_parts.append(Part.from_data(image_bytes, mime_type="image/jpeg"))
    
    # Add text prompt
    content_parts.append(prompt)
    
    # Generate response
    response = gemini_model.generate_content(
        content_parts,
        generation_config={
            "max_output_tokens": max_output_tokens,
            "temperature": temperature,
        }
    )
    
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
def chat(prompt: str, model: str = DEFAULT_MODEL) -> str:
    """
    Simple text-to-text generation.
    
    Args:
        prompt: Text prompt/question
        model: Model ID to use
    
    Returns:
        str: Generated text response
    """
    return generate_text(prompt=prompt, model=model)


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

