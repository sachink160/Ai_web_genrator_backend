"""
Test script for WebsiteFileManager
"""
from app.file_manager import WebsiteFileManager
import os

def test_file_manager():
    """Test the WebsiteFileManager functionality."""
    
    print("=" * 60)
    print("Testing WebsiteFileManager")
    print("=" * 60)
    
    # Initialize file manager
    file_manager = WebsiteFileManager()
    print(f"✓ File manager initialized")
    print(f"  Base directory: {file_manager.base_dir}")
    
    # Test data - sample multi-page website
    sample_pages = {
        "home": {
            "html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Home - Coffee Shop</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; }
        .hero { background: #8B4513; color: white; padding: 50px; text-align: center; }
        nav { background: #333; padding: 10px; }
        nav a { color: white; margin: 0 15px; text-decoration: none; }
    </style>
</head>
<body>
    <nav>
        <a href="home">Home</a>
        <a href="about">About</a>
        <a href="menu">Menu</a>
        <a href="contact">Contact</a>
    </nav>
    <div class="hero">
        <h1>Welcome to Our Coffee Shop</h1>
        <p>The best coffee in town!</p>
    </div>
</body>
</html>""",
            "css": ""
        },
        "about": {
            "html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>About - Coffee Shop</title>
    <style>
        .about-section { padding: 40px; }
        .about-section h2 { color: #8B4513; }
    </style>
</head>
<body>
    <nav>
        <a href="home.html">Home</a>
        <a href="about.html">About</a>
        <a href="menu.html">Menu</a>
        <a href="contact.html">Contact</a>
    </nav>
    <div class="about-section">
        <h2>About Us</h2>
        <p>We've been serving quality coffee since 2020.</p>
    </div>
</body>
</html>""",
            "css": ""
        },
        "menu": {
            "html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Menu - Coffee Shop</title>
    <style>
        .menu-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; padding: 40px; }
        .menu-item { border: 1px solid #ddd; padding: 20px; border-radius: 8px; }
    </style>
</head>
<body>
    <nav>
        <a href="home.html">Home</a>
        <a href="about.html">About</a>
        <a href="menu.html">Menu</a>
        <a href="contact.html">Contact</a>
    </nav>
    <div class="menu-grid">
        <div class="menu-item">
            <h3>Espresso</h3>
            <p>$3.50</p>
        </div>
        <div class="menu-item">
            <h3>Cappuccino</h3>
            <p>$4.50</p>
        </div>
        <div class="menu-item">
            <h3>Latte</h3>
            <p>$4.00</p>
        </div>
    </div>
</body>
</html>""",
            "css": ""
        },
        "contact": {
            "html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Contact - Coffee Shop</title>
    <style>
        .contact-section { padding: 40px; max-width: 600px; margin: 0 auto; }
        .contact-section input, .contact-section textarea { width: 100%; padding: 10px; margin: 10px 0; }
    </style>
</head>
<body>
    <nav>
        <a href="home.html">Home</a>
        <a href="about.html">About</a>
        <a href="menu.html">Menu</a>
        <a href="contact.html">Contact</a>
    </nav>
    <div class="contact-section">
        <h2>Contact Us</h2>
        <form>
            <input type="text" placeholder="Name" required>
            <input type="email" placeholder="Email" required>
            <textarea placeholder="Message" rows="5" required></textarea>
            <button type="submit">Send</button>
        </form>
    </div>
</body>
</html>""",
            "css": ""
        }
    }
    
    sample_plan = {
        "name": "Coffee Shop Website",
        "pages": [
            {"name": "home", "purpose": "Landing page"},
            {"name": "about", "purpose": "About us"},
            {"name": "menu", "purpose": "Menu items"},
            {"name": "contact", "purpose": "Contact form"}
        ]
    }
    
    sample_description = "A modern coffee shop website with home, about, menu, and contact pages"
    
    # Test complete website save
    print("\n" + "=" * 60)
    print("Saving complete website...")
    print("=" * 60)
    
    result = file_manager.save_complete_website(
        pages=sample_pages,
        plan=sample_plan,
        description=sample_description,
        website_name="Test_Coffee_Shop",
        image_urls={"hero": "/uploads/hero.png", "features": "/uploads/features.png"}
    )
    
    print(f"\n✓ Website saved successfully!")
    print(f"  Folder: {result['folder_path']}")
    print(f"  Pages saved: {len(result['saved_files'])}")
    
    for page_name, file_path in result['saved_files'].items():
        print(f"    - {page_name}: {os.path.basename(file_path)}")
    
    # Verify files exist
    print("\n" + "=" * 60)
    print("Verifying saved files...")
    print("=" * 60)
    
    folder_path = result['folder_path']
    
    # Check HTML files
    for page_name in sample_pages.keys():
        html_file = os.path.join(folder_path, f"{page_name}.html")
        if os.path.exists(html_file):
            print(f"✓ {page_name}.html exists ({os.path.getsize(html_file)} bytes)")
        else:
            print(f"✗ {page_name}.html NOT FOUND")
    
    # Check CSS file
    css_file = os.path.join(folder_path, "style.css")
    if os.path.exists(css_file):
        print(f"✓ style.css exists ({os.path.getsize(css_file)} bytes)")
    else:
        print(f"✗ style.css NOT FOUND")
    
    # Check index.html
    index_file = os.path.join(folder_path, "index.html")
    if os.path.exists(index_file):
        print(f"✓ index.html exists ({os.path.getsize(index_file)} bytes)")
    else:
        print(f"✗ index.html NOT FOUND")
    
    # Check metadata.json
    metadata_file = os.path.join(folder_path, "metadata.json")
    if os.path.exists(metadata_file):
        print(f"✓ metadata.json exists ({os.path.getsize(metadata_file)} bytes)")
        
        # Display metadata content
        import json
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        print("\n  Metadata content:")
        print(f"    - Created: {metadata.get('created_at')}")
        print(f"    - Pages: {metadata.get('pages')}")
        print(f"    - Description: {metadata.get('description')[:50]}...")
    else:
        print(f"✗ metadata.json NOT FOUND")
    
    # Verify CSS extraction
    print("\n" + "=" * 60)
    print("Verifying CSS extraction...")
    print("=" * 60)
    
    # Check home.html for CSS link
    home_file = os.path.join(folder_path, "home.html")
    with open(home_file, 'r', encoding='utf-8') as f:
        home_content = f.read()
    
    if '<link rel="stylesheet" href="style.css">' in home_content:
        print("✓ CSS link tag found in home.html")
    else:
        print("✗ CSS link tag NOT FOUND in home.html")
    
    if '<style>' not in home_content:
        print("✓ Style tags removed from home.html")
    else:
        print("✗ Style tags still present in home.html")
    
    # Verify internal links
    print("\n" + "=" * 60)
    print("Verifying internal link fixes...")
    print("=" * 60)
    
    if 'href="home.html"' in home_content or 'href="about.html"' in home_content:
        print("✓ Internal links properly formatted (.html extension)")
    else:
        print("⚠ Internal links may need review")
    
    print("\n" + "=" * 60)
    print("Test completed successfully! ✓")
    print("=" * 60)
    print(f"\nYou can open the website by navigating to:")
    print(f"  {folder_path}")
    print(f"\nAnd opening index.html or any page in your browser.")
    

if __name__ == "__main__":
    test_file_manager()
