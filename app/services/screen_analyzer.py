"""
Screen analysis service for understanding mobile app screens
"""
import base64
import io
from typing import Dict, Any, Optional, List
from PIL import Image
import cv2
import numpy as np
from pydantic import BaseModel
from app.services.ai_service import ai_service
import logging

logger = logging.getLogger(__name__)


class UIElement(BaseModel):
    """Represents a UI element on screen"""
    id: str
    type: str  # button, text, image, input, etc.
    position: Dict[str, int]  # x, y, width, height
    text: Optional[str] = None
    confidence: float = 0.0
    app_context: Optional[str] = None


class ScreenContext(BaseModel):
    """Context information about the current screen"""
    app_name: Optional[str] = None
    screen_type: Optional[str] = None  # home, search, payment, etc.
    ui_elements: List[UIElement] = []
    actionable_elements: List[UIElement] = []
    text_content: List[str] = []
    confidence: float = 0.0


class ScreenAnalyzer:
    """Analyzes mobile app screens and extracts UI elements"""
    
    def __init__(self):
        self.supported_formats = ['png', 'jpg', 'jpeg', 'bmp']
        self.max_image_size = 20 * 1024 * 1024  # 20MB limit
    
    async def analyze_screen(self, screenshot_data: bytes, context: Optional[Dict[str, Any]] = None) -> ScreenContext:
        """Analyze screenshot and extract UI elements and context"""
        try:
            # Validate image
            if not self._validate_image(screenshot_data):
                raise ValueError("Invalid image format or size")
            
            # Convert to PIL Image for processing
            image = Image.open(io.BytesIO(screenshot_data))
            
            # Basic image analysis
            image_info = self._get_image_info(image)
            
            # Use AI to analyze the screen
            ai_analysis = await self._analyze_with_ai(screenshot_data, context)
            
            # Extract UI elements using computer vision
            ui_elements = await self._extract_ui_elements(screenshot_data)
            
            # Filter actionable elements
            actionable_elements = self._filter_actionable_elements(ui_elements)
            
            # Extract text content
            text_content = await self._extract_text_content(screenshot_data)
            
            return ScreenContext(
                app_name=ai_analysis.get('app_name'),
                screen_type=ai_analysis.get('screen_type'),
                ui_elements=ui_elements,
                actionable_elements=actionable_elements,
                text_content=text_content,
                confidence=ai_analysis.get('confidence', 0.8)
            )
            
        except Exception as e:
            logger.error(f"Error analyzing screen: {e}")
            return ScreenContext(
                app_name=None,
                screen_type=None,
                ui_elements=[],
                actionable_elements=[],
                text_content=[],
                confidence=0.0
            )
    
    async def _analyze_with_ai(self, screenshot_data: bytes, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Use AI to analyze the screen content"""
        try:
            prompt = """
            Analyze this mobile app screenshot and provide the following information:
            1. What app is this? (e.g., Swiggy, WhatsApp, Google Pay)
            2. What type of screen is this? (e.g., home, search, payment, settings)
            3. What are the main UI elements visible? (buttons, text fields, images)
            4. What actions can the user take on this screen?
            5. What is the current state or context?
            
            Respond in JSON format with keys: app_name, screen_type, main_elements, available_actions, current_state, confidence
            """
            
            if context:
                prompt += f"\n\nAdditional context: {context}"
            
            analysis_text = await ai_service.analyze_image(screenshot_data, prompt)
            
            # Parse AI response (simplified - in production, use proper JSON parsing)
            return self._parse_ai_analysis(analysis_text)
            
        except Exception as e:
            logger.error(f"Error in AI analysis: {e}")
            return {
                "app_name": None,
                "screen_type": None,
                "confidence": 0.0
            }
    
    async def _extract_ui_elements(self, screenshot_data: bytes) -> List[UIElement]:
        """Extract UI elements using computer vision"""
        try:
            # Convert to OpenCV format
            nparr = np.frombuffer(screenshot_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # Convert to grayscale for processing
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect buttons (rectangular shapes)
            buttons = self._detect_buttons(gray)
            
            # Detect text regions
            text_regions = self._detect_text_regions(gray)
            
            # Combine and format elements
            ui_elements = []
            
            for i, button in enumerate(buttons):
                ui_elements.append(UIElement(
                    id=f"button_{i}",
                    type="button",
                    position=button,
                    confidence=0.8
                ))
            
            for i, text_region in enumerate(text_regions):
                ui_elements.append(UIElement(
                    id=f"text_{i}",
                    type="text",
                    position=text_region,
                    confidence=0.7
                ))
            
            return ui_elements
            
        except Exception as e:
            logger.error(f"Error extracting UI elements: {e}")
            return []
    
    def _detect_buttons(self, gray_image) -> List[Dict[str, int]]:
        """Detect button-like elements in the image"""
        try:
            # Use edge detection to find rectangular shapes
            edges = cv2.Canny(gray_image, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            buttons = []
            for contour in contours:
                # Approximate the contour
                epsilon = 0.02 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                
                # Check if it's roughly rectangular
                if len(approx) >= 4:
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # Filter by size (buttons should be reasonably sized)
                    if 50 < w < 500 and 30 < h < 200:
                        buttons.append({
                            "x": int(x),
                            "y": int(y),
                            "width": int(w),
                            "height": int(h)
                        })
            
            return buttons
            
        except Exception as e:
            logger.error(f"Error detecting buttons: {e}")
            return []
    
    def _detect_text_regions(self, gray_image) -> List[Dict[str, int]]:
        """Detect text regions in the image"""
        try:
            # Use EAST text detector (simplified version)
            # In production, you'd use a proper text detection model
            
            # For now, use simple contour detection for text-like regions
            edges = cv2.Canny(gray_image, 30, 100)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            text_regions = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Text regions are typically wider than they are tall
                if w > h * 2 and 20 < w < 800 and 10 < h < 100:
                    text_regions.append({
                        "x": int(x),
                        "y": int(y),
                        "width": int(w),
                        "height": int(h)
                    })
            
            return text_regions
            
        except Exception as e:
            logger.error(f"Error detecting text regions: {e}")
            return []
    
    async def _extract_text_content(self, screenshot_data: bytes) -> List[str]:
        """Extract text content from the screenshot"""
        try:
            # Use OCR to extract text (simplified - in production, use proper OCR)
            # For now, return empty list - this would be implemented with Tesseract or similar
            return []
            
        except Exception as e:
            logger.error(f"Error extracting text content: {e}")
            return []
    
    def _filter_actionable_elements(self, ui_elements: List[UIElement]) -> List[UIElement]:
        """Filter elements that can be interacted with"""
        actionable_types = ['button', 'input', 'link', 'checkbox', 'radio']
        return [element for element in ui_elements if element.type in actionable_types]
    
    def _get_image_info(self, image: Image.Image) -> Dict[str, Any]:
        """Get basic image information"""
        return {
            "width": image.width,
            "height": image.height,
            "format": image.format,
            "mode": image.mode
        }
    
    def _validate_image(self, image_data: bytes) -> bool:
        """Validate image format and size"""
        if len(image_data) == 0:
            return False
        
        if len(image_data) > self.max_image_size:
            return False
        
        try:
            # Try to open with PIL to validate format
            Image.open(io.BytesIO(image_data))
            return True
        except Exception:
            return False
    
    def _parse_ai_analysis(self, analysis_text: str) -> Dict[str, Any]:
        """Parse AI analysis response"""
        # Simplified parsing - in production, use proper JSON parsing
        try:
            import json
            return json.loads(analysis_text)
        except:
            # Fallback parsing
            return {
                "app_name": "unknown",
                "screen_type": "unknown",
                "confidence": 0.5
            }
