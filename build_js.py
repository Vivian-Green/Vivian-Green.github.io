import os
import re
import json
import datetime
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

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

def get_post_date(filename):
    """Extract date from filename in YYYYMMDDHHMM format"""
    # Extract the timestamp part from filename like "202312011230actual_title.md"
    date_match = re.search(r'^(\d{12})', filename)
    if date_match:
        date_str = date_match.group(1)
        try:
            return datetime.datetime.strptime(date_str, '%Y%m%d%H%M')
        except ValueError:
            pass
    
    # Fallback: use file modification time
    file_path = os.path.join(POSTS_DIR, filename)
    if os.path.exists(file_path):
        timestamp = os.path.getmtime(file_path)
        return datetime.datetime.fromtimestamp(timestamp)
    
    # Final fallback: current time
    return datetime.datetime.now()

def escape_xml(text):
    """Escape XML special characters"""
    return (text.replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&apos;'))

def generate_simple_rss(posts_data, base_url="https://vivianswebsite.neocities.org"):    
    rss_template = '''<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
<channel>
    <title>ViviansUsername's Website Blog Thing</title>
    <link>{base_url}</link>
    <description>I will infodump at you about whatever I am working on, and probably plug my youtube channel. Usually programming, with python, godot, linux mint, and occasionally some light web dev, as I try to make something portfolioesc happen.</description>
    <language>en-us</language>
    <lastBuildDate>{build_date}</lastBuildDate>
    
    {items}
</channel>
</rss>'''

    item_template = '''
    <item>
        <title>{title}</title>
        <link>{url}</link>
        <description>{description}</description>
        <pubDate>{pub_date}</pubDate>
        <guid>{url}</guid>
    </item>'''

    items = []
    for post in posts_data:
        slug = os.path.splitext(post['filename'])[0]
        # Remove the timestamp from the slug for cleaner URLs
        clean_slug = re.sub(r'^\d{12}', '', slug)
        
        # Use hash-based URLs that work with your single-page app
        post_url = f"{base_url}/#post-{clean_slug}"
        
        items.append(item_template.format(
            title=escape_xml(post['title']),
            url=post_url,
            description=escape_xml(post['subtitle'] or post['title']),
            pub_date=get_post_date(post['filename']).strftime('%a, %d %b %Y %H:%M:%S GMT')
        ))
    
    rss_content = rss_template.format(
        base_url=base_url,
        build_date=datetime.datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT'),
        items=''.join(items)
    )
    
    return rss_content

def build_output_files(posts_dir):
    posts_data = []

    # foreach .md in dir
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

    # sort posts by most recent first (using the date from filename)
    posts_data.sort(key=lambda x: get_post_date(x['filename']), reverse=True)

    # split into recent and whatever else for faster initial loading
    recent_posts = posts_data[:2]
    older_posts = posts_data[2:]

    # generate JSON versions (for Neocities)
    with open('recentPosts.json', 'w', encoding='utf-8') as f:
        json.dump(recent_posts, f, indent=4, ensure_ascii=False)
    
    with open('olderPosts.json', 'w', encoding='utf-8') as f:
        json.dump(older_posts, f, indent=4, ensure_ascii=False)

    # generate JSONP versions (for GitHub Pages)
    with open('recentPosts.js', 'w', encoding='utf-8') as f:
        f.write(f'handleRecentPosts({json.dumps(recent_posts, indent=4, ensure_ascii=False)});')
    
    with open('olderPosts.js', 'w', encoding='utf-8') as f:
        f.write(f'handleOlderPosts({json.dumps(older_posts, indent=4, ensure_ascii=False)});')

    print("Generated files successfully!")
    print("- JSON (for Neocities): recentPosts.json, olderPosts.json")
    print("- JSONP (for GitHub): recentPosts.js, olderPosts.js")
    
    print("Building RSS feed...")
    rss_content = generate_simple_rss(posts_data)
    
    # Write RSS feed
    with open('rss.xml', 'w', encoding='utf-8') as f:
        f.write(rss_content)
    
    print("- RSS: rss.xml")

if __name__ == '__main__':
    build_output_files(POSTS_DIR)
