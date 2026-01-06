# Standard library imports
import json
import logging
import re

# Third-party imports
import dspy

# Local application imports
from app.prompts.doc_prompt import user_prompt_html, system_prompt_html, user_prompt_edit_html
from app.signature import (
    ImagePromptSignature,
    LandingPageSignature,
    TemplateModificationSignature,
    HTMLEditSignature,
    WebsitePlannerSignature,
    ImageDescriptionSignature,
    MultiPageSignature,
    WebsiteUpdateAnalyzerSignature
)
# Import LLM configurations from config module (used in various DSPy modules)
from app.config import planning_llm, update_llm


class ImagePromptGenerator(dspy.Module):
    """Generate image prompts for landing page sections."""
    
    def __init__(self):
        super().__init__()
        self.predict = dspy.Predict(ImagePromptSignature)
    
    def forward(self, business_description: str, section_type: str, section_focus: str, section_details: str):
        system_rules = """You are a senior visual designer creating background images for professional websites.

Your task is to generate image prompts that will be used ONLY as BACKGROUND or DECORATIVE visuals.
All text, icons, cards, numbers, and UI elements will be added later using HTML/CSS.

STRICT RULES (VERY IMPORTANT):
- DO NOT include any text, letters, numbers, words, quotes, headings, UI cards, buttons, or labels
- DO NOT include testimonial cards, review boxes, star ratings, or speech bubbles
- DO NOT include dashboards, website mockups, or UI screenshots
- Images must feel empty, breathable, and content-ready
- Think like a real SaaS/enterprise website designer

STYLE REQUIREMENTS:
- Professional, modern, website-friendly visuals
- Clean composition with negative space
- Subtle lighting, soft depth, balanced contrast
- Suitable for overlaying web content

Generate a detailed, professional image prompt that will be used to create a background/decorative image for this section. The prompt should be specific, visually descriptive, and aligned with the business description."""
        
        result = self.predict(
            business_description=f"{system_rules}\n\nBusiness/Product Description: {business_description}",
            section_type=section_type,
            section_focus=section_focus,
            section_details=section_details
        )
        return result.prompt.strip()


class LandingPageGenerator(dspy.Module):
    """Generate HTML landing pages from scratch."""
    
    def __init__(self):
        super().__init__()
        self.predict = dspy.Predict(LandingPageSignature)
    
    def forward(self, description: str, image_urls_text: str):

        
        # Build the full prompt using the existing prompt structure
        system_prompt = system_prompt_html()
        user_prompt_content = user_prompt_html(
            type('obj', (object,), {'description': description}),
            image_urls_text
        )
        
        # Combine into a single description for DSPy
        full_description = f"{system_prompt}\n\n{user_prompt_content}"
        
        result = self.predict(
            description=full_description,
            image_urls_text=image_urls_text
        )
        return result.html


class TemplateModifier(dspy.Module):
    """Modify existing HTML templates."""
    
    def __init__(self):
        super().__init__()
        # Use update_llm for template modifications (4K tokens sufficient) - imported at top
        self.predict = dspy.Predict(TemplateModificationSignature)
        self.predict.lm = update_llm
    
    def forward(self, template_html: str, description: str, image_urls_text: str):
        modification_rules = f"""You are an expert frontend engineer specializing in modifying existing HTML templates while preserving their structure and design patterns.
If Image URL is provided, then use the image URL to modify the template.
{image_urls_text}

CRITICAL TASK: Modify the provided HTML template based on the user's instructions while maintaining:
- The same HTML structure, CSS classes, and layout patterns
- The same responsive design breakpoints and behavior
- The same CSS styling, animations, and visual effects
- The same section organization and navigation structure

MODIFICATION GUIDELINES:

1. PRESERVE TEMPLATE STRUCTURE:
   - Keep the same HTML element hierarchy
   - Maintain all IDs, classes, and data attributes
   - Preserve navigation structure and form elements
   - Keep the same CSS organization and variable names
   - Maintain all media queries and responsive breakpoints

2. CONTENT MODIFICATIONS:
   - Update text content (headings, paragraphs, button text) as requested
   - Replace brand names, company names, and product names
   - Modify feature descriptions and testimonials
   - Update contact information and form labels
   - Change image sources if requested (use provided image URLs)
   - Update metadata (title, meta descriptions, alt text)

3. STYLING MODIFICATIONS:
   - Update colors, fonts, spacing as requested
   - Modify CSS variables if they exist
   - Adjust sizes, padding, margins as needed
   - Change background colors, gradients, or images
   - Update button styles, hover effects, transitions
   - Maintain CSS organization and structure

4. STRUCTURAL MODIFICATIONS:
   - Add new sections if requested (while maintaining template style)
   - Remove sections if explicitly requested
   - Reorder sections if needed
   - Add or remove elements within sections
   - Maintain consistent styling with existing template

5. IMAGE HANDLING:
   - Replace image URLs with provided paths if requested
   - Maintain existing image styling and responsive behavior
   - Update alt text to match new content
   - Preserve image positioning and layout

TECHNICAL REQUIREMENTS:
- Output ONLY complete HTML (with embedded CSS in <style> tag)
- Include <!DOCTYPE html>
- No JavaScript, no external libraries
- Production-ready, valid HTML
- Maintain mobile-first responsive design
- Preserve all accessibility features

IMPORTANT:
- Only modify what is explicitly requested in the modification instructions
- Preserve everything else exactly as it appears in the template
- Ensure the modified HTML is valid and properly closed
- Maintain the same code quality and organization as the template
- Coordinate changes with the provided images if image paths are specified"""
        
        full_description = f"{modification_rules}\n\nMODIFICATION INSTRUCTIONS:\n{description}"
        
        result = self.predict(
            template_html=template_html,
            description=full_description,
            image_urls_text=image_urls_text
        )
        return result.html


class HTMLEditor(dspy.Module):
    """Edit existing HTML/CSS content."""
    
    def __init__(self):
        super().__init__()
        # Use update_llm for HTML editing (4K tokens sufficient) - imported at top
        self.predict = dspy.Predict(HTMLEditSignature)
        self.predict.lm = update_llm
    
    def forward(self, html: str, css: str, edit_request: str):
        
        
        # Use the existing prompt structure
        full_prompt = user_prompt_edit_html(html, css, edit_request)
        
        result = self.predict(
            html_input=html,
            css_input=css,
            edit_request=full_prompt
        )
        return result.html_output


# New DSPy Modules for LangGraph Workflow

class WebsitePlanner(dspy.Module):
    """Generate comprehensive website structure plan."""
    
    def __init__(self):
        super().__init__()
        # Import planning_llm from config and use it for this module - imported at top
        self.predict = dspy.Predict(WebsitePlannerSignature)
        # Configure this specific predict to use planning_llm
        self.predict.lm = planning_llm
    
    
    def forward(self, description: str):
        planning_instructions = """You are an expert website architect and UX designer.
        
Your task is to create a comprehensive, professional website structure plan based on the business description.

PLANNING REQUIREMENTS:

1. PAGES STRUCTURE:
   - Determine the optimal number of pages (typically 3-5 for most businesses)
   - Each page should have a clear purpose and target audience
   - Define sections for each page that support the page's purpose
   - Common pages: home (landing), about, features/services, contact, pricing (if applicable)

2. SECTION PLANNING:
   - Hero: Main value proposition, CTA
   - Features: Product/service highlights
   - Testimonials: Social proof, customer reviews
   - CTA: Call-to-action sections
   - Additional: FAQ, pricing, team, portfolio, etc.

3. STYLING STRATEGY:
   - Choose a theme that matches the business type (modern, professional, creative, minimal, etc.)
   - Select a primary and secondary color scheme
   - Define font strategy (professional sans-serif, elegant serif, etc.)
   - Specify overall design style

4. IMAGE REQUIREMENTS:
   - Identify which sections need background/decorative images
   - Typically: hero, features, testimonials
   - Images should enhance, not distract

5. NAVIGATION:
   - Define clear navigation structure
   - Should include all main pages
   - Logical order for user journey

OUTPUT FORMAT: Return ONLY valid JSON matching the structure specified in the signature.
Do not include any explanatory text, only the JSON object."""
        
        full_description = f"{planning_instructions}\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nBUSINESS DESCRIPTION TO ANALYZE:\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n{description}\n\nNow create an EXCEPTIONAL website plan based on this business."
        
        result = self.predict(description=full_description)
        return result.plan.strip()


class ImageDescriptionGenerator(dspy.Module):
    """Generate targeted image descriptions for specific sections."""
    
    def __init__(self):
        super().__init__()
        # Import planning_llm from config - image descriptions are short - imported at top
        self.predict = dspy.Predict(ImageDescriptionSignature)
        # Configure this specific predict to use planning_llm (descriptions are short prompts)
        self.predict.lm = planning_llm
    
    
    def forward(self, plan: str, section_name: str, page_name: str, business_description: str):
        system_rules = """You are a professional visual designer creating DALL-E 3 prompts for website background images.

CRITICAL: These images are BACKGROUND/DECORATIVE ONLY. All text, UI elements, and interactive components will be added via HTML/CSS.

YOUR TASK:
- Analyze the website plan, section purpose, and business description
- Create a DALL-E 3 prompt for a background image that enhances the section
- The image should align with the website's theme and styling strategy
- Focus on composition, mood, color harmony, and professional aesthetics

STRICT RULES (MUST FOLLOW):
- NO text, letters, numbers, words, quotes, headings, labels
- NO UI elements, cards, buttons, icons with text
- NO testimonial cards, review boxes, star ratings
- NO dashboards, mockups, screenshots, or website previews
- NO speech bubbles, quotes, or text overlays

VISUAL REQUIREMENTS:
- Professional, modern aesthetic suitable for business websites
- Clean composition with breathing room for overlay content
- Soft, flattering lighting (avoid harsh shadows)
- Minimal to moderate contrast (avoid extreme darks/lights)
- Color palette should complement the website's styling strategy
- Subtle depth and dimension (gradients, layering)
- Images should feel premium and polished

OUTPUT: A detailed DALL-E 3 prompt (2-4 sentences) describing the visual composition, mood, colors, and style."""
        
        result = self.predict(
            plan=plan,
            section_name=section_name,
            page_name=page_name,
            business_description=f"{system_rules}\n\nBusiness: {business_description}"
        )
        return result.image_description.strip()


class MultiPageGenerator(dspy.Module):
    """Generate HTML/CSS for individual pages."""
    
    def __init__(self):
        super().__init__()
        self.predict = dspy.Predict(MultiPageSignature)
    
    def forward(self, plan: str, page_name: str, page_config: str, image_urls: str, business_description: str):
        generation_rules = """You are an expert frontend developer specializing in creating professional, responsive websites.

YOUR TASK:
- Generate a complete, production-ready HTML page based on the website plan
- Follow the page configuration and include all specified sections
- Use the provided image URLs for appropriate sections (hero, features, testimonials)
- Create realistic, professional content aligned with the business description
- Apply the styling strategy from the plan

TECHNICAL REQUIREMENTS:

1. HTML STRUCTURE:
   - Start with <!DOCTYPE html>
   - Include proper <head> with meta tags, title, viewport
   - Use semantic HTML5 (header, nav, main, section, footer)
   - Proper heading hierarchy (h1, h2, h3)
   - Accessible markup (alt text, ARIA labels where needed)

2. CSS STYLING:
   - Embed ALL CSS in <style> tag in <head>
   - Mobile-first responsive design
   - Use CSS Grid and Flexbox for layouts
   - Smooth transitions and hover effects
   - Professional color scheme matching plan
   - Typography hierarchy with web-safe fonts or Google Fonts
   - Proper spacing and white space

3. RESPONSIVE DESIGN:
   - Mobile: < 768px
   - Tablet: 768px - 1024px
   - Desktop: > 1024px
   - Use media queries for breakpoints
   - Responsive images and typography

4. IMAGE INTEGRATION:
   - Use provided image URLs as background images or <img> tags
   - Ensure images are responsive
   - Add overlays for text legibility if needed
   - Fallback colors if images fail to load

5. CONTENT GUIDELINES:
   - Generate realistic, professional content (not Lorem Ipsum)
   - Align all content with the business description
   - Include compelling CTAs (Call-to-Actions)
   - Professional tone and messaging

6. NO EXTERNAL DEPENDENCIES:
   - No JavaScript (unless absolutely necessary for navigation)
   - No external CSS frameworks
   - Self-contained, single HTML file
   - Can use Google Fonts via CDN

7. RESPONSIVE HTML STRUCTURE (CRITICAL):

   A global CSS theme exists with pre-defined classes. USE THESE CLASSES.
   
   ✅ CORRECT Section Structure:
   <section class="section-padding">
       <div class="container">
           <h2 class="section-title">Products</h2>
           <div class="grid grid-cols-1 grid-cols-md-3 gap-lg">
               <div class="card product-card">
                   <img src="..." alt="Product">
                   <h3>Product Name</h3>
                   <p>Description</p>
               </div>
           </div>
       </div>
   </section>
   
   ✅ CORRECT Navigation (with mobile menu):
   <header>
       <div class="navbar container">
           <a href="home.html" class="logo">Brand</a>
           <button class="hamburger-menu" aria-label="Toggle menu">
               <span></span><span></span><span></span>
           </button>
           <nav>
               <ul class="nav-menu">
                   <li><a href="home.html" class="nav-link active">Home</a></li>
                   <li><a href="about.html" class="nav-link">About</a></li>
               </ul>
           </nav>
       </div>
   </header>
   
   ❌ WRONG (DO NOT USE custom classes):
   <div class="product-grid">
       <div class="product-item">...</div>
   </div>
   
   ALWAYS use: .container, .grid .grid-cols-1 .grid-cols-md-3, .card, .btn, .section-padding

OUTPUT: Complete, valid HTML5 document ready for production deployment."""
        
        full_prompt = f"{generation_rules}\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n📋 GENERATION INPUTS:\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\nBUSINESS DESCRIPTION:\n{business_description}\n\nNow create an EXCEPTIONAL HTML page for this business!"
        
        # PRINT COMPLETE PROMPT TO TERMINAL
        print("\n" + "="*80)
        print(f"🎯 GENERATING HTML FOR PAGE: {page_name}")
        print("="*80)
        print("\n📋 INPUTS TO DSPY:")
        print("-"*80)
        print(f"\n1️⃣  PAGE NAME: {page_name}")
        print(f"\n2️⃣  PAGE CONFIG:\n{page_config[:500]}..." if len(page_config) > 500 else f"\n2️⃣  PAGE CONFIG:\n{page_config}")
        print(f"\n3️⃣  IMAGE URLS:\n{image_urls}")
        print(f"\n4️⃣  PLAN (first 500 chars):\n{plan[:500]}...")
        print(f"\n5️⃣  BUSINESS DESCRIPTION:\n{business_description[:300]}...")
        print("\n" + "-"*80)
        print("📝 FULL PROMPT STRUCTURE:")
        print("-"*80)
        # print(f"Length: {len(full_prompt)} characters")
        # print(f"Generation Rules: {len(generation_rules)} chars")
        print(f"Business Context: {len(business_description)} chars")
        print("\n💬 PROMPT PREVIEW (First 1000 chars):")
        print("-"*80)
        print(full_prompt[:1000] + "...")
        print("\n" + "="*80 + "\n")
        
        result = self.predict(
            plan=plan,
            page_name=page_name,
            page_config=page_config,
            image_urls=image_urls,
            business_description=full_prompt
        )
        return result.html.strip()


class WebsiteUpdater(dspy.Module):
    """Intelligently update website pages and global CSS based on natural language requests."""
    
    def __init__(self):
        super().__init__()
        # Use planning_llm for analysis (short task, 2K tokens) - imported at top
        self.analyzer = dspy.Predict(WebsiteUpdateAnalyzerSignature)
        self.analyzer.lm = update_llm
        
        # Use HTMLEditor for actual modifications (which now uses update_llm with 4K tokens)
        self.html_editor = HTMLEditor()
    
    def forward(self, pages: dict, global_css: str, edit_request: str):
        """
        Analyze edit request and apply updates intelligently.
        
        Args:
            pages: Dict of page_name -> {html: str, css: str}
            global_css: Current global CSS content
            edit_request: User's natural language edit instructions
        
        Returns:
            Dict with:
                - updated_pages: Dict of modified pages only
                - updated_global_css: Modified global CSS if changed
                - changes_summary: Description of what was changed
        """
        # json, logging imported at top of file
        logger = logging.getLogger(__name__)
        
        # Step 1: Analyze the edit request
        available_pages_list = list(pages.keys())
        available_pages_text = ", ".join(available_pages_list)
        
        logger.info(f"Analyzing edit request: {edit_request[:100]}...")
        logger.info(f"Available pages: {available_pages_text}")
        
        try:
            analysis_result = self.analyzer(
                edit_request=edit_request,
                available_pages=available_pages_text,
                current_global_css=global_css[:500] if global_css else ""  # Just a sample for context
            )
            
            # Parse analysis
            try:
                analysis = json.loads(analysis_result.analysis)
                logger.info(f"Analysis result: {analysis}")
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse analysis JSON: {e}, using fallback")
                # Fallback: try to determine from keywords
                edit_lower = edit_request.lower()
                
                # Check for global styling keywords
                global_keywords = ['color', 'font', 'theme', 'all pages', 'everywhere', 'global', 'button', 'spacing']
                is_global = any(keyword in edit_lower for keyword in global_keywords)
                
                # Check for page-specific keywords
                page_specific = any(page_name in edit_lower for page_name in available_pages_list)
                
                if is_global and not page_specific:
                    analysis = {
                        "update_type": "global_css",
                        "target_pages": [],
                        "requires_css_update": True,
                        "interpretation": "Applying global styling changes"
                    }
                elif page_specific and not is_global:
                    # Try to identify which pages
                    target_pages = [page for page in available_pages_list if page in edit_lower]
                    analysis = {
                        "update_type": "specific_pages",
                        "target_pages": target_pages if target_pages else [available_pages_list[0]],
                        "requires_css_update": False,
                        "interpretation": f"Updating content on specific pages: {', '.join(target_pages)}"
                    }
                else:
                    # Both or ambiguous
                    target_pages = [page for page in available_pages_list if page in edit_lower]
                    if not target_pages:
                        target_pages = [available_pages_list[0]]  # Default to first page
                    analysis = {
                        "update_type": "both",
                        "target_pages": target_pages,
                        "requires_css_update": True,
                        "interpretation": "Updating both styling and page content"
                    }
        except Exception as e:
            logger.error(f"Analysis failed: {e}, using fallback analysis")
            # Ultra-fallback: update first page only
            analysis = {
                "update_type": "specific_pages",
                "target_pages": [available_pages_list[0]] if available_pages_list else [],
                "requires_css_update": False,
                "interpretation": "Updating page content"
            }
        
        # Step 2: Apply updates based on analysis
        updated_pages = {}
        updated_global_css = None
        changes_made = []
        
        # Update global CSS if needed
        if analysis.get("requires_css_update") and global_css:
            logger.info("Updating global CSS...")
            try:
                # Create a minimal HTML wrapper for CSS editing
                css_wrapper_html = f"""<!DOCTYPE html>
<html>
<head>
    <style>
    {global_css}
    </style>
</head>
<body>
    <p>CSS Template</p>
</body>
</html>"""
                
                # Use HTMLEditor to modify the CSS
                modified_html = self.html_editor(
                    html=css_wrapper_html,
                    css=global_css,
                    edit_request=f"Update the CSS styling based on this request: {edit_request}. Only modify the CSS, preserve the HTML structure."
                )
                
                # Extract the modified CSS from the result
                import re
                style_pattern = r'<style[^>]*>(.*?)</style>'
                css_matches = re.findall(style_pattern, modified_html, re.DOTALL | re.IGNORECASE)
                if css_matches:
                    updated_global_css = '\n\n'.join(css_matches).strip()
                    changes_made.append("Updated global CSS styling")
                    logger.info(f"✓ Global CSS updated ({len(updated_global_css)} chars)")
                else:
                    logger.warning("Could not extract CSS from modified HTML, keeping original")
                    updated_global_css = global_css
            except Exception as e:
                logger.error(f"Error updating global CSS: {e}")
                updated_global_css = global_css
        
        # Update specific pages if needed
        target_pages = analysis.get("target_pages", [])
        if target_pages and analysis.get("update_type") in ["specific_pages", "both"]:
            for page_name in target_pages:
                if page_name not in pages:
                    logger.warning(f"Page '{page_name}' not found in provided pages")
                    continue
                
                logger.info(f"Updating page: {page_name}...")
                try:
                    page_data = pages[page_name]
                    current_html = page_data.get('html', '')
                    current_css = page_data.get('css', global_css if global_css else '')
                    
                    # Use HTMLEditor to modify the page
                    modified_html = self.html_editor(
                        html=current_html,
                        css=current_css,
                        edit_request=edit_request
                    )
                    
                    # Extract CSS if any (re imported at top)
                    html_clean, extracted_css = self._extract_css(modified_html)
                    
                    updated_pages[page_name] = {
                        'html': html_clean,
                        'css': extracted_css if extracted_css else current_css
                    }
                    changes_made.append(f"Updated {page_name} page")
                    logger.info(f"✓ Page '{page_name}' updated")
                except Exception as e:
                    logger.error(f"Error updating page '{page_name}': {e}")
        
        # Generate summary
        if not changes_made:
            changes_summary = "No changes were made. Please check your request."
        else:
            changes_summary = f"Successfully applied changes: {', '.join(changes_made)}"
        
        logger.info(f"Update complete: {changes_summary}")
        
        return {
            "updated_pages": updated_pages,
            "updated_global_css": updated_global_css,
            "changes_summary": changes_summary,
            "analysis": analysis
        }
    
    def _extract_css(self, html: str):
        """Helper method to extract CSS from HTML. (re imported at top)"""
        style_pattern = r'<style[^>]*>(.*?)</style>'
        css_matches = re.findall(style_pattern, html, re.DOTALL | re.IGNORECASE)
        extracted_css = '\n\n'.join(css_matches).strip()
        html_without_style = re.sub(style_pattern, '', html, flags=re.DOTALL | re.IGNORECASE)
        return html_without_style, extracted_css
