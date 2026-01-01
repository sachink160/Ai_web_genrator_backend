# Website Generation Workflow - Visual Guide

## Complete Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER REQUEST                                  │
│  "Create a coffee shop website with home, about, menu, contact" │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: PLANNING NODE                                          │
│  ────────────────────────────────────────────────────────────── │
│  • AI analyzes request                                           │
│  • Generates website plan (pages, styling, navigation)           │
│  • Output: JSON plan with page structure                         │
│                                                                   │
│  Example Output:                                                 │
│  {                                                               │
│    "pages": [                                                    │
│      {"name": "home", "sections": ["hero", "features"]},        │
│      {"name": "about", "sections": ["story", "team"]},          │
│      {"name": "menu", "sections": ["items"]},                   │
│      {"name": "contact", "sections": ["form"]}                  │
│    ],                                                            │
│    "styling": {"theme": "modern", "colors": {...}}              │
│  }                                                               │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  STEP 2A: IMAGE DESCRIPTION NODE                                │
│  ────────────────────────────────────────────────────────────── │
│  • Generate image prompts for each section                       │
│  • Tailored to business type and page context                    │
│                                                                   │
│  Example Output:                                                 │
│  {                                                               │
│    "hero": "Coffee shop interior with warm lighting...",        │
│    "features": "Coffee beans and brewing equipment...",         │
│    "testimonials": "Happy customers enjoying coffee..."         │
│  }                                                               │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  STEP 2B: IMAGE GENERATION NODE                                 │
│  ────────────────────────────────────────────────────────────── │
│  • Use DALL-E 3 to generate images                              │
│  • Download and save to /uploads                                │
│                                                                   │
│  Example Output:                                                 │
│  {                                                               │
│    "hero": "/uploads/hero_image.png",                           │
│    "features": "/uploads/features_image.png",                   │
│    "testimonials": "/uploads/testimonials_image.png"            │
│  }                                                               │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  STEP 3: HTML GENERATION NODE                                   │
│  ────────────────────────────────────────────────────────────── │
│  • Generate complete HTML/CSS for each page                      │
│  • Include images, styling, content                             │
│                                                                   │
│  Example Output:                                                 │
│  {                                                               │
│    "home": {                                                     │
│      "html": "<!DOCTYPE html><html>...<style>...</style>...</html>", │
│      "css": "body { font-family: Arial; }..."                   │
│    },                                                            │
│    "about": {...},                                              │
│    "menu": {...},                                               │
│    "contact": {...}                                             │
│  }                                                               │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  STEP 4: FILE STORAGE NODE ⭐ NEW!                              │
│  ────────────────────────────────────────────────────────────── │
│  WebsiteFileManager performs:                                    │
│                                                                   │
│  1. Create Folder:                                              │
│     Backend/webtemplates/Coffee_Shop_20260101_120330/           │
│                                                                   │
│  2. Extract CSS from all pages:                                 │
│     <style> tags → style.css                                    │
│                                                                   │
│  3. Save HTML files:                                            │
│     • home.html (with <link rel="stylesheet" href="style.css">) │
│     • about.html                                                │
│     • menu.html                                                 │
│     • contact.html                                              │
│                                                                   │
│  4. Fix internal links:                                         │
│     href="about" → href="about.html"                           │
│                                                                   │
│  5. Create index.html:                                          │
│     Redirects to home.html                                      │
│                                                                   │
│  6. Save metadata.json:                                         │
│     {created_at, description, plan, pages, image_urls}          │
│                                                                   │
│  Output:                                                         │
│  {                                                               │
│    "folder_path": "d:\...\Coffee_Shop_20260101_120330",        │
│    "saved_files": {                                             │
│      "home": "d:\...\home.html",                                │
│      "about": "d:\...\about.html",                              │
│      ...                                                         │
│    }                                                             │
│  }                                                               │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  FINAL RESULT                                                    │
│  ────────────────────────────────────────────────────────────── │
│  Structured Website Folder:                                      │
│                                                                   │
│  Backend/webtemplates/Coffee_Shop_20260101_120330/              │
│  ├── index.html          ← Redirects to home.html              │
│  ├── home.html           ← Clean HTML with CSS link            │
│  ├── about.html          ← Clean HTML with CSS link            │
│  ├── menu.html           ← Clean HTML with CSS link            │
│  ├── contact.html        ← Clean HTML with CSS link            │
│  ├── style.css           ← Global styles (extracted)           │
│  └── metadata.json       ← Website metadata                    │
│                                                                   │
│  ✅ Ready to open in browser!                                   │
│  ✅ All links work!                                             │
│  ✅ Clean code structure!                                       │
│  ✅ Easy to edit and deploy!                                    │
└─────────────────────────────────────────────────────────────────┘
```

## File Manager Operations Detail

### Operation 1: CSS Extraction

```
INPUT (from HTML generation):
┌──────────────────────────────┐
│ home.html                    │
│ <html>                       │
│   <head>                     │
│     <style>                  │
│       body { margin: 0; }    │
│       .hero { padding: 50px; }│
│     </style>                 │
│   </head>                    │
│   <body>...</body>           │
│ </html>                      │
└──────────────────────────────┘
           ↓
    [Extract CSS]
           ↓
OUTPUT (saved files):
┌──────────────────────────────┐  ┌──────────────────────────┐
│ home.html                    │  │ style.css                │
│ <html>                       │  │ /* CSS for home page */  │
│   <head>                     │  │ body { margin: 0; }      │
│     <link rel="stylesheet"   │  │ .hero { padding: 50px; } │
│           href="style.css">  │  │                          │
│   </head>                    │  │ /* CSS for about page */ │
│   <body>...</body>           │  │ .about { ... }           │
│ </html>                      │  │ ...                      │
└──────────────────────────────┘  └──────────────────────────┘
```

### Operation 2: Link Fixing

```
BEFORE (generated HTML):
┌──────────────────────────────────┐
│ <nav>                            │
│   <a href="home">Home</a>        │
│   <a href="about">About</a>      │
│   <a href="menu">Menu</a>        │
│   <a href="contact">Contact</a>  │
│ </nav>                           │
└──────────────────────────────────┘
              ↓
      [Fix Internal Links]
              ↓
AFTER (saved HTML):
┌──────────────────────────────────┐
│ <nav>                            │
│   <a href="home.html">Home</a>   │
│   <a href="about.html">About</a> │
│   <a href="menu.html">Menu</a>   │
│   <a href="contact.html">Contact</a>│
│ </nav>                           │
└──────────────────────────────────┘
✅ All links now work correctly!
```

### Operation 3: Metadata Storage

```
metadata.json
┌─────────────────────────────────────────────┐
│ {                                           │
│   "created_at": "2026-01-01T12:03:29",     │
│   "description": "A modern coffee shop...", │
│   "plan": {                                 │
│     "pages": [...],                         │
│     "styling": {...},                       │
│     "navigation": [...]                     │
│   },                                        │
│   "pages": [                                │
│     "home", "about", "menu", "contact"     │
│   ],                                        │
│   "image_urls": {                           │
│     "hero": "/uploads/hero_image.png",     │
│     "features": "/uploads/features_image.png"│
│   }                                         │
│ }                                           │
└─────────────────────────────────────────────┘
```

## API Streaming Response

```
Progress Updates (Server-Sent Events):

┌─────────────────────────────────────────────┐
│ data: {                                     │
│   "step": "planning",                       │
│   "progress": 25,                           │
│   "message": "✓ Planning complete: 4 pages"│
│ }                                           │
└─────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────┐
│ data: {                                     │
│   "step": "image_description",              │
│   "progress": 40,                           │
│   "message": "✓ Image descriptions ready"  │
│ }                                           │
└─────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────┐
│ data: {                                     │
│   "step": "image_generation",               │
│   "progress": 65,                           │
│   "message": "✓ 3 images generated"        │
│ }                                           │
└─────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────┐
│ data: {                                     │
│   "step": "html_generation",                │
│   "progress": 90,                           │
│   "message": "✓ HTML generated for 4 pages"│
│ }                                           │
└─────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────┐
│ data: {                                     │
│   "step": "file_storage",                   │
│   "progress": 95,                           │
│   "message": "Saving files..."             │
│ }                                           │
└─────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────┐
│ data: {                                     │
│   "step": "complete",                       │
│   "status": "completed",                    │
│   "progress": 100,                          │
│   "message": "✓ Website complete",         │
│   "data": {                                 │
│     "folder_path": "d:\...\Coffee_Shop...",│
│     "saved_files": {...},                   │
│     "pages": {...},                         │
│     "image_urls": {...}                     │
│   }                                         │
│ }                                           │
└─────────────────────────────────────────────┘
```

## Class Structure

```
WebsiteFileManager
├── __init__(base_templates_dir)
├── create_website_folder(website_name) → folder_path
├── extract_css_from_html(html) → (html_clean, css)
├── add_css_link_to_html(html, css_filename) → html_with_link
├── save_website_files(pages, folder, ...) → saved_files
├── fix_internal_links(folder, pages)
├── create_index_html(folder, home_page)
├── save_metadata(folder, metadata)
└── save_complete_website(...) → {folder_path, saved_files, ...}
```

## Benefits Summary

| Before | After |
|--------|-------|
| HTML returned as string only | ✅ HTML + Files saved |
| Manual file organization needed | ✅ Auto-organized folders |
| CSS embedded in HTML | ✅ External style.css |
| Broken internal links | ✅ Working .html links |
| No metadata tracking | ✅ Complete metadata.json |
| Hard to reuse/edit | ✅ Ready to edit/deploy |
