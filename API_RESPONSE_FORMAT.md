# API Response Format - /api/generate-website

## Endpoint
```
POST /api/generate-website
```

## Request Format

### Headers
```
Content-Type: application/json
```

### Body
```json
{
  "description": "Your business description here..."
}
```

### Example Request
```json
{
  "description": "AI-powered project management tool for remote teams with task automation, real-time collaboration, and intelligent analytics dashboard"
}
```

---

## Response Format

The API uses **Server-Sent Events (SSE)** to stream progress updates in real-time.

### Content-Type
```
text/event-stream
```

### Event Format
Each event is sent as:
```
data: <JSON_OBJECT>

```

---

## Progress Events

### 1. Planning Step (Progress: 25%)
```json
data: {
  "step": "planning",
  "status": "in_progress",
  "progress": 25,
  "message": "✓ Planning complete: 4 pages planned",
  "error": null
}
```

### 2. Image Description Step (Progress: 40%)
```json
data: {
  "step": "image_description",
  "status": "in_progress",
  "progress": 40,
  "message": "✓ Image descriptions ready for 3 sections",
  "error": null
}
```

### 3. Image Generation Step (Progress: 65%)
```json
data: {
  "step": "image_generation",
  "status": "in_progress",
  "progress": 65,
  "message": "✓ 3 images generated successfully",
  "error": null
}
```

### 4. HTML Generation Step (Progress: 95%)
```json
data: {
  "step": "html_generation",
  "status": "in_progress",
  "progress": 95,
  "message": "✓ Generating page 3/4",
  "error": null
}
```

---

## Final Success Event (Progress: 100%)

```json
data: {
  "step": "complete",
  "status": "completed",
  "progress": 100,
  "message": "✓ Website generation complete",
  "data": {
    "pages": {
      "home": {
        "html": "<!DOCTYPE html>\n<html>...",
        "css": "/* Home page styles */\n..."
      },
      "about": {
        "html": "<!DOCTYPE html>\n<html>...",
        "css": "/* About page styles */\n..."
      },
      "features": {
        "html": "<!DOCTYPE html>\n<html>...",
        "css": "/* Features page styles */\n..."
      },
      "contact": {
        "html": "<!DOCTYPE html>\n<html>...",
        "css": "/* Contact page styles */\n..."
      }
    },
    "image_urls": {
      "hero": "/uploads/hero_image.png",
      "features": "/uploads/features_image.png",
      "testimonials": "/uploads/testimonials_image.png"
    },
    "plan": {
      "pages": [
        {
          "name": "home",
          "purpose": "Landing page showcasing main value proposition",
          "sections": ["hero", "features", "testimonials", "cta"]
        },
        {
          "name": "about",
          "purpose": "Company story and team information",
          "sections": ["story", "team", "values"]
        },
        {
          "name": "features",
          "purpose": "Detailed product features and capabilities",
          "sections": ["hero", "feature_grid", "comparison", "cta"]
        },
        {
          "name": "contact",
          "purpose": "Contact form and information",
          "sections": ["form", "info", "map"]
        }
      ],
      "styling": {
        "theme": "modern professional",
        "primary_color": "#3B82F6",
        "secondary_color": "#64748B",
        "font_family": "Inter, sans-serif",
        "design_style": "clean and minimal with subtle gradients"
      },
      "image_sections": ["hero", "features", "testimonials"],
      "navigation": ["home", "about", "features", "contact"]
    }
  }
}
```

---

## Error Event

```json
data: {
  "step": "failed",
  "status": "failed",
  "progress": 40,
  "message": "Planning failed: Invalid JSON format",
  "error": "Planning failed: Invalid JSON format"
}
```

---

## Response Fields

### Progress Event Fields
| Field | Type | Description |
|-------|------|-------------|
| `step` | string | Current workflow step: `"planning"`, `"image_description"`, `"image_generation"`, `"html_generation"`, `"complete"`, `"failed"` |
| `status` | string | Current status: `"in_progress"`, `"completed"`, `"failed"` |
| `progress` | number | Progress percentage (0-100) |
| `message` | string | Human-readable progress message |
| `error` | string \| null | Error message if failed, otherwise null |

### Final Success Event Additional Fields
| Field | Type | Description |
|-------|------|-------------|
| `data` | object | Contains the complete results |
| `data.pages` | object | Map of page names to HTML/CSS objects |
| `data.pages[name].html` | string | Complete HTML for the page |
| `data.pages[name].css` | string | Extracted CSS for the page |
| `data.image_urls` | object | Map of section names to image URLs |
| `data.plan` | object | Complete website plan object |
| `data.plan.pages` | array | Array of page configurations |
| `data.plan.styling` | object | Styling strategy (theme, colors, fonts) |
| `data.plan.image_sections` | array | Sections requiring images |
| `data.plan.navigation` | array | Navigation structure |

---

## JavaScript Client Example

```javascript
async function generateWebsite(description) {
  const response = await fetch('/api/generate-website', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ description })
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    
    if (done) break;

    const chunk = decoder.decode(value, { stream: true });
    const lines = chunk.split('\n');

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const jsonData = line.substring(6);
        const data = JSON.parse(jsonData);
        
        // Update progress
        console.log(`Progress: ${data.progress}% - ${data.message}`);
        
        // Handle completion
        if (data.status === 'completed' && data.data) {
          console.log('Pages:', data.data.pages);
          console.log('Images:', data.data.image_urls);
          console.log('Plan:', data.data.plan);
        }
        
        // Handle errors
        if (data.status === 'failed') {
          console.error('Error:', data.error);
        }
      }
    }
  }
}

// Usage
generateWebsite('Your business description here...');
```

---

## cURL Example

```bash
curl -X POST http://localhost:8000/api/generate-website \
  -H "Content-Type: application/json" \
  -d '{
    "description": "AI-powered project management tool for remote teams"
  }' \
  --no-buffer
```

---

## Testing

Visit the test page at:
```
http://localhost:8000/test
```

This provides a complete UI for testing the endpoint with:
- Progress tracking
- Real-time log display
- Image preview
- Generated pages viewer
- Website plan display
