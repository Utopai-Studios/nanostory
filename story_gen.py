import os
import argparse
from datetime import datetime
from pathlib import Path
from vertex_provider import generate_text

# Load system prompt from file
SCRIPT_DIR = Path(__file__).parent
SYSTEM_PROMPT_PATH = SCRIPT_DIR / "story_gen_prompt.txt"

# Default output directory
DEFAULT_OUTPUT_DIR = SCRIPT_DIR / "generated_stories"


def load_system_prompt() -> str:
    """Load the system prompt from story_gen_prompt.txt"""
    with open(SYSTEM_PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read()


def generate_story(
    topic: str,
    count: int = 3,
    system_prompt: str = None,
) -> str:
    """
    Generate stories based on a topic.
    
    Args:
        topic: The theme or keywords for story generation (e.g., 面试、相亲、借钱)
        count: Number of stories to generate (default: 3)
        system_prompt: Custom system prompt (uses default if None)
    
    Returns:
        str: Generated stories in markdown format
    """
    if system_prompt is None:
        system_prompt = load_system_prompt()
    
    # Build the full prompt
    user_prompt = f"""
{system_prompt}

---

## 用户请求
主题/关键词: {topic}
生成数量: {count} 个剧本

请根据以上主题，按照 Output Format 生成 {count} 个不同场景的反转短剧剧本。
"""
    
    # Call Vertex AI
    response = generate_text(
        prompt=user_prompt,
        temperature=1.0,
        max_output_tokens=8192,
    )
    
    return response


def save_story(content: str, topic: str, output_dir: Path, index: int = None) -> Path:
    """
    Save a story to a text file.
    
    Args:
        content: Story content
        topic: Topic used for filename
        output_dir: Directory to save the file
        index: Optional index for batch generation
    
    Returns:
        Path: Path to the saved file
    """
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_topic = "".join(c if c.isalnum() or c in "._-" else "_" for c in topic)[:30]
    
    if index is not None:
        filename = f"story_{safe_topic}_{timestamp}_{index}.md"
    else:
        filename = f"story_{safe_topic}_{timestamp}.md"
    
    filepath = output_dir / filename
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    
    return filepath


def batch_generate(
    topics: list[str],
    stories_per_topic: int = 3,
    output_dir: Path = None,
) -> list[Path]:
    """
    Batch generate stories for multiple topics.
    
    Args:
        topics: List of topics/keywords
        stories_per_topic: Number of stories per topic (default: 3)
        output_dir: Output directory (uses default if None)
    
    Returns:
        list[Path]: List of paths to saved files
    """
    if output_dir is None:
        output_dir = DEFAULT_OUTPUT_DIR
    
    saved_files = []
    system_prompt = load_system_prompt()
    
    for i, topic in enumerate(topics, 1):
        print(f"\n[{i}/{len(topics)}] 生成主题: {topic}")
        print("-" * 40)
        
        try:
            content = generate_story(
                topic=topic,
                count=stories_per_topic,
                system_prompt=system_prompt,
            )
            
            filepath = save_story(content, topic, output_dir, index=i)
            saved_files.append(filepath)
            print(f"✅ 已保存: {filepath}")
            
        except Exception as e:
            print(f"❌ 生成失败: {e}")
    
    return saved_files


def main():
    parser = argparse.ArgumentParser(
        description="批量生成反转短剧剧本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 单个主题生成3个剧本
  python story_gen.py "相亲"
  
  # 多个主题，每个生成5个剧本
  python story_gen.py "面试" "借钱" "买车" -n 5
  
  # 指定输出目录
  python story_gen.py "相亲" -o ./my_stories
        """
    )
    
    parser.add_argument(
        "topics",
        nargs="+",
        help="故事主题/关键词（可以多个）"
    )
    parser.add_argument(
        "-n", "--count",
        type=int,
        default=3,
        help="每个主题生成的剧本数量 (默认: 3)"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="输出目录 (默认: ./generated_stories)"
    )
    
    args = parser.parse_args()
    
    output_dir = Path(args.output) if args.output else DEFAULT_OUTPUT_DIR
    
    print("=" * 50)
    print("🎬 反转短剧剧本生成器")
    print("=" * 50)
    print(f"主题: {', '.join(args.topics)}")
    print(f"每个主题生成: {args.count} 个剧本")
    print(f"输出目录: {output_dir}")
    
    saved_files = batch_generate(
        topics=args.topics,
        stories_per_topic=args.count,
        output_dir=output_dir,
    )
    
    print("\n" + "=" * 50)
    print(f"✨ 完成! 共生成 {len(saved_files)} 个文件")
    for f in saved_files:
        print(f"   - {f}")


if __name__ == "__main__":
    main()

