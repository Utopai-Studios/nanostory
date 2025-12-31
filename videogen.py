from seedance_provider import generate_video

# Example prompts
EXAMPLE_PROMPTS = [
    "A character is struck by a gunshot, his body jerks violently as dark blood bursts outward, splattering across the surrounding space in a sudden, shocking moment.",
    "A serene sunset over the ocean, waves gently rolling onto a sandy beach with golden light reflecting off the water.",
    "A futuristic cityscape at night, neon lights flickering, flying cars zooming between towering skyscrapers.",
]


if __name__ == "__main__":
    # Use the first example prompt
    prompt = EXAMPLE_PROMPTS[0]
    
    print(f"Generating video for prompt:\n{prompt}\n")
    
    # Generate video (text-to-video)
    result = generate_video(
        prompt=prompt,
        duration=5,
        camera_fixed=False,
    )
    
    print("\n----- Result -----")
    print(result)
    
    # Example: Image-to-video generation (uncomment to use)
    # result = generate_video(
    #     prompt="A gentle breeze moves through the scene",
    #     reference_image_url="https://your-image-url.com/image.png",
    #     duration=5,
    # )

