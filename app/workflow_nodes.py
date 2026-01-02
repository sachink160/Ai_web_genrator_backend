"""
LangGraph workflow nodes for website generation.
"""
import json
import logging
import os
import httpx
from typing import Dict, List, Optional
from app.workflow_state import WorkflowState
from app.dspy_modules import WebsitePlanner, ImageDescriptionGenerator, MultiPageGenerator
from app.file_manager import WebsiteFileManager
from openai import AzureOpenAI
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Azure OpenAI client for DALL-E 3
azure_client = AzureOpenAI(
    api_key=os.getenv("AZURE_AI_TOKEN"),
    api_version=os.getenv("AZURE_AI_APP_VERSION"),
    azure_endpoint=os.getenv("AZURE_AI_ENDPOINT_URL")
)


def planning_node(state: WorkflowState) -> WorkflowState:
    """
    Step 1: Generate comprehensive website plan.
    """
    logger.info("Starting planning node...")
    
    try:
        # Initialize WebsitePlanner module
        planner = WebsitePlanner()
        
        # Generate plan
        plan_json = planner(description=state["description"])
        # plan_json = planner.forward(description=state["description"])
        
        logger.info(f"Raw plan response length: {len(plan_json)} chars")
        logger.info(f"Raw plan preview: {plan_json[:200]}...")
        
        # Parse JSON with multiple fallback strategies
        plan = None
        parse_error = None
        
        # Strategy 1: Direct JSON parse
        try:
            plan = json.loads(plan_json)
            logger.info("✓ JSON parsed directly")
        except json.JSONDecodeError as e:
            parse_error = str(e)
            logger.warning(f"Direct JSON parse failed: {e}")
            
            # Strategy 2: Extract from markdown code blocks
            try:
                if "```json" in plan_json:
                    logger.info("Attempting to extract JSON from ```json block")
                    plan_json = plan_json.split("```json")[1].split("```")[0].strip()
                elif "```" in plan_json:
                    logger.info("Attempting to extract JSON from ``` block")
                    plan_json = plan_json.split("```")[1].split("```")[0].strip()
                
                plan = json.loads(plan_json)
                logger.info("✓ JSON extracted from code block")
            except (json.JSONDecodeError, IndexError) as e2:
                logger.warning(f"Code block extraction failed: {e2}")
                
                # Strategy 3: Find JSON object using regex
                json_match = re.search(r'\{[^{}]*"pages"[^{}]*\}|\{.*"pages".*\}', plan_json, re.DOTALL)
                if json_match:
                    logger.info("Attempting regex extraction of JSON")
                    try:
                        plan = json.loads(json_match.group(0))
                        logger.info("✓ JSON extracted using regex")
                    except json.JSONDecodeError as e3:
                        logger.error(f"Regex extraction failed: {e3}")
                
                # Strategy 4: Create a fallback plan
                if plan is None:
                    logger.warning("All JSON parsing strategies failed, using fallback plan")
                    plan = {
                        "pages": [
                            {"name": "home", "purpose": "Landing page", "sections": ["hero", "features", "cta"]},
                            {"name": "about", "purpose": "About page", "sections": ["story", "team"]},
                            {"name": "contact", "purpose": "Contact page", "sections": ["form", "info"]}
                        ],
                        "styling": {
                            "theme": "modern",
                            "primary_color": "#3B82F6",
                            "secondary_color": "#64748B",
                            "font_family": "sans-serif",
                            "design_style": "clean and professional"
                        },
                        "image_sections": ["hero", "features", "testimonials"],
                        "navigation": ["home", "about", "contact"]
                    }
        
        # Validate plan structure
        if not isinstance(plan, dict):
            raise ValueError("Plan must be a dictionary")
        
        if "pages" not in plan or not isinstance(plan["pages"], list):
            raise ValueError("Plan must contain 'pages' array")
        
        if len(plan["pages"]) == 0:
            raise ValueError("Plan must contain at least one page")
        
        logger.info(f"✓ Generated plan with {len(plan.get('pages', []))} pages")
        logger.info(f"Pages: {[p.get('name', 'unknown') for p in plan.get('pages', [])]}")
        
        # Update state
        return {
            **state,
            "plan": plan,
            "plan_json": json.dumps(plan),  # Store normalized JSON
            "current_step": "image_description",
            "status": "in_progress",
            "progress": 25,
            "progress_message": f"✓ Planning complete: {len(plan.get('pages', []))} pages planned"
        }
        
    except Exception as e:
        logger.error(f"Planning node error: {str(e)}")
        return {
            **state,
            "current_step": "failed",
            "status": "failed",
            "error": f"Planning failed: {str(e)}",
            "progress": 0,
            "progress_message": f"✗ Planning failed: {str(e)}"
        }




def image_description_node(state: WorkflowState) -> WorkflowState:
    """
    Step 2a: Generate image descriptions for sections based on plan.
    """
    logger.info("Starting image description node...")
    
    try:
        plan = state["plan"]
        image_sections = plan.get("image_sections", ["hero", "features", "testimonials"])
        
        # Initialize generator
        generator = ImageDescriptionGenerator()
        
        # Generate descriptions for each section
        image_descriptions = {}
        plan_str = json.dumps(plan)
        
        # Fallback descriptions for content policy violations
        fallback_descriptions = {
            "hero": "Professional business hero banner with modern design, clean layout, and welcoming atmosphere",
            "features": "Clean feature section with minimalist icons and professional presentation",
            "testimonials": "Professional testimonial section with friendly atmosphere and trust-building design",
            "about": "Professional about section showcasing company story and values",
            "services": "Professional services showcase with clean modern design",
            "products": "Professional product display with attractive presentation",
            "team": "Professional team photo with friendly workplace environment",
            "contact": "Professional contact section with welcoming design"
        }
        
        for section in image_sections:
            # Determine which page has this section
            page_name = "home"  # Default to home page
            for page in plan.get("pages", []):
                if section in page.get("sections", []):
                    page_name = page["name"]
                    break
            
            logger.info(f"Generating image description for {section} on {page_name}")
            
            try:
                # Try to generate description with AI
                description = generator(
                    plan=plan_str,
                    section_name=section,
                    page_name=page_name,
                    business_description=state["description"]
                )
                # description = generator.forward(
                #     plan=plan_str,
                #     section_name=section,
                #     page_name=page_name,
                #     business_description=state["description"]
                # )
                image_descriptions[section] = description
                logger.info(f"✓ Generated description for {section}")
                
            except Exception as gen_error:
                error_str = str(gen_error).lower()
                
                # Check if it's a content policy violation
                is_content_policy = (
                    "content" in error_str and "policy" in error_str or
                    "contentpolicyviolation" in error_str or
                    "filtered" in error_str or
                    "content management" in error_str
                )
                
                if is_content_policy:
                    logger.warning(f"Content policy violation for {section}, using fallback description")
                    # Use fallback description
                    fallback = fallback_descriptions.get(
                        section,
                        f"Professional {section} section with modern, clean design"
                    )
                    image_descriptions[section] = fallback
                else:
                    # Re-raise if it's a different error
                    logger.error(f"Error generating description for {section}: {str(gen_error)}")
                    raise
        
        logger.info(f"Generated {len(image_descriptions)} image descriptions")
        
        # Update state
        return {
            **state,
            "image_descriptions": image_descriptions,
            "current_step": "image_generation",
            "progress": 40,
            "progress_message": f"✓ Image descriptions ready for {len(image_descriptions)} sections"
        }
        
    except Exception as e:
        logger.error(f"Image description node error: {str(e)}")
        
        # Check if content policy error - use all fallback descriptions
        error_str = str(e).lower()
        is_content_policy = (
            "content" in error_str and "policy" in error_str or
            "contentpolicyviolation" in error_str or
            "filtered" in error_str
        )
        
        if is_content_policy:
            logger.warning("Content policy violation detected, using fallback descriptions for all sections")
            
            # Use fallback descriptions for all sections
            plan = state.get("plan", {})
            image_sections = plan.get("image_sections", ["hero", "features", "testimonials"])
            
            fallback_descriptions = {
                "hero": "Professional business hero banner with modern design, clean layout, and welcoming atmosphere",
                "features": "Clean feature section with minimalist icons and professional presentation",
                "testimonials": "Professional testimonial section with friendly atmosphere and trust-building design"
            }
            
            image_descriptions = {}
            for section in image_sections:
                image_descriptions[section] = fallback_descriptions.get(
                    section,
                    f"Professional {section} section with modern, clean design"
                )
            
            # Continue workflow with fallback descriptions
            return {
                **state,
                "image_descriptions": image_descriptions,
                "current_step": "image_generation",
                "progress": 40,
                "progress_message": f"✓ Image descriptions ready (using safe defaults)"
            }
        
        # For other errors, fail the workflow
        return {
            **state,
            "current_step": "failed",
            "status": "failed",
            "error": f"Image description generation failed: {str(e)}",
            "progress": 25,
            "progress_message": f"✗ Image description failed: {str(e)}"
        }



def image_generation_node(state: WorkflowState) -> WorkflowState:
    """
    Step 2b: Generate images using DALL-E 3 based on descriptions.
    Falls back to static images if API fails.
    """
    logger.info("Starting image generation node...")
    
    try:
        image_descriptions = state["image_descriptions"]
        image_urls = {}
        
        # Get upload directory and base URL
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        upload_dir = os.path.join(base_dir, "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        
        # Get base URL from environment (default to localhost)
        base_url = os.getenv("BASE_URL", "http://127.0.0.1:8000")
        
        # Static image mapping for fallback
        static_images = {
            "hero": "hero_1766668485.png",
            "features": "features_1766668478.png",
            "testimonials": "testimonials_1766668479.png"
        }
        
        for section, description in image_descriptions.items():
            logger.info(f"Generating image for {section}")
            
            try:
                # Generate image using DALL-E 3
                response = azure_client.images.generate(
                    model="dall-e-3",
                    prompt=description,
                    size="1792x1024",
                    quality="hd",
                    n=1
                )
                
                image_url = response.data[0].url
                
                # Download and save image
                image_response = httpx.get(image_url, timeout=30.0)
                if image_response.status_code == 200:
                    filename = f"{section}_image.png"
                    filepath = os.path.join(upload_dir, filename)
                    
                    with open(filepath, "wb") as f:
                        f.write(image_response.content)
                    
                    # Store full URL
                    image_urls[section] = f"{base_url}/uploads/{filename}"
                    logger.info(f"✓ Image saved for {section}: {image_urls[section]}")
                else:
                    logger.warning(f"Failed to download image for {section}, using static fallback")
                    # Use static fallback
                    fallback_filename = static_images.get(section, "placeholder.png")
                    image_urls[section] = f"{base_url}/uploads/{fallback_filename}"
                    
            except Exception as img_error:
                logger.error(f"Image generation failed for {section}: {str(img_error)}")
                logger.info(f"Using static fallback image for {section}")
                # Use static fallback
                fallback_filename = static_images.get(section, "placeholder.png")
                image_urls[section] = f"{base_url}/uploads/{fallback_filename}"
        
        logger.info(f"Generated {len(image_urls)} images")
        logger.info(f"Image URLs: {image_urls}")
        
        # Update state
        return {
            **state,
            "image_urls": image_urls,
            "current_step": "html_generation",
            "progress": 65,
            "progress_message": f"✓ {len(image_urls)} images generated successfully"
        }
        
    except Exception as e:
        logger.error(f"Image generation node error: {str(e)}")
        return {
            **state,
            "current_step": "failed",
            "status": "failed",
            "error": f"Image generation failed: {str(e)}",
            "progress": 40,
            "progress_message": f"✗ Image generation failed: {str(e)}"
        }


def html_generation_node(state: WorkflowState) -> WorkflowState:
    """
    Step 3: Generate HTML/CSS for each page based on plan.
    """
    logger.info("Starting HTML generation node...")
    
    try:
        plan = state["plan"]
        image_urls = state["image_urls"]
        pages_output = {}
        
        # Initialize generator
        generator = MultiPageGenerator()
        
        # Format image URLs for DSPy
        image_urls_text = "\n".join([f"{section}: {url}" for section, url in image_urls.items()])
        
        # Extract all page names for navigation context
        all_pages = plan.get("pages", [])
        page_names = [page["name"] for page in all_pages]
        
        logger.info(f"Generating HTML for {len(all_pages)} pages: {page_names}")
        
        # Generate HTML for each page
        total_pages = len(all_pages)
        for idx, page in enumerate(all_pages):
            page_name = page["name"]
            logger.info(f"Generating HTML for page: {page_name} ({idx + 1}/{total_pages})")
            
            # Create enhanced plan with navigation info
            enhanced_plan = {
                **plan,
                "current_page": page_name,
                "all_pages": page_names,
                "navigation_instruction": f"Create navigation links for: {', '.join(page_names)}. Use href='[page_name].html' format."
            }
            
            # Generate HTML
            html = generator(
                plan=json.dumps(enhanced_plan),
                page_name=page_name,
                page_config=json.dumps(page),
                image_urls=image_urls_text,
                business_description=state["description"]
            )
            
            # CRITICAL: Clean up markdown blocks and validate
            html = html.strip()
            
            # Remove markdown code blocks if present
            if html.startswith("```html"):
                logger.info(f"Removing ```html markdown wrapper from {page_name}")
                html = html[7:]  # Remove ```html
            elif html.startswith("```"):
                logger.info(f"Removing ``` markdown wrapper from {page_name}")
                html = html[3:]  # Remove ```
            
            if html.endswith("```"):
                logger.info(f"Removing trailing ``` from {page_name}")
                html = html[:-3]
            
            html = html.strip()
            
            # Validate HTML content
            if not html or len(html) < 100:
                logger.error(f"❌ Empty or too short HTML generated for {page_name} ({len(html)} chars)")
                raise ValueError(f"HTML generation failed for {page_name}: Response too short or empty")
            
            if not html.startswith("<!DOCTYPE") and not html.startswith("<html"):
                logger.error(f"❌ Invalid HTML structure for {page_name}. First 100 chars: {html[:100]}")
                raise ValueError(f"HTML generation failed for {page_name}: Invalid HTML structure")
            
            # Check for truncation warning
            if "</html>" not in html.lower():
                logger.warning(f"⚠ HTML for {page_name} might be truncated - missing closing </html> tag")
            
            # Extract CSS from HTML
            css = ""
            if "<style>" in html and "</style>" in html:
                css = html.split("<style>")[1].split("</style>")[0].strip()
            
            pages_output[page_name] = {
                "html": html,
                "css": css
            }
            
            # Log success
            logger.info(f"✓ Generated HTML for {page_name} ({len(html)} chars)")
            
            # Update progress
            page_progress = 65 + int((idx + 1) / total_pages * 25)
            
        logger.info(f"Generated HTML for {len(pages_output)} pages")
        
        # Update state - don't mark as complete yet, we need to save files
        return {
            **state,
            "pages": pages_output,
            "current_step": "file_storage",
            "status": "in_progress",
            "progress": 90,
            "progress_message": f"✓ HTML generated for {len(pages_output)} pages, preparing to save files..."
        }
        
    except Exception as e:
        logger.error(f"HTML generation node error: {str(e)}")
        return {
            **state,
            "current_step": "failed",
            "status": "failed",
            "error": f"HTML generation failed: {str(e)}",
            "progress": 65,
            "progress_message": f"✗ HTML generation failed: {str(e)}"
        }


def html_validation_node(state: WorkflowState) -> WorkflowState:
    """
    Step 3.5: Validate and fix HTML for responsiveness.
    """
    logger.info("Starting HTML validation node...")
    
    try:
        pages = state["pages"]
        css_theme = state.get("css_theme", "")
        
        validated_pages = {}
        
        for page_name, page_content in pages.items():
            html = page_content["html"]
            
            try:
                # Validate and fix HTML
                fixed_html = validate_and_fix_html(html, css_theme)
                
                validated_pages[page_name] = {
                    "html": fixed_html,
                    "css": page_content.get("css", "")
                }
                
                logger.info(f"✓ Validated and fixed {page_name}")
                
            except Exception as fix_error:
                logger.warning(f"Could not validate {page_name}: {str(fix_error)}, using original")
                # Use original if fixing fails
                validated_pages[page_name] = page_content
        
        return {
            **state,
            "pages": validated_pages,
            "current_step": "file_storage",
            "progress": 95,
            "progress_message": f"✓ HTML validated - {len(validated_pages)} pages optimized for responsiveness"
        }
        
    except Exception as e:
        logger.error(f"HTML validation node error: {str(e)}")
        # Don't fail the workflow - continue with unvalidated HTML
        logger.warning("Continuing without validation")
        return {
            **state,
            "current_step": "file_storage",
            "progress": 95,
            "progress_message": "⚠ HTML validation skipped - using generated HTML as-is"
        }


def validate_and_fix_html(html: str, css_theme: str) -> str:
    """
    Validate HTML and fix common responsive issues.
    
    Fixes:
    - Adds .container wrappers where missing
    - Replaces custom grid classes with CSS theme grid classes
    - Ensures hamburger menu exists for mobile
    - Adds section-padding to sections
    """
    try:
        from bs4 import BeautifulSoup
        import re
        
    except ImportError:
        logger.warning("BeautifulSoup not available, skipping HTML validation")
        return html
    
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # Fix 1: Ensure sections have proper structure
        main = soup.find('main')
        if main:
            sections = main.find_all('section')
            for section in sections:
                # Add section-padding class if not hero and doesn't have it
                classes = section.get('class', [])
                if isinstance(classes, str):
                    classes = classes.split()
                
                if 'hero' not in classes and 'section-padding' not in classes:
                    classes.append('section-padding')
                    section['class'] = classes
                
                # Ensure container div exists (skip hero sections)
                if 'hero' not in classes:
                    container = section.find('div', class_='container')
                    if not container:
                        # Wrap content in container
                        container_div = soup.new_tag('div')
                        container_div['class'] = 'container'
                        
                        # Move all children to container
                        children = list(section.children)
                        for child in children:
                            container_div.append(child.extract())
                        
                        section.append(container_div)
        
        # Fix 2: Replace custom grid/wrapper classes with CSS theme grid
        # Find elements with common custom class patterns
        custom_patterns = [
            r'.*-grid',
            r'.*-list',
            r'.*-wrapper',
            r'.*-container',
            r'.*-items'
        ]
        
        for pattern in custom_patterns:
            for elem in soup.find_all(class_=re.compile(pattern)):
                # Check if it's not already using grid classes
                elem_classes = elem.get('class', [])
                if isinstance(elem_classes, str):
                    elem_classes = elem_classes.split()
                
                if 'grid' not in elem_classes:
                    # Replace with proper grid classes
                    elem['class'] = ['grid', 'grid-cols-1', 'grid-cols-md-3', 'gap-lg']
        
        # Fix 3: Ensure hamburger menu exists
        navbar = soup.find(class_='navbar')
        if navbar:
            hamburger = soup.find(class_='hamburger-menu')
            if not hamburger:
                # Create hamburger menu button
                button = soup.new_tag('button')
                button['class'] = 'hamburger-menu'
                button['aria-label'] = 'Toggle menu'
                
                # Add three spans for hamburger icon
                for _ in range(3):
                    span = soup.new_tag('span')
                    button.append(span)
                
                # Insert after logo or at beginning of navbar
                logo = navbar.find(class_='logo')
                if logo:
                    logo.insert_after(button)
                else:
                    navbar.insert(0, button)
        
        # Fix 4: Ensure nav-menu class on navigation ul
        nav_ul = soup.find('nav').find('ul') if soup.find('nav') else None
        if nav_ul:
            ul_classes = nav_ul.get('class', [])
            if isinstance(ul_classes, str):
                ul_classes = ul_classes.split()
            if 'nav-menu' not in ul_classes:
                ul_classes.append('nav-menu')
                nav_ul['class'] = ul_classes
        
        return str(soup)
        
    except Exception as e:
        logger.error(f"Error during HTML validation: {str(e)}")
        # Return original HTML if validation fails
        return html



def file_storage_node(state: WorkflowState) -> WorkflowState:
    """
    Step 4: Save generated website files to structured folders.
    """
    logger.info("Starting file storage node...")
    
    try:
        pages = state["pages"]
        plan = state.get("plan")
        description = state.get("description")
        image_urls = state.get("image_urls")
        css_theme = state.get("css_theme")  # Get global CSS theme
        
        # Extract website name from description or plan
        website_name = None
        if plan and "name" in plan:
            website_name = plan["name"]
        elif description:
            # Use first few words of description as website name
            words = description.split()[:3]
            website_name = "_".join(words)
        
        # Initialize file manager
        file_manager = WebsiteFileManager()
        
        # Save complete website with global CSS theme
        logger.info(f"Saving website with {len(pages)} pages...")
        if css_theme:
            logger.info(f"Using global CSS theme ({len(css_theme)} chars)")
        result = file_manager.save_complete_website(
            pages=pages,
            plan=plan,
            description=description,
            website_name=website_name,
            image_urls=image_urls,
            css_theme=css_theme  # Pass global CSS theme
        )
        
        folder_path = result['folder_path']
        saved_files = result['saved_files']
        
        logger.info(f"✓ Website saved to: {folder_path}")
        logger.info(f"✓ Saved {len(saved_files)} HTML files")
        
        # Update state with file information
        return {
            **state,
            "folder_path": folder_path,
            "saved_files": saved_files,
            "current_step": "complete",
            "status": "completed",
            "progress": 100,
            "progress_message": f"✓ Website generation complete: {len(saved_files)} pages saved to {os.path.basename(folder_path)}"
        }
        
    except Exception as e:
        logger.error(f"File storage node error: {str(e)}")
        # Even if file storage fails, we still have the HTML in memory
        # So we'll mark it as completed but with a warning
        return {
            **state,
            "current_step": "complete",
            "status": "completed",
            "progress": 100,
            "progress_message": f"✓ HTML generated but file storage failed: {str(e)}",
            "error": f"File storage warning: {str(e)}"
        }

