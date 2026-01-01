# Azure Content Policy Error - Fix Applied

## ❌ The Error You Encountered

```
litellm.ContentPolicyViolationError: AzureException - The response was filtered 
due to the prompt triggering Azure OpenAI's content management policy.
```

## 🔍 Why This Happens

Azure OpenAI has **strict content filtering** that sometimes flags innocent content:

- Business descriptions can accidentally contain flagged words
- AI-generated prompts might use phrases Azure considers risky
- The filter is overly cautious to prevent misuse
- Even terms like "bar", "wine", "spirits", or certain business types can trigger it

## ✅ Solution Applied

I've updated `workflow_nodes.py` with **intelligent error handling**:

### 1. Per-Section Fallback
When a specific section triggers the filter:
- Catches the content policy error
- Uses a safe, generic fallback description
- Continues with other sections normally

```python
# If "hero" section triggers filter:
# ❌ AI-generated: "Craft beer bar with dark wood and brewing equipment"
# ✅ Fallback used: "Professional business hero banner with modern design"
```

### 2. Full Fallback System
If the entire process fails:
- Detects content policy violation
- Uses safe defaults for ALL sections
- Continues workflow (doesn't fail)

### 3. Fallback Descriptions

```python
fallback_descriptions = {
    "hero": "Professional business hero banner with modern design",
    "features": "Clean feature section with minimalist icons",
    "testimonials": "Professional testimonial section with friendly atmosphere",
    "about": "Professional about section showcasing company story",
    "services": "Professional services showcase with clean modern design",
    "products": "Professional product display with attractive presentation",
    "team": "Professional team photo with friendly workplace environment",
    "contact": "Professional contact section with welcoming design"
}
```

## 🎯 What Happens Now

### Before (Would Fail):
```
Step 2: Image Description → ❌ Content Policy Error → Workflow FAILED
```

### After (Graceful Fallback):
```
Step 2: Image Description → ⚠️ Content Policy Detected → ✅ Use Safe Defaults → Continue
```

## 📊 Behavior Examples

### Scenario 1: One Section Triggers Filter
```
✓ Generating hero description... Content policy detected!
⚠️ Using fallback for hero section
✓ Generating features description... Success!
✓ Generating testimonials description... Success!
→ Workflow continues with 1 fallback, 2 AI-generated
```

### Scenario 2: All Sections Trigger Filter
```
⚠️ Content policy violation detected
⚠️ Using safe fallback descriptions for all sections
→ Workflow continues with all fallbacks
```

### Scenario 3: No Issues
```
✓ Generating hero description... Success!
✓ Generating features description... Success!
✓ Generating testimonials description... Success!
→ Workflow continues with all AI-generated descriptions
```

## 🔧 How to Test

Try generating a website now:

```bash
POST http://localhost:8000/api/generate-website
{
  "description": "A craft beer bar with tap room and tasting experiences"
}
```

**Result**: Even if Azure flags content, the workflow will complete successfully with safe, professional image descriptions.

## 📝 Log Messages

You'll see these in your logs:

### When content is flagged:
```
⚠️ Content policy violation for hero, using fallback description
✓ Image descriptions ready (using safe defaults)
```

### When everything works:
```
✓ Generated description for hero
✓ Generated description for features
✓ Image descriptions ready for 3 sections
```

## 🎨 Impact on Image Quality

- **Fallback descriptions** are generic but professional
- DALL-E will still generate good images
- Images will be more generic/safe but still usable
- You can manually edit descriptions in the code if needed

## 🛡️ Prevention Tips

To reduce content policy triggers:

1. **Use generic business terms**
   - ✅ "Modern restaurant"
   - ❌ "Bar and grill with craft cocktails"

2. **Avoid specific product mentions**
   - ✅ "Beverage service"
   - ❌ "Beer, wine, and spirits"

3. **Keep descriptions professional**
   - ✅ "Professional service provider"
   - ❌ "Adult entertainment venue"

## 🔄 If Issues Persist

If you continue to get content policy errors:

1. **Check your Azure OpenAI settings**
   - Content filtering level may be set to "Strict"
   - Consider adjusting to "Medium" if available

2. **Modify the business description**
   - Use more generic terms
   - Avoid industry-specific jargon

3. **Use the fallback descriptions**
   - Edit `fallback_descriptions` in `workflow_nodes.py`
   - Customize them for your use case

## ✨ Summary

✅ **Error is now handled gracefully**
✅ **Workflow won't fail due to content policy**
✅ **Safe fallback descriptions are used automatically**
✅ **Website generation continues successfully**

**Your website generator is now resilient to Azure's content filtering!** 🎉
