import re
import argparse
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import List, Optional

from seedance_provider import generate_video, extend_video


@dataclass
class Scene:
    """Represents a single scene/shot in a script."""
    time_range: str  # e.g., "0-5s", "5-10s"
    visual_description: str  # 画面/动作/特效
    dialogue: str  # 台词
    audio: str  # BGM/音效
    duration: int = 5  # Estimated duration in seconds


@dataclass
class Script:
    """Represents a complete script with multiple scenes."""
    title: str
    characters: dict  # {role_name: description}
    scenes: List[Scene]
    

def parse_script_md(md_path: str) -> List[Script]:
    """
    Parse a script markdown file and extract all scripts.
    
    Args:
        md_path: Path to the markdown file
        
    Returns:
        List of Script objects
    """
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    scripts = []
    
    # Split by script sections (### 剧本标题)
    script_sections = re.split(r'(?=### 剧本标题)', content)
    
    for section in script_sections:
        if not section.strip() or '### 剧本标题' not in section:
            continue
            
        # Extract title
        title_match = re.search(r'### 剧本标题[：:]\s*(.+)', section)
        title = title_match.group(1).strip() if title_match else "Unknown"
        
        # Extract characters
        characters = {}
        char_matches = re.findall(r'\*\s*\*\*(角色[AB].*?)\*\*[：:]\s*(.+)', section)
        for role, desc in char_matches:
            characters[role.strip()] = desc.strip()
        
        # Extract table rows (scenes)
        scenes = []
        # Match table rows: | time | visual | dialogue | audio |
        table_pattern = r'\|\s*\*\*(\d+-\d+s|结尾)\*\*\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|'
        
        for match in re.finditer(table_pattern, section):
            time_range = match.group(1)
            visual = match.group(2).strip()
            dialogue = match.group(3).strip()
            audio = match.group(4).strip()
            
            # Clean up HTML tags
            visual = re.sub(r'<br\s*/?>', ' ', visual)
            dialogue = re.sub(r'<br\s*/?>', ' ', dialogue)
            audio = re.sub(r'<br\s*/?>', ' ', audio)
            
            # Parse duration from time range
            if time_range == "结尾":
                duration = 3  # Short ending shot
            else:
                try:
                    start, end = time_range.replace('s', '').split('-')
                    duration = int(end) - int(start)
                except:
                    duration = 5
            
            scenes.append(Scene(
                time_range=time_range,
                visual_description=visual,
                dialogue=dialogue,
                audio=audio,
                duration=duration,
            ))
        
        if scenes:
            scripts.append(Script(
                title=title,
                characters=characters,
                scenes=scenes,
            ))
    
    return scripts


def build_video_prompt(scene: Scene, script: Script, style: str = "cinematic") -> str:
    """
    Build a video generation prompt from a scene.
    
    Args:
        scene: The scene to generate
        script: The parent script (for context)
        style: Visual style hint
        
    Returns:
        str: Video generation prompt
    """
    # Extract key visual elements
    visual = scene.visual_description
    
    # Remove markdown formatting
    visual = re.sub(r'\[.*?\]', '', visual)  # Remove [特写], [中景], etc. but keep the content
    visual = re.sub(r'\*\*.*?\*\*', '', visual)  # Remove bold
    
    # Build prompt with style hints
    prompt = f"{visual}. {style} style, high quality, detailed"
    
    return prompt


def generate_videos_from_script(
    md_path: str,
    output_dir: str = None,
    script_index: int = None,
    duration: int = 5,
    dry_run: bool = False,
) -> List[dict]:
    """
    Generate videos for all scenes in a script markdown file.
    
    Args:
        md_path: Path to the script markdown file
        output_dir: Directory to save results (default: same as input)
        script_index: Generate only this script (0-indexed), or None for all
        duration: Video duration per scene (default: 5)
        dry_run: If True, only print prompts without generating
        
    Returns:
        List of generation results
    """
    md_path = Path(md_path)
    
    if output_dir is None:
        output_dir = md_path.parent / "videos" / md_path.stem
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Parse scripts
    scripts = parse_script_md(str(md_path))
    print(f"📖 Found {len(scripts)} scripts in {md_path.name}")
    
    if script_index is not None:
        if script_index >= len(scripts):
            raise ValueError(f"Script index {script_index} out of range (0-{len(scripts)-1})")
        scripts = [scripts[script_index]]
    
    results = []
    
    for i, script in enumerate(scripts):
        print(f"\n{'='*60}")
        print(f"🎬 Script {i+1}: {script.title}")
        print(f"{'='*60}")
        print(f"Characters: {script.characters}")
        print(f"Scenes: {len(script.scenes)}")
        
        for j, scene in enumerate(script.scenes):
            print(f"\n--- Scene {j+1}: {scene.time_range} ---")
            
            prompt = build_video_prompt(scene, script)
            print(f"Prompt: {prompt[:100]}...")
            
            if dry_run:
                print("(dry run - skipping generation)")
                continue
            
            try:
                result = generate_video(
                    prompt=prompt,
                    duration=duration,
                    camera_fixed=False,
                )
                
                # Save result info
                result_info = {
                    "script_title": script.title,
                    "scene_index": j,
                    "time_range": scene.time_range,
                    "prompt": prompt,
                    "result": result,
                }
                results.append(result_info)
                
                print(f"✅ Generated: {result}")
                
            except Exception as e:
                print(f"❌ Failed: {e}")
                results.append({
                    "script_title": script.title,
                    "scene_index": j,
                    "error": str(e),
                })
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description="从剧本 Markdown 文件批量生成视频",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 预览所有剧本（不生成视频）
  python videogen.py story_面试.md --dry-run
  
  # 生成第一个剧本的所有场景
  python videogen.py story_面试.md --script 0
  
  # 生成所有剧本的所有场景
  python videogen.py story_面试.md
  
  # 指定输出目录
  python videogen.py story_面试.md -o ./output_videos
        """
    )
    
    parser.add_argument(
        "script_file",
        help="剧本 Markdown 文件路径"
    )
    parser.add_argument(
        "-s", "--script",
        type=int,
        default=None,
        help="只生成指定剧本 (0-indexed)"
    )
    parser.add_argument(
        "-d", "--duration",
        type=int,
        default=5,
        help="每个场景的视频时长 (默认: 5秒)"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="输出目录"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅预览 prompts，不实际生成视频"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🎥 剧本视频生成器")
    print("=" * 60)
    print(f"输入文件: {args.script_file}")
    print(f"视频时长: {args.duration}s")
    print(f"Dry run: {args.dry_run}")
    
    results = generate_videos_from_script(
        md_path=args.script_file,
        output_dir=args.output,
        script_index=args.script,
        duration=args.duration,
        dry_run=args.dry_run,
    )
    
    print("\n" + "=" * 60)
    print(f"✨ 完成! 处理了 {len(results)} 个场景")


if __name__ == "__main__":
    main()
