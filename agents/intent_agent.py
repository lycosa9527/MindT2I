"""
Intent Recognition Agent for MindT2I
=====================================

Ultra-simple keyword detection:
1. Check for explicit keywords (video, image, picture, etc.)
2. Default to image if no keywords found

No motion detection, no fallback analysis - just direct keyword matching.
"""

import logging
from typing import Dict, Literal, Optional
from clients.multimodal import text_client

logger = logging.getLogger(__name__)


class IntentAgent:
    """ReAct agent for analyzing user intent (image vs video)"""
    
    def __init__(self):
        """Initialize the intent agent"""
        self.text_client = text_client
        logger.info("IntentAgent initialized with keyword detection")
    
    async def analyze_intent(self, prompt: str) -> Dict[str, any]:
        """
        Analyze user prompt to determine intent using direct keyword detection.
        
        Simple and fast - checks for explicit keywords only:
        - "video", "视频", "动画" → VIDEO
        - "image", "picture", "photo", "图片", "照片" → IMAGE
        - No keywords → IMAGE (default)
        
        Args:
            prompt: User's input prompt
            
        Returns:
            Dict containing:
            - intent: "image" or "video"
            - confidence: float between 0 and 1
            - reasoning: explanation of the decision
            - enhanced_prompt: improved version of the prompt
        """
        try:
            logger.info(f"Analyzing intent for prompt: {prompt[:50]}...")
            
            # Direct keyword detection only
            direct_result = self._detect_direct_keywords(prompt)
            if direct_result:
                logger.info(f"Direct keyword detected: {direct_result['intent']} (confidence: {direct_result['confidence']})")
                return direct_result
            
            # Default to image if no explicit keywords
            logger.info("No explicit keywords found, defaulting to image")
            return {
                "intent": "image",
                "confidence": 0.8,
                "reasoning": "No explicit media type keyword detected, defaulting to image",
                "enhanced_prompt": prompt
            }
            
        except Exception as e:
            logger.error(f"Intent analysis failed: {e}")
            # Default to image if analysis fails
            return {
                "intent": "image",
                "confidence": 0.5,
                "reasoning": "Failed to analyze intent, defaulting to image",
                "enhanced_prompt": prompt
            }
    
    def _detect_direct_keywords(self, prompt: str) -> Optional[Dict]:
        """
        Detect explicit video/image keywords in prompt.
        
        Returns result immediately if found, None otherwise.
        """
        prompt_lower = prompt.lower()
        
        # Video keywords (highest priority)
        video_keywords = [
            'video', 'videos', '视频', '影片', '动画', 'animation',
            'clip', 'footage', 'movie', 'film'
        ]
        
        for keyword in video_keywords:
            if keyword in prompt_lower:
                return {
                    "intent": "video",
                    "confidence": 1.0,
                    "reasoning": f"Explicit video keyword detected: '{keyword}'",
                    "enhanced_prompt": prompt
                }
        
        # Image keywords (high priority)
        image_keywords = [
            'image', 'images', 'picture', 'pictures', 'photo', 'photos',
            '图片', '图像', '照片', '画', '图',
            'pic', 'pics', 'photograph', 'illustration', 'drawing'
        ]
        
        for keyword in image_keywords:
            if keyword in prompt_lower:
                return {
                    "intent": "image",
                    "confidence": 1.0,
                    "reasoning": f"Explicit image keyword detected: '{keyword}'",
                    "enhanced_prompt": prompt
                }
        
        return None
    
    
    def _build_react_prompt(self, user_prompt: str) -> str:
        """
        Build a ReAct-style prompt for Qwen-turbo.
        
        ReAct = Reasoning + Acting
        The model will reason about the intent and then act by providing a structured response.
        """
        return f"""You are an AI assistant that analyzes user prompts to determine if they want to generate an IMAGE or a VIDEO.

**User Prompt**: "{user_prompt}"

**Your Task**: Analyze this prompt using the ReAct (Reasoning + Acting) pattern:

**STEP 1 - OBSERVATION**: 
What do you observe in the prompt? Look for:
- Keywords suggesting motion, animation, or time (e.g., "running", "moving", "animation", "动态", "运动")
- Keywords suggesting a single scene or static image (e.g., "picture", "photo", "scene", "图片", "照片")
- Duration or sequence indicators (e.g., "5 seconds", "short clip", "一段")
- Context clues about the desired output

**STEP 2 - REASONING**:
Based on your observations, explain your reasoning:
- Does the user want something with motion/animation? → VIDEO
- Does the user want a single frame/static scene? → IMAGE
- Are there any ambiguous elements?

**STEP 3 - ACTION**:
Provide your decision in this EXACT format:

INTENT: [image or video]
CONFIDENCE: [0.0 to 1.0]
REASONING: [brief explanation]
ENHANCED_PROMPT: [improved version of the prompt optimized for the chosen format]

**Important Rules**:
1. If there are motion keywords (running, flying, moving, 奔跑, 飞翔, 移动, 动作), choose VIDEO
2. If unclear or no motion keywords, default to IMAGE
3. Confidence should be:
   - 0.9-1.0: Very clear motion or static indicators
   - 0.7-0.8: Likely motion or static
   - 0.5-0.6: Unclear, educated guess
4. Enhanced prompt should be optimized for the format (add motion details for video, visual details for image)

**Example Responses**:

Example 1 (Video):
User: "一只小猫在月光下奔跑"
INTENT: video
CONFIDENCE: 0.95
REASONING: Contains "奔跑" (running) which indicates motion and action over time
ENHANCED_PROMPT: 一只可爱的小猫在明亮的月光下快速奔跑，尾巴摇摆，展现出优雅的动作

Example 2 (Image):
User: "A beautiful sunset over mountains"
INTENT: image
CONFIDENCE: 0.9
REASONING: Describes a static natural scene with no motion indicators
ENHANCED_PROMPT: A breathtaking sunset over majestic mountains with golden and orange hues painting the sky, peaceful and serene landscape

Example 3 (Video):
User: "狗狗在公园里玩耍"
INTENT: video
CONFIDENCE: 0.9
REASONING: "玩耍" (playing) implies movement and activity
ENHANCED_PROMPT: 一只活泼的狗狗在绿色的公园里欢快地玩耍，跑来跑去，摇尾巴，充满活力

Now analyze the user's prompt and provide your response:"""

    def _parse_react_response(self, response: str, original_prompt: str) -> Dict:
        """
        Parse the ReAct response from Qwen-turbo.
        
        Args:
            response: Raw response from Qwen-turbo
            original_prompt: Original user prompt (fallback)
            
        Returns:
            Structured intent result
        """
        try:
            # Extract intent, confidence, reasoning, and enhanced prompt
            intent = "image"  # default
            confidence = 0.5
            reasoning = "Unable to parse response"
            enhanced_prompt = original_prompt
            
            lines = response.strip().split('\n')
            for line in lines:
                line = line.strip()
                
                if line.startswith('INTENT:'):
                    intent_value = line.split(':', 1)[1].strip().lower()
                    if 'video' in intent_value:
                        intent = "video"
                    elif 'image' in intent_value:
                        intent = "image"
                
                elif line.startswith('CONFIDENCE:'):
                    try:
                        conf_value = line.split(':', 1)[1].strip()
                        confidence = float(conf_value)
                        # Clamp between 0 and 1
                        confidence = max(0.0, min(1.0, confidence))
                    except ValueError:
                        pass
                
                elif line.startswith('REASONING:'):
                    reasoning = line.split(':', 1)[1].strip()
                
                elif line.startswith('ENHANCED_PROMPT:'):
                    enhanced_prompt = line.split(':', 1)[1].strip()
            
            return {
                "intent": intent,
                "confidence": confidence,
                "reasoning": reasoning,
                "enhanced_prompt": enhanced_prompt,
                "raw_response": response
            }
            
        except Exception as e:
            logger.error(f"Failed to parse ReAct response: {e}")
            return {
                "intent": "image",
                "confidence": 0.5,
                "reasoning": f"Parse error: {str(e)}",
                "enhanced_prompt": original_prompt,
                "raw_response": response
            }
    
    def get_decision(self, intent_result: Dict) -> Literal["image", "video"]:
        """
        Get the final decision based on intent analysis.
        
        Args:
            intent_result: Result from analyze_intent()
            
        Returns:
            "image" or "video"
        """
        return intent_result["intent"]


# Global instance
intent_agent = IntentAgent()

