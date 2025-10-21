"""
Video Generation Default Configuration
========================================

Default parameters for video generation optimized for quality and cost balance.

Cost Formula: 单价（分辨率）× 时长（秒）
Higher resolution costs more: 1080P > 720P > 480P
"""

# Video Resolution Defaults
DEFAULT_VIDEO_SIZE = "1920*1080"  # 1080P (16:9 landscape)
DEFAULT_DURATION = 10              # 10 seconds (wan2.5-t2v-preview)

# Video Generation Settings
DEFAULT_PROMPT_EXTEND = True       # Enable prompt enhancement
DEFAULT_WATERMARK = False          # No watermark by default
DEFAULT_AUDIO = True               # Auto-generate audio (wan2.5)

# Resolution Options (organized by quality tier)
RESOLUTION_1080P = {
    "landscape_16_9": "1920*1080",
    "portrait_9_16": "1080*1920",
    "square_1_1": "1440*1440",
    "landscape_4_3": "1632*1248",
    "portrait_3_4": "1248*1632"
}

RESOLUTION_720P = {
    "landscape_16_9": "1280*720",
    "portrait_9_16": "720*1280",
    "square_1_1": "960*960",
    "landscape_4_3": "1088*832",
    "portrait_3_4": "832*1088"
}

RESOLUTION_480P = {
    "landscape_16_9": "832*480",
    "portrait_9_16": "480*832",
    "square_1_1": "624*624"
}

# Duration Options
DURATION_SHORT = 5   # 5 seconds (all models support)
DURATION_LONG = 10   # 10 seconds (only wan2.5-t2v-preview)

# Model Support Matrix
MODEL_SUPPORT = {
    "wan2.5-t2v-preview": {
        "resolutions": ["480P", "720P", "1080P"],
        "durations": [5, 10],
        "audio": True,
        "default_resolution": "1920*1080",
        "default_duration": 10
    },
    "wan2.2-t2v-plus": {
        "resolutions": ["480P", "1080P"],
        "durations": [5],
        "audio": False,
        "default_resolution": "1920*1080",
        "default_duration": 5
    },
    "wanx2.1-t2v-turbo": {
        "resolutions": ["480P", "720P"],
        "durations": [5],
        "audio": False,
        "default_resolution": "1280*720",
        "default_duration": 5
    },
    "wanx2.1-t2v-plus": {
        "resolutions": ["720P"],
        "durations": [5],
        "audio": False,
        "default_resolution": "1280*720",
        "default_duration": 5
    }
}

# Cost Estimate (for reference)
# Note: Actual costs may vary, check DashScope pricing
COST_NOTES = """
Resolution Cost Hierarchy:
  1080P > 720P > 480P

Duration Impact:
  费用 = 单价（基于分辨率）× 时长（秒）
  
Example:
  - 1080P, 10s: Higher quality, higher cost
  - 720P, 5s: Medium quality, medium cost
  - 480P, 5s: Lower quality, lower cost

Recommendation:
  - Default: 1080P, 10s (best quality)
  - Budget: 720P, 5s (balanced)
  - Testing: 480P, 5s (fastest/cheapest)
"""

