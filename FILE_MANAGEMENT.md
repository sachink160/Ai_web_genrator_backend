# Website File Management System

## Overview

The enhanced `/api/generate-website` endpoint now automatically saves generated multi-page websites in a structured folder format within the `Backend/webtemplates` directory.

## Features

### 1. **Structured File Storage**
- Each generated website is saved in its own unique folder
- Folder naming: `{website_name}_{timestamp}`
- Example: `Coffee_Shop_20260101_120330`

### 2. **Automatic File Organization**
Each website folder contains:
- **HTML files** - One file per page (e.g., `home.html`, `about.html`, `menu.html`, `contact.html`)
- **CSS file** - Single global `style.css` file containing all page styles
- **index.html** - Auto-redirect to the home page
- **metadata.json** - Website metadata (plan, description, creation date, etc.)

### 3. **Internal Link Management**
- Automatically fixes internal page navigation links
- Converts references like `href="about"` to `href="about.html"`
- Ensures all navigation links work correctly

### 4. **CSS Extraction & Consolidation**
- Extracts CSS from `<style>` tags in HTML
- Creates a single global `style.css` file
- Updates HTML files to reference the external stylesheet
- Removes inline `<style>` tags from HTML

## File Structure Example

```
Backend/webtemplates/
└── Coffee_Shop_20260101_120330/
    ├── index.html           # Redirects to home.html
    ├── home.html            # Homepage
    ├── about.html           # About page
    ├── menu.html            # Menu page
    ├── contact.html         # Contact page
    ├── style.css            # Global stylesheet
    └── metadata.json        # Website metadata
```

## API Response

The `/api/generate-website` endpoint now returns additional information:

```json
{
  "step": "complete",
  "status": "completed",
  "progress": 100,
  "message": "✓ Website generation complete",
  "data": {
    "pages": {
      "home": {"html": "...", "css": "..."},
      "about": {"html": "...", "css": "..."},
      ...
    },
    "image_urls": {...},
    "plan": {...},
    "folder_path": "d:\\...\\Backend\\webtemplates\\Coffee_Shop_20260101_120330",
    "saved_files": {
      "home": "d:\\...\\home.html",
      "about": "d:\\...\\about.html",
      ...
    }
  }
}
```

## Workflow Steps

The website generation workflow now includes 5 steps:

1. **Planning** - Generate website structure and page plan
2. **Image Description** - Create image descriptions for each section
3. **Image Generation** - Generate images using DALL-E 3
4. **HTML Generation** - Create HTML/CSS for each page
5. **File Storage** ✨ NEW - Save website files in structured folders

## Usage

### Basic Usage

```python
import requests

# Generate website
response = requests.post(
    "http://localhost:8000/api/generate-website",
    json={
        "description": "A modern coffee shop website with home, about, menu, and contact pages"
    },
    stream=True
)

# Process streaming response
for line in response.iter_lines():
    if line:
        data = json.loads(line.decode('utf-8').replace('data: ', ''))
        print(f"Progress: {data['progress']}% - {data['message']}")
        
        # Final result
        if data['step'] == 'complete':
            folder_path = data['data']['folder_path']
            print(f"Website saved to: {folder_path}")
```

### Accessing Saved Files

After generation, you can find your website files at:
- Windows: `d:\Ai_project_landing_page\Ai_project_multi_page\Backend\webtemplates\{website_folder}`
- The exact path is provided in the API response under `data.folder_path`

### Opening the Website

1. Navigate to the website folder
2. Open `index.html` in your browser
3. Or directly open any page (e.g., `home.html`)

## Configuration

### Custom Website Name

The website folder name is automatically generated from:
1. Website plan name (if provided by AI)
2. First 3 words of the description
3. Timestamp for uniqueness

### Custom Base Directory

You can customize the base templates directory by modifying the `WebsiteFileManager` initialization:

```python
from app.file_manager import WebsiteFileManager

# Custom directory
file_manager = WebsiteFileManager(base_templates_dir="/path/to/custom/templates")
```

## File Manager Class

The `WebsiteFileManager` class (in `app/file_manager.py`) provides the following methods:

### Core Methods

- `create_website_folder(website_name)` - Create a unique website folder
- `save_website_files(pages, website_folder)` - Save HTML/CSS files
- `fix_internal_links(website_folder, pages)` - Fix navigation links
- `create_index_html(website_folder, home_page)` - Create redirect page
- `save_metadata(website_folder, metadata)` - Save website metadata
- `save_complete_website(pages, plan, description, ...)` - Complete workflow

### Utility Methods

- `extract_css_from_html(html)` - Extract CSS from style tags
- `add_css_link_to_html(html, css_filename)` - Add stylesheet link

## Benefits

✅ **Organized Storage** - Each website in its own folder
✅ **Easy Access** - Find and reuse generated websites
✅ **Proper Structure** - Standard web project structure
✅ **Working Links** - All internal navigation works correctly
✅ **Clean Code** - Separated CSS, clean HTML
✅ **Metadata Tracking** - Track generation details and plans
✅ **Ready to Deploy** - Files ready for web hosting

## Future Enhancements

Potential improvements:
- [ ] Copy generated images to website folder
- [ ] Generate a README for each website
- [ ] Create a zip archive for easy download
- [ ] Add support for custom assets/resources
- [ ] Generate sitemap.xml
- [ ] Add robots.txt

## Troubleshooting

### Files not saved
- Check `Backend/webtemplates` directory exists
- Verify write permissions
- Check backend logs for errors

### Links not working
- Ensure all pages are in the same folder
- Check that `fix_internal_links()` was called
- Verify HTML contains proper href attributes

### CSS not loading
- Check that `style.css` exists in the folder
- Verify HTML contains `<link rel="stylesheet" href="style.css">`
- Check browser console for 404 errors

## License

Part of the AI Landing Page Generator project.
