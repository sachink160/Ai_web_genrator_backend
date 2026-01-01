
---

# **UNIN-13601 – AI Landing Page Generator – Backend API Implementation Guide**

## **AI Landing Page Generator – Postman API Implementation Guide**

This document outlines backend API integrations for the three stages of landing page generation:

1. Generate image prompts using **Azure OpenAI GPT-5**
2. Generate images using **Ideogram V3**
3. Generate HTML using **Azure OpenAI GPT-5**

---

## **Prerequisites**

### **API Credentials**

Create the following environment variables in Postman:

```
{{AZURE_ENDPOINT}}
{{AZURE_API_KEY}}
{{AZURE_DEPLOYMENT}}
{{AZURE_API_VERSION}}
{{LANDING_PAGE_DESC}}
```

Example:

```
AZURE_API_KEY="xxxx"
AZURE_ENDPOINT="https://xxxx.openai.azure.com/"
AZURE_DEPLOYMENT="gpt-5" 
AZURE_API_VERSION="2024-01-01-preview"
```

---

---

# **Stage 1: Generate Image Prompts with Azure OpenAI GPT-5**

Goal: Create unique creative prompts for different landing page sections (hero, features, testimonials).

---

## **API Call**

**Method:** POST

**URL:**

```
{{AZURE_ENDPOINT}}/openai/deployments/{{AZURE_DEPLOYMENT}}/chat/completions?api-version={{AZURE_API_VERSION}}
```

### **Headers**

```
Content-Type: application/json
api-key: {{AZURE_API_KEY}}
```

### **Request Body**

```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are an expert prompt generator for AI image models. Generate short but powerful prompts."
    },
    {
      "role": "user",
      "content": "Generate a hero section prompt for: {{LANDING_PAGE_DESC}}"
    }
  ],
  "temperature": 0.7,
  "max_tokens": 200
}
```

---

### **Sample Response**

```json
{
  "id": "chatcmpl-12345",
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "Ultra-realistic hero image of a modern coffee shop..."
      }
    }
  ]
}
```

---

# **Stage 2: Generate Images with Ideogram V3**

Goal: Convert the creative prompts into actual images using Ideogram.

---

## **API Endpoint**

**URL:**

```
https://api.ideogram.ai/generate
```

### **Headers**

```
Content-Type: application/json
API-Key: <YOUR_IDEOGRAM_KEY>
```

### **Example Request Body**

```json
{
  "model": "ideogram-v3",
  "prompt": "Ultra-realistic hero image..."
}
```

### **Sample Response**

```json
{
  "id": "img-12345",
  "image_url": "https://images.ideogram.ai/abc123.jpg"
}
```

---

### **Download and Store the Image**

Use the returned URL to download and store the image.

---

# **Stage 3: Generate HTML with Azure OpenAI GPT-5**

Goal: Combine images + content to generate final landing page HTML.

---

## **API Call**

**Method:** POST
**URL:**

```
{{AZURE_ENDPOINT}}/openai/deployments/{{AZURE_DEPLOYMENT}}/chat/completions?api-version={{AZURE_API_VERSION}}
```

### **Headers**

```
Content-Type: application/json
api-key: {{AZURE_API_KEY}}
```

### **Request Body**

```json
{
  "messages": [
    {
      "role": "system",
      "content": "You generate HTML landing pages. Provide clean HTML+CSS."
    },
    {
      "role": "user",
      "content": "Use these assets to generate a landing page:\nHero: <URL1>\nFeatures: <URL2>\nTestimonials: <URL3>"
    }
  ],
  "max_tokens": 4000
}
```

---

### **Sample Response (HTML Snippet)**

```html
<section class='hero'>
  <img src='URL1'>
</section>
<section class='features'>
  <img src='URL2'>
</section>
<section class='testimonials'>
  <img src='URL3'>
</section>
```

---

# **Streaming Version (Optional)**

Backend can stream HTML generation for a live preview.

---

# **Complete Flow Summary**

1. Generate image prompts (Azure GPT-5)
2. Generate images (Ideogram V3)
3. Generate HTML (Azure GPT-5)
4. Display in frontend
5. Add caching, rate limiting, performance improvements

---

# **Error Handling**

### Example

```
400 – Missing API key  
401 – Unauthorized  
429 – Rate limit exceeded  
500 – Model error
```

---

# **Performance Optimization**

### Reduce Costs

* Use `reasoning_effort="low"` (50–60% cheaper)
* Reduce `max_completion_tokens`
* Cache prompts

### Improve Speed

* Parallel image generation
* Ideogram TURBO
* Stream HTML preview

---

# **Testing in Postman**

Create a collection:

1. Stage 1 – Generate Image Prompts
2. Stage 2 – Generate Image (Hero)
3. Stage 2 – Generate Image (Features)
4. Stage 2 – Generate Image (Testimonials)
5. Stage 3 – Generate HTML

### Environment Variables Example:

```
"AZURE_ENDPOINT": "https://xxx.openai.azure.com/",
"AZURE_API_KEY": "<key>",
"AZURE_DEPLOYMENT": "gpt-5",
"AZURE_API_VERSION": "2024-01-01-preview",
"LANDING_PAGE_DESC": "A modern coffee shop specializing in artisan coffee"
```

---

# **Next Steps for Developers**

1. Import the Postman collection
2. Test each API call
3. Implement backend (Node, Python, Java, etc.)
4. Add file storage
5. Build frontend
6. Add authentication
7. Add caching & rate limiting

---

# **Support Links**

* Azure OpenAI Documentation
* Ideogram API Documentation

---