import os
import re
import json

# Path to the folder where markdown posts are stored
POSTS_DIR = './posts'

def parse_markdown(content):
    # Extract title (first level header `#`)
    title_match = re.search(r'^# (.+)', content, re.MULTILINE)
    title = title_match.group(1) if title_match else 'Untitled'

    # Extract subtitle (second level header `##`)
    subtitle_match = re.search(r'^## (.+)', content, re.MULTILINE)
    subtitle = subtitle_match.group(1) if subtitle_match else ''
    
    if subtitle == "":  # if contains no ##, try first ###
        subtitle_match2 = re.search(r'^### (.+)', content, re.MULTILINE)
        subtitle = subtitle_match2.group(1) if subtitle_match2 else ''

    # Extract thumbnail (first image URL `![](url)`)
    thumbnail_match = re.search(r'!\[.*?\]\((.*?)\)', content)
    thumbnail = thumbnail_match.group(1) if thumbnail_match else ''

    return {
        'title': title,
        'subtitle': subtitle,
        'thumbnail': thumbnail,
        'content': content
    }

def build_json_files(posts_dir):
    posts_data = []

    # Iterate over all markdown files in the directory
    for filename in os.listdir(posts_dir):
        if filename.endswith('.md'):
            with open(os.path.join(posts_dir, filename), 'r', encoding='utf-8') as f:
                content = f.read()
                post_data = parse_markdown(content)
                posts_data.append({
                    'filename': filename,
                    'title': post_data['title'],
                    'subtitle': post_data['subtitle'],
                    'thumbnail': post_data['thumbnail'],
                    'content': post_data['content']
                })

    # Sort posts by filename (reverse chronological order)
    posts_data.sort(key=lambda x: x['filename'], reverse=True)

    # Split into recent posts (first 2) and older posts (the rest)
    recent_posts = posts_data[:2]
    older_posts = posts_data[2:]

    # Write recent posts to JSON
    with open('recentPosts.json', 'w', encoding='utf-8') as f:
        json.dump(recent_posts, f, indent=4, ensure_ascii=False)

    # Write older posts to JSON
    with open('olderPosts.json', 'w', encoding='utf-8') as f:
        json.dump(older_posts, f, indent=4, ensure_ascii=False)

    print("recentPosts.json and olderPosts.json have been generated successfully!")

if __name__ == '__main__':
    build_json_files(POSTS_DIR)
