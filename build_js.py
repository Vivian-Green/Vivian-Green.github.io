import os
import re
import json

POSTS_DIR = './posts'

def parse_markdown(content):
    # extract title (first level header `#`)
    title_match = re.search(r'^# (.+)', content, re.MULTILINE)
    title = title_match.group(1) if title_match else 'Untitled'

    # extract subtitle (second level header `##`)
    subtitle_match = re.search(r'^## (.+)', content, re.MULTILINE)
    subtitle = subtitle_match.group(1) if subtitle_match else ''
    
    if subtitle == "":  # if contains no ##, try first ###
        subtitle_match2 = re.search(r'^### (.+)', content, re.MULTILINE)
        subtitle = subtitle_match2.group(1) if subtitle_match2 else ''

    # extract thumbnail (first image URL `![](url)`)
    thumbnail_match = re.search(r'!\[.*?\]\((.*?)\)', content)
    thumbnail = thumbnail_match.group(1) if thumbnail_match else ''

    return {
        'title': title,
        'subtitle': subtitle,
        'thumbnail': thumbnail,
        'content': content
    }

def build_output_files(posts_dir):
    posts_data = []

    # foreach .md in dir
    for filename in os.listdir(posts_dir): # can probably python list comprehension this one? but those aren't... readable.......
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

    # sort posts by most recent first (filename alphabetical, reversed)
    posts_data.sort(key=lambda x: x['filename'], reverse=True)

    # split into recent and whatever else for faster initial loading
    recent_posts = posts_data[:2]
    older_posts = posts_data[2:]

    # generate JSON versions (for Neocities)
    with open('recentPosts.json', 'w', encoding='utf-8') as f:
        json.dump(recent_posts, f, indent=4, ensure_ascii=False)
    
    with open('olderPosts.json', 'w', encoding='utf-8') as f:
        json.dump(older_posts, f, indent=4, ensure_ascii=False)

    # generate JSONP versions (for GitHub Pages)
    # todo: figure out how to get github pages to accept json-
    with open('recentPosts.js', 'w', encoding='utf-8') as f:
        f.write(f'handleRecentPosts({json.dumps(recent_posts, indent=4, ensure_ascii=False)});')
    
    with open('olderPosts.js', 'w', encoding='utf-8') as f:
        f.write(f'handleOlderPosts({json.dumps(older_posts, indent=4, ensure_ascii=False)});')

    print("Generated files successfully!")
    print("- JSON (for Neocities): recentPosts.json, olderPosts.json")
    print("- JSONP (for GitHub): recentPosts.js, olderPosts.js")

if __name__ == '__main__':
    build_output_files(POSTS_DIR)
