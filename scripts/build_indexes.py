import os
import json
import math
import shutil
import base64
import hashlib
from collections import Counter
import re
import yaml

# 配置路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECTS_DIR = os.path.join(BASE_DIR, 'projects')
CONFIG_PATH = os.path.join(BASE_DIR, 'config', 'site-settings.yaml')
OUTPUT_DIR = os.path.join(BASE_DIR, 'public', 'api')
PAGES_DIR = os.path.join(OUTPUT_DIR, 'pages')
DETAILS_DIR = os.path.join(OUTPUT_DIR, 'details')
TAGS_DIR = os.path.join(OUTPUT_DIR, 'tags')

def load_config():
    """Load configuration from site-settings.yaml"""
    default_config = {"items_per_page": 200}
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Warning: Failed to load config file: {e}. Using defaults.")
    return default_config

# 加载配置
CONFIG = load_config()
ITEMS_PER_PAGE = CONFIG.get('items_per_page', 200)

# 预定义 Tag 分类 (基于甲方提供的图片)
TAG_CATEGORIES = [
    {
        "name": "发布者",
        "tags": ["3FUI 核心成员", "普通成员"]
    },
    {
        "name": "规格",
        "tags": ["2160p", "1440p", "1080p", "720p", "其他分辨率", "高帧率"]
    },
    {
        "name": "编码",
        "tags": ["H.266/VVC", "AV1", "H.265/HEVC", "H.264/AVC"]
    },
    {
        "name": "处理",
        "tags": ["直接压制", "滤镜", "AI", "视频帧服务器", "后期制作"]
    },
    {
        "name": "下载源",
        "tags": ["磁力", "百度云", "蓝奏云", "123网盘", "夸克", "直链"]
    }
]

def safe_filename(name):
    """
    Generate a safe filename for tags.
    Replaces unsafe characters with underscores to keep it human-readable.
    """
    # Replace invalid characters for Windows/Linux filesystems
    # < > : " / \ | ? *
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', name)
    # Strip leading/trailing spaces and dots (Windows doesn't like trailing dots)
    sanitized = sanitized.strip().strip('.')
    
    if not sanitized:
        # Fallback to hash if sanitized name is empty (e.g. tag was just "???")
        return hashlib.md5(name.encode('utf-8')).hexdigest()
        
    return sanitized

def get_all_projects():
    """遍历 projects 目录获取所有项目文件"""
    projects = []
    tag_counter = Counter()
    
    # Store items by tag for generating tag files
    items_by_tag = {}

    for root, _, files in os.walk(PROJECTS_DIR):
        for file in files:
            if file.endswith('.json'):
                full_path = os.path.join(root, file)
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                        # 生成 ID
                        rel_path = os.path.relpath(full_path, PROJECTS_DIR)
                        project_id = os.path.splitext(rel_path.replace(os.sep, '/'))[0]
                        
                        # 收集 Tags
                        tags = data.get("basic", {}).get("tags", [])
                        for t in tags:
                            tag_counter[t] += 1
                            if t not in items_by_tag:
                                items_by_tag[t] = []

                        # 极简清洗逻辑
                        clean_data = {
                            "id": project_id,
                            "basic": data.get("basic", {}),
                            "meta": data.get("meta", {}),
                            "source": data.get("source", {}),
                            "download": data.get("download", {})
                        }
                        
                        # Add to tags collection (using minimal info)
                        minimal_info = {
                            "id": project_id,
                            "basic": {
                                "title": clean_data["basic"].get("title"),
                                "tags": clean_data["basic"].get("tags")
                            },
                            "meta": clean_data["meta"]
                        }
                        for t in tags:
                            items_by_tag[t].append(minimal_info)
                            
                        projects.append(clean_data)
                except Exception as e:
                    print(f"Error reading {file}: {e}")
    return projects, tag_counter, items_by_tag

def main():
    print(f"Starting build process (Paged, {ITEMS_PER_PAGE} items/page)...")
    
    # 1. 准备输出目录
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(PAGES_DIR)
    os.makedirs(DETAILS_DIR)
    os.makedirs(TAGS_DIR)

    # 2. 读取所有项目
    all_projects, tag_stats, items_by_tag = get_all_projects()
    all_projects.sort(key=lambda x: x['id'], reverse=True) 
    
    total_items = len(all_projects)
    print(f"Found {total_items} projects.")

    # 3. 生成分页文件 (List View)
    total_pages = math.ceil(total_items / ITEMS_PER_PAGE)
    if total_pages == 0: total_pages = 1

    for i in range(total_pages):
        start = i * ITEMS_PER_PAGE
        end = start + ITEMS_PER_PAGE
        page_data = {
            "page": i + 1,
            "total_pages": total_pages,
            "total_items": total_items,
            "items": all_projects[start:end]
        }
        page_path = os.path.join(PAGES_DIR, f"{i+1}.json")
        with open(page_path, 'w', encoding='utf-8') as f:
            json.dump(page_data, f, ensure_ascii=False, indent=2)

    # 3.5 Generate Detail Files
    for project in all_projects:
        # Create directory structure for details if needed (e.g. details/2026/project.json)
        # But here we just use flat hash or ID structure?
        # Actually, using the ID path structure is best.
        
        # ID is like "2026/example_project"
        # Output to "public/api/details/2026/example_project.json"
        
        detail_path = os.path.join(DETAILS_DIR, f"{project['id']}.json")
        detail_dir = os.path.dirname(detail_path)
        if not os.path.exists(detail_dir):
            os.makedirs(detail_dir)
            
        with open(detail_path, 'w', encoding='utf-8') as f:
            json.dump(project, f, ensure_ascii=False, indent=2)

    # 3.8 Generate all.json (Minimal Index)
    all_projects_minimal = []
    for p in all_projects:
        all_projects_minimal.append({
            "id": p["id"],
            "basic": {
                "title": p["basic"].get("title")
            },
            "meta": {
                "author": p["meta"].get("author")
            }
        })
    with open(os.path.join(OUTPUT_DIR, 'all.json'), 'w', encoding='utf-8') as f:
        json.dump(all_projects_minimal, f, ensure_ascii=False, indent=2)

    # 4. 生成 Tags 索引文件 & Tag Detail Files
    
    # 4.1 Tag Map (Name -> Hash)
    tag_map = {}
    for tag in tag_stats.keys():
        tag_map[tag] = safe_filename(tag)
        
    # 4.2 Generate individual tag files
    for tag, items in items_by_tag.items():
        tag_filename = tag_map[tag]
        tag_file_path = os.path.join(TAGS_DIR, f"{tag_filename}.json")
        
        tag_data = {
            "tag": tag,
            "count": len(items),
            "items": items # List of minimal project info
        }
        with open(tag_file_path, 'w', encoding='utf-8') as f:
            json.dump(tag_data, f, ensure_ascii=False, indent=2)

    # 4.3 Main tags.json
    all_tags = set(tag_stats.keys())
    categorized_tags = set()
    for cat in TAG_CATEGORIES:
        for t in cat["tags"]:
            categorized_tags.add(t)

    uncategorized = list(all_tags - categorized_tags)
    uncategorized.sort()

    final_categories = [c for c in TAG_CATEGORIES]
    if uncategorized:
        final_categories.append({
            "name": "其他标签",
            "tags": uncategorized
        })

    tags_data = {
        "categories": final_categories,
        "stats": tag_stats,
        "map": tag_map # Frontend needs this to know which file to fetch
    }
    with open(os.path.join(OUTPUT_DIR, 'tags.json'), 'w', encoding='utf-8') as f:
        json.dump(tags_data, f, ensure_ascii=False, indent=2)

    # 5. 生成主入口 index.json
    index_data = {
        "site_name": "3FUI-Studios",
        "total_items": total_items,
        "total_pages": total_pages,
        "items_per_page": ITEMS_PER_PAGE,
        "first_page_url": "/api/pages/1.json",
        "tags_url": "/api/tags.json",
        "all_projects_url": "/api/all.json"
    }
    with open(os.path.join(OUTPUT_DIR, 'index.json'), 'w', encoding='utf-8') as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)

    print(f"Build complete: Generated {total_pages} pages and tags index.")

if __name__ == "__main__":
    main()
