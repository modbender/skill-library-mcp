# IMA All AI - CHANGELOG

All notable changes to this skill will be documented in this file.

## [1.0.2] - 2026-02-27

### 🔄 Image Model Updates (Critical)

#### Added Nano Banana2
- ✅ **Nano Banana2** (gemini-3.1-flash-image) is now available
  - text_to_image: 4/6/10/13pts (512px/1K/2K/4K)
  - image_to_image: 4/6/10/13pts (512px/1K/2K/4K)
  - **Cheapest option at 512px (4pts)**
  - Fastest generation time (20-40s)
  - 1:1 square only

#### Updated Model Count
- Image models: 2 → 3 (SeeDream 4.5, Nano Banana2, Nano Banana Pro)
- Restored budget option for image generation

### 📖 Documentation Updates

#### Updated Sections
1. **YAML Header**
   - Updated model count: text_to_image (3), image_to_image (3)
   - Added budget option: Nano Banana2 (4pts for 512px)

2. **Fallback Model Table**
   - Added Nano Banana2 to all image fallback scenarios
   - Now includes 3-tier system: budget/balanced/premium

3. **Supported Models at a Glance**
   - Added Nano Banana2 with size options
   - Updated model count from 2 to 3

4. **Quick Selection Guide**
   - Budget option: Nano Banana2 512px (4pts)
   - Balanced: SeeDream 4.5 (5pts)
   - Premium: Nano Banana Pro (10-18pts)

5. **Estimated Generation Time**
   - Added Nano Banana2: 20-40s (fastest)

### 🎯 Cost Structure

#### Image Model Pricing
- **Budget**: Nano Banana2 512px - 4pts (cheapest)
- **Balanced**: SeeDream 4.5 - 5pts (best value, aspect ratio support)
- **Premium**: Nano Banana Pro - 10-18pts (highest quality)

### 📝 Notes

- Synchronized with ima-image-ai v1.0.1
- Video models remain unchanged (already up-to-date from v1.0.1)
- Music models unchanged
- All changes reflect actual Open API availability (2026-02-27)

---

## [1.0.1] - 2026-02-26

### 🔄 Video Model Updates

#### Models Removed
- ❌ Vidu Q2 Turbo (no longer available via Open API)

#### Models Added/Updated
- ✅ Updated Pixverse model variants (V3.5-V5.5)
- ✅ Confirmed availability of all 14 video models

#### Updated Default Recommendations
- text_to_video: Wan 2.6 (most popular, 25pts)
- Removed references to unavailable models

### 📖 Documentation Updates
- Updated model counts and lists
- Corrected Pixverse variant information
- Updated fallback model recommendations

---

## [1.0.0] - 2026-02-25

### Initial Release
- Unified skill for image, video, and music generation
- Support for 2 image models (SeeDream 4.5, Nano Banana Pro)
- Support for 14 video models
- Support for 3 music models
- User preference system
- Comprehensive model selection guide
