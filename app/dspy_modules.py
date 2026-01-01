import dspy
from app.prompts.doc_prompt import user_prompt_html, system_prompt_html, user_prompt_edit_html
from app.signature import ( ImagePromptSignature,
                            LandingPageSignature,
                            TemplateModificationSignature,
                            HTMLEditSignature,
                            WebsitePlannerSignature,
                            ImageDescriptionSignature,
                            MultiPageSignature
                        )







#DSPy Modules
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
        self.predict = dspy.Predict(TemplateModificationSignature)
    
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
        self.predict = dspy.Predict(HTMLEditSignature)
    
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
        self.predict = dspy.Predict(WebsitePlannerSignature)
    
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
        
        full_description = f"{planning_instructions}\n\nBUSINESS DESCRIPTION:\n{description}"
        
        result = self.predict(description=full_description)
        return result.plan.strip()


class ImageDescriptionGenerator(dspy.Module):
    """Generate targeted image descriptions for specific sections."""
    
    def __init__(self):
        super().__init__()
        self.predict = dspy.Predict(ImageDescriptionSignature)
    
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


class CSSThemeGenerator(dspy.Module):
    """Generate unified CSS theme for entire website."""
    
    def __init__(self):
        super().__init__()
        self.predict = dspy.Predict(CSSThemeSignature)
    
    def forward(self, plan: str, business_description: str):
        theme_instructions = """You are a senior frontend developer and UI/UX designer specializing in creating cohesive, production-ready web design systems.

YOUR MISSION:
Create a comprehensive CSS theme that will be used across ALL pages of the website, ensuring perfect consistency and professional quality.

KEY PRINCIPLES:

1. DESIGN SYSTEM APPROACH:
   - Every color, font, spacing value should be defined as a CSS variable
   - Create a complete set of reusable component classes
   - All pages will use these same classes - NO page-specific CSS
   - Think like you're building a design system for a company

2. CSS VARIABLES (CRITICAL):
   Set up a complete variable system:
   
   :root {
     /* Colors - Full Palette */
     --primary-color: #...;
     --primary-dark: #...;
     --primary-light: #...;
     --secondary-color: #...;
     --accent-color: #...;
     --text-primary: #...;
     --text-secondary: #...;
     --background: #...;
     --surface: #...;
     --border-color: #...;
     
     /* Typography */
     --font-heading: '...', sans-serif;
     --font-body: '...', sans-serif;
     --h1-size: ...;
     --h2-size: ...;
     --h3-size: ...;
     --text-base: ...;
     --text-sm: ...;
     --line-height-tight: ...;
     --line-height-normal: ...;
     --line-height-relaxed: ...;
     
     /* Spacing System */
     --spacing-xs: 0.5rem;
     --spacing-sm: 1rem;
     --spacing-md: 1.5rem;
     --spacing-lg: 2rem;
     --spacing-xl: 3rem;
     --spacing-2xl: 4rem;
     
     /* Layout */
     --container-width: 1200px;
     --gap: 2rem;
     
     /* Design Elements */
     --border-radius: 0.5rem;
     --shadow-sm: ...;
     --shadow-md: ...;
     --shadow-lg: ...;
     --transition: all 0.3s ease;
   }

3. COMPONENT LIBRARY:
   Create reusable classes that all pages will use:
   
   - Navigation (.navbar, .nav-menu, .nav-link, .nav-link.active)
   - Hero sections (.hero, .hero-content, .hero-title, .hero-subtitle)
   - Buttons (.btn, .btn-primary, .btn-secondary, .btn-outline)
   - Cards (.card, .card-header, .card-body, .card-footer)
   - Product/feature cards (.product-card, .feature-card, .testimonial-card)
   - Forms (.form-group, .input, .textarea, .select, .label)
   - Sections (.section, .section-padding, .section-title)
   - Footer (.footer, .footer-content, .footer-links)

4. UTILITY CLASSES:
   - Layout: .container, .flex, .grid, .flex-center
   - Text: .text-center, .text-left, .text-right
   - Spacing: .mt-*, .mb-*, .p-*, .m-* (using spacing system)
   - Colors: .text-primary, .bg-primary, etc.

5. RESPONSIVE DESIGN:
   - Mobile-first approach
   - Breakpoints: 768px (tablet), 1024px (desktop)
   - Responsive navigation (hamburger menu for mobile)
   - Flexible grid systems

6. PROFESSIONAL POLISH:
   - Smooth hover transitions on all interactive elements
   - Focus states for accessibility
   - Box shadows for depth and dimension
   - Subtle gradients where appropriate
   - Consistent border radius
   - Professional color relationships

7. CONSISTENCY RULES:
   - NEVER use hardcoded colors - ALWAYS use CSS variables
   - NEVER use hardcoded spacing - ALWAYS use spacing variables
   - All components MUST be reusable across pages
   - Maintain visual hierarchy through consistent sizing

IMPORTANT INSTRUCTIONS:
- Output ONLY the CSS code
- NO explanations, NO comments (except for section headers)
- NO markdown code blocks (```css)
- Start directly with CSS
- Make it production-ready and comprehensive
- Every page will include this same CSS file

Analyze the website plan and business description to choose appropriate:
- Color schemes (professional/corporate vs creative/vibrant)
- Typography (modern sans-serif vs elegant serif)
- Visual style (minimal/clean vs rich/detailed)
- Component designs matching the business type"""

        full_plan = f"{theme_instructions}\n\nWEBSITE PLAN:\n{plan}\n\nBUSINESS:\n{business_description}"
        
        result = self.predict(
            plan=full_plan,
            business_description=business_description
        )
        return result.css_theme.strip()


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
        
        full_prompt = f"{generation_rules}\n\nBUSINESS DESCRIPTION:\n{business_description}"
        
        result = self.predict(
            plan=plan,
            page_name=page_name,
            page_config=page_config,
            image_urls=image_urls,
            business_description=full_prompt
        )
        return result.html.strip()
