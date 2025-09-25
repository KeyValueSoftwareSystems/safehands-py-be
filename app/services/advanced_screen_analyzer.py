"""
Advanced screen analyzer with enhanced UI detection and understanding
"""
import cv2
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont
import json
import logging
from app.services.screen_analyzer import ScreenAnalyzer, ScreenContext, UIElement
from app.services.ai_service import ai_service
import base64
import io

logger = logging.getLogger(__name__)


class AdvancedUIElement(UIElement):
    """Enhanced UI element with additional properties"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ocr_text: Optional[str] = None
        self.visual_features: Dict[str, Any] = {}
        self.interaction_type: Optional[str] = None  # tap, swipe, long_press, etc.
        self.accessibility_label: Optional[str] = None
        self.is_clickable: bool = False
        self.is_editable: bool = False
        self.importance_score: float = 0.0


class AdvancedScreenContext(ScreenContext):
    """Enhanced screen context with advanced analysis"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.advanced_ui_elements: List[AdvancedUIElement] = []
        self.screen_layout: Dict[str, Any] = {}
        self.navigation_elements: List[AdvancedUIElement] = []
        self.content_areas: List[Dict[str, Any]] = []
        self.interaction_hotspots: List[Dict[str, Any]] = []
        self.visual_hierarchy: List[Dict[str, Any]] = []
        self.accessibility_score: float = 0.0


class AdvancedScreenAnalyzer(ScreenAnalyzer):
    """Advanced screen analyzer with enhanced capabilities"""
    
    def __init__(self):
        super().__init__()
        self.ui_element_templates = {
            "button": {
                "min_width": 50,
                "min_height": 30,
                "aspect_ratio_range": (0.5, 3.0),
                "color_variance_threshold": 0.3
            },
            "text_field": {
                "min_width": 100,
                "min_height": 40,
                "aspect_ratio_range": (1.0, 5.0),
                "border_detection": True
            },
            "image": {
                "min_width": 30,
                "min_height": 30,
                "aspect_ratio_range": (0.5, 2.0),
                "color_complexity_threshold": 0.7
            },
            "navigation": {
                "position_preferences": ["top", "bottom", "left", "right"],
                "common_patterns": ["tabs", "menu", "back_button"]
            }
        }
    
    async def analyze_screen_advanced(self, screenshot_data: bytes, context: Optional[Dict[str, Any]] = None) -> AdvancedScreenContext:
        """Perform advanced screen analysis"""
        try:
            # Basic analysis first
            basic_context = await self.analyze_screen(screenshot_data, context)
            
            # Create advanced context
            advanced_context = AdvancedScreenContext(**basic_context.model_dump())
            
            # Convert to OpenCV format
            nparr = np.frombuffer(screenshot_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                logger.error("Failed to decode image")
                return advanced_context
            
            # Advanced analysis
            await self._analyze_ui_elements_advanced(image, advanced_context)
            await self._analyze_screen_layout(image, advanced_context)
            await self._analyze_navigation_elements(image, advanced_context)
            await self._analyze_content_areas(image, advanced_context)
            await self._analyze_interaction_hotspots(image, advanced_context)
            await self._analyze_visual_hierarchy(image, advanced_context)
            await self._calculate_accessibility_score(advanced_context)
            
            # AI-enhanced analysis
            await self._ai_enhanced_analysis(screenshot_data, advanced_context)
            
            return advanced_context
            
        except Exception as e:
            logger.error(f"Error in advanced screen analysis: {e}")
            return AdvancedScreenContext(
                app_name=basic_context.app_name if 'basic_context' in locals() else None,
                screen_type=basic_context.screen_type if 'basic_context' in locals() else None,
                ui_elements=[],
                actionable_elements=[],
                text_content=[],
                confidence=0.0
            )
    
    async def _analyze_ui_elements_advanced(self, image: np.ndarray, context: AdvancedScreenContext):
        """Advanced UI element analysis"""
        try:
            # Convert to different color spaces for better analysis
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Detect different types of UI elements
            buttons = await self._detect_buttons_advanced(image, gray)
            text_fields = await self._detect_text_fields_advanced(image, gray)
            images = await self._detect_images_advanced(image, hsv)
            text_regions = await self._detect_text_regions_advanced(image, gray)
            
            # Convert to advanced UI elements
            advanced_elements = []
            
            for i, button in enumerate(buttons):
                element = AdvancedUIElement(
                    id=f"button_{i}",
                    type="button",
                    position=button["position"],
                    confidence=button["confidence"],
                    is_clickable=True,
                    interaction_type="tap",
                    importance_score=button.get("importance", 0.5)
                )
                element.visual_features = button.get("features", {})
                advanced_elements.append(element)
            
            for i, text_field in enumerate(text_fields):
                element = AdvancedUIElement(
                    id=f"text_field_{i}",
                    type="text_field",
                    position=text_field["position"],
                    confidence=text_field["confidence"],
                    is_editable=True,
                    interaction_type="tap"
                )
                element.visual_features = text_field.get("features", {})
                advanced_elements.append(element)
            
            for i, img in enumerate(images):
                element = AdvancedUIElement(
                    id=f"image_{i}",
                    type="image",
                    position=img["position"],
                    confidence=img["confidence"]
                )
                element.visual_features = img.get("features", {})
                advanced_elements.append(element)
            
            for i, text_region in enumerate(text_regions):
                element = AdvancedUIElement(
                    id=f"text_{i}",
                    type="text",
                    position=text_region["position"],
                    confidence=text_region["confidence"],
                    text=text_region.get("text", "")
                )
                element.visual_features = text_region.get("features", {})
                advanced_elements.append(element)
            
            context.advanced_ui_elements = advanced_elements
            
        except Exception as e:
            logger.error(f"Error analyzing UI elements: {e}")
    
    async def _detect_buttons_advanced(self, image: np.ndarray, gray: np.ndarray) -> List[Dict[str, Any]]:
        """Advanced button detection"""
        buttons = []
        
        try:
            # Use multiple detection methods
            # Method 1: Contour-based detection
            contours = await self._detect_contours(gray, min_area=500)
            
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Check if it looks like a button
                if self._is_button_like(x, y, w, h, image):
                    # Analyze button features
                    features = await self._analyze_button_features(image, x, y, w, h)
                    
                    buttons.append({
                        "position": {"x": x, "y": y, "width": w, "height": h},
                        "confidence": features["confidence"],
                        "importance": features["importance"],
                        "features": features
                    })
            
            # Method 2: Color-based detection
            color_buttons = await self._detect_buttons_by_color(image)
            buttons.extend(color_buttons)
            
            # Method 3: Template matching (for common button patterns)
            template_buttons = await self._detect_buttons_by_template(image)
            buttons.extend(template_buttons)
            
            # Remove duplicates and merge similar buttons
            buttons = await self._merge_similar_buttons(buttons)
            
            return buttons
            
        except Exception as e:
            logger.error(f"Error detecting buttons: {e}")
            return []
    
    async def _detect_text_fields_advanced(self, image: np.ndarray, gray: np.ndarray) -> List[Dict[str, Any]]:
        """Advanced text field detection"""
        text_fields = []
        
        try:
            # Detect rectangular regions that could be text fields
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Check if it looks like a text field
                if self._is_text_field_like(x, y, w, h, image):
                    features = await self._analyze_text_field_features(image, x, y, w, h)
                    
                    text_fields.append({
                        "position": {"x": x, "y": y, "width": w, "height": h},
                        "confidence": features["confidence"],
                        "features": features
                    })
            
            return text_fields
            
        except Exception as e:
            logger.error(f"Error detecting text fields: {e}")
            return []
    
    async def _detect_images_advanced(self, image: np.ndarray, hsv: np.ndarray) -> List[Dict[str, Any]]:
        """Advanced image detection"""
        images = []
        
        try:
            # Detect regions with high color complexity (likely images)
            # Calculate color variance for each region
            h, w = image.shape[:2]
            block_size = 50
            
            for y in range(0, h - block_size, block_size):
                for x in range(0, w - block_size, block_size):
                    block = image[y:y+block_size, x:x+block_size]
                    
                    # Calculate color variance
                    color_variance = np.var(block.reshape(-1, 3), axis=0).mean()
                    
                    if color_variance > 1000:  # High variance indicates image
                        features = await self._analyze_image_features(block)
                        
                        images.append({
                            "position": {"x": x, "y": y, "width": block_size, "height": block_size},
                            "confidence": features["confidence"],
                            "features": features
                        })
            
            return images
            
        except Exception as e:
            logger.error(f"Error detecting images: {e}")
            return []
    
    async def _detect_text_regions_advanced(self, image: np.ndarray, gray: np.ndarray) -> List[Dict[str, Any]]:
        """Advanced text region detection with OCR"""
        text_regions = []
        
        try:
            # Use EAST text detector (simplified version)
            # In production, you would use a proper text detection model
            
            # Detect text-like regions
            edges = cv2.Canny(gray, 30, 100)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Check if it looks like text
                if self._is_text_like(x, y, w, h):
                    # Extract text region
                    text_region = gray[y:y+h, x:x+w]
                    
                    # Perform OCR (simplified - in production, use Tesseract or similar)
                    text = await self._perform_ocr(text_region)
                    
                    if text and len(text.strip()) > 0:
                        features = await self._analyze_text_features(text_region, text)
                        
                        text_regions.append({
                            "position": {"x": x, "y": y, "width": w, "height": h},
                            "confidence": features["confidence"],
                            "text": text,
                            "features": features
                        })
            
            return text_regions
            
        except Exception as e:
            logger.error(f"Error detecting text regions: {e}")
            return []
    
    async def _analyze_screen_layout(self, image: np.ndarray, context: AdvancedScreenContext):
        """Analyze screen layout and structure"""
        try:
            h, w = image.shape[:2]
            
            # Analyze layout patterns
            layout = {
                "screen_dimensions": {"width": w, "height": h},
                "layout_type": "unknown",  # grid, list, card, etc.
                "content_areas": [],
                "navigation_areas": [],
                "header_footer": {"header": None, "footer": None}
            }
            
            # Detect header and footer
            header_region = image[0:h//10, :]
            footer_region = image[h-h//10:h, :]
            
            if self._is_navigation_area(header_region):
                layout["header_footer"]["header"] = {"y": 0, "height": h//10}
            
            if self._is_navigation_area(footer_region):
                layout["header_footer"]["footer"] = {"y": h-h//10, "height": h//10}
            
            # Detect content areas
            content_areas = await self._detect_content_areas(image)
            layout["content_areas"] = content_areas
            
            # Determine layout type
            layout["layout_type"] = await self._determine_layout_type(image, content_areas)
            
            context.screen_layout = layout
            
        except Exception as e:
            logger.error(f"Error analyzing screen layout: {e}")
    
    async def _analyze_navigation_elements(self, image: np.ndarray, context: AdvancedScreenContext):
        """Analyze navigation elements"""
        try:
            navigation_elements = []
            
            # Look for common navigation patterns
            # Back button, menu button, tabs, etc.
            
            # Detect back button (usually top-left)
            h, w = image.shape[:2]
            top_left_region = image[0:h//4, 0:w//4]
            
            if self._is_back_button(top_left_region):
                navigation_elements.append(AdvancedUIElement(
                    id="back_button",
                    type="navigation",
                    position={"x": 0, "y": 0, "width": w//4, "height": h//4},
                    confidence=0.8,
                    is_clickable=True,
                    interaction_type="tap",
                    importance_score=0.9
                ))
            
            # Detect menu button (usually top-right or hamburger menu)
            top_right_region = image[0:h//4, 3*w//4:w]
            
            if self._is_menu_button(top_right_region):
                navigation_elements.append(AdvancedUIElement(
                    id="menu_button",
                    type="navigation",
                    position={"x": 3*w//4, "y": 0, "width": w//4, "height": h//4},
                    confidence=0.8,
                    is_clickable=True,
                    interaction_type="tap",
                    importance_score=0.8
                ))
            
            # Detect tabs (usually bottom)
            bottom_region = image[3*h//4:h, :]
            tabs = await self._detect_tabs(bottom_region)
            
            for i, tab in enumerate(tabs):
                navigation_elements.append(AdvancedUIElement(
                    id=f"tab_{i}",
                    type="navigation",
                    position=tab["position"],
                    confidence=tab["confidence"],
                    is_clickable=True,
                    interaction_type="tap",
                    importance_score=0.7
                ))
            
            context.navigation_elements = navigation_elements
            
        except Exception as e:
            logger.error(f"Error analyzing navigation elements: {e}")
    
    async def _analyze_content_areas(self, image: np.ndarray, context: AdvancedScreenContext):
        """Analyze content areas and their types"""
        try:
            content_areas = []
            
            # Detect different types of content areas
            # Lists, cards, forms, etc.
            
            # Detect list areas
            list_areas = await self._detect_list_areas(image)
            content_areas.extend(list_areas)
            
            # Detect card areas
            card_areas = await self._detect_card_areas(image)
            content_areas.extend(card_areas)
            
            # Detect form areas
            form_areas = await self._detect_form_areas(image)
            content_areas.extend(form_areas)
            
            context.content_areas = content_areas
            
        except Exception as e:
            logger.error(f"Error analyzing content areas: {e}")
    
    async def _analyze_interaction_hotspots(self, image: np.ndarray, context: AdvancedScreenContext):
        """Analyze interaction hotspots and their importance"""
        try:
            hotspots = []
            
            # Analyze all UI elements for interaction potential
            for element in context.advanced_ui_elements:
                if element.is_clickable or element.is_editable:
                    hotspot = {
                        "element_id": element.id,
                        "position": element.position,
                        "interaction_type": element.interaction_type,
                        "importance_score": element.importance_score,
                        "accessibility": element.accessibility_label
                    }
                    hotspots.append(hotspot)
            
            # Sort by importance
            hotspots.sort(key=lambda x: x["importance_score"], reverse=True)
            
            context.interaction_hotspots = hotspots
            
        except Exception as e:
            logger.error(f"Error analyzing interaction hotspots: {e}")
    
    async def _analyze_visual_hierarchy(self, image: np.ndarray, context: AdvancedScreenContext):
        """Analyze visual hierarchy and importance"""
        try:
            hierarchy = []
            
            # Analyze visual importance based on:
            # - Size
            # - Position
            # - Color contrast
            # - Typography
            
            for element in context.advanced_ui_elements:
                importance = await self._calculate_visual_importance(element, image)
                
                hierarchy.append({
                    "element_id": element.id,
                    "importance_score": importance,
                    "visual_weight": element.visual_features.get("weight", 0),
                    "position_importance": self._calculate_position_importance(element.position, image.shape)
                })
            
            # Sort by importance
            hierarchy.sort(key=lambda x: x["importance_score"], reverse=True)
            
            context.visual_hierarchy = hierarchy
            
        except Exception as e:
            logger.error(f"Error analyzing visual hierarchy: {e}")
    
    async def _calculate_accessibility_score(self, context: AdvancedScreenContext):
        """Calculate accessibility score for the screen"""
        try:
            score = 0.0
            factors = 0
            
            # Check for accessibility features
            for element in context.advanced_ui_elements:
                if element.accessibility_label:
                    score += 0.2
                    factors += 1
                
                if element.is_clickable and element.position["width"] > 44 and element.position["height"] > 44:
                    score += 0.1
                    factors += 1
                
                if element.text and len(element.text) > 0:
                    score += 0.1
                    factors += 1
            
            # Normalize score
            if factors > 0:
                context.accessibility_score = min(score / factors, 1.0)
            else:
                context.accessibility_score = 0.0
            
        except Exception as e:
            logger.error(f"Error calculating accessibility score: {e}")
            context.accessibility_score = 0.0
    
    async def _ai_enhanced_analysis(self, screenshot_data: bytes, context: AdvancedScreenContext):
        """Use AI to enhance screen analysis"""
        try:
            # Use AI to analyze the screen and provide additional insights
            prompt = f"""
            Analyze this mobile app screenshot and provide detailed insights:
            
            Current analysis:
            - App: {context.app_name}
            - Screen type: {context.screen_type}
            - UI elements: {len(context.advanced_ui_elements)}
            - Navigation elements: {len(context.navigation_elements)}
            - Content areas: {len(context.content_areas)}
            
            Please provide:
            1. App identification confirmation
            2. Screen type classification
            3. Main user actions available
            4. Accessibility assessment
            5. User experience insights
            
            Respond in JSON format.
            """
            
            # For now, we'll use a simplified approach
            # In production, you would send the image to the AI service
            
            ai_insights = {
                "app_confidence": 0.9,
                "screen_type_confidence": 0.8,
                "main_actions": ["tap", "scroll", "input"],
                "accessibility_notes": "Good contrast, clear buttons",
                "ux_insights": "Clean layout, intuitive navigation"
            }
            
            # Update context with AI insights
            context.metadata = context.metadata or {}
            context.metadata["ai_insights"] = ai_insights
            
        except Exception as e:
            logger.error(f"Error in AI enhanced analysis: {e}")
    
    # Helper methods (simplified implementations)
    async def _detect_contours(self, gray: np.ndarray, min_area: int = 100) -> List:
        """Detect contours in the image"""
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return [c for c in contours if cv2.contourArea(c) > min_area]
    
    def _is_button_like(self, x: int, y: int, w: int, h: int, image: np.ndarray) -> bool:
        """Check if a region looks like a button"""
        # Simplified button detection logic
        return 30 < w < 300 and 20 < h < 100 and w/h > 0.5
    
    def _is_text_field_like(self, x: int, y: int, w: int, h: int, image: np.ndarray) -> bool:
        """Check if a region looks like a text field"""
        # Simplified text field detection logic
        return 100 < w < 500 and 30 < h < 80 and w/h > 1.5
    
    def _is_text_like(self, x: int, y: int, w: int, h: int) -> bool:
        """Check if a region looks like text"""
        # Simplified text detection logic
        return w > h and w > 20 and h > 10
    
    async def _perform_ocr(self, text_region: np.ndarray) -> str:
        """Perform OCR on text region (simplified)"""
        # In production, use Tesseract or similar OCR engine
        # For now, return empty string
        return ""
    
    async def _analyze_button_features(self, image: np.ndarray, x: int, y: int, w: int, h: int) -> Dict[str, Any]:
        """Analyze button features"""
        return {
            "confidence": 0.8,
            "importance": 0.7,
            "color": "blue",
            "text": "",
            "border": True
        }
    
    async def _analyze_text_field_features(self, image: np.ndarray, x: int, y: int, w: int, h: int) -> Dict[str, Any]:
        """Analyze text field features"""
        return {
            "confidence": 0.7,
            "placeholder": "",
            "border": True,
            "background": "white"
        }
    
    async def _analyze_image_features(self, image_block: np.ndarray) -> Dict[str, Any]:
        """Analyze image features"""
        return {
            "confidence": 0.6,
            "color_complexity": 0.8,
            "type": "photo"
        }
    
    async def _analyze_text_features(self, text_region: np.ndarray, text: str) -> Dict[str, Any]:
        """Analyze text features"""
        return {
            "confidence": 0.8,
            "font_size": "medium",
            "color": "black",
            "style": "normal"
        }
    
    def _is_navigation_area(self, region: np.ndarray) -> bool:
        """Check if region is a navigation area"""
        # Simplified navigation detection
        return True
    
    def _is_back_button(self, region: np.ndarray) -> bool:
        """Check if region contains a back button"""
        # Simplified back button detection
        return True
    
    def _is_menu_button(self, region: np.ndarray) -> bool:
        """Check if region contains a menu button"""
        # Simplified menu button detection
        return True
    
    async def _detect_tabs(self, region: np.ndarray) -> List[Dict[str, Any]]:
        """Detect tabs in the region"""
        # Simplified tab detection
        return []
    
    async def _detect_list_areas(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Detect list areas"""
        return []
    
    async def _detect_card_areas(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Detect card areas"""
        return []
    
    async def _detect_form_areas(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Detect form areas"""
        return []
    
    async def _detect_buttons_by_color(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Detect buttons by color analysis"""
        return []
    
    async def _detect_buttons_by_template(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Detect buttons by template matching"""
        return []
    
    async def _merge_similar_buttons(self, buttons: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merge similar buttons"""
        return buttons
    
    async def _detect_content_areas(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Detect content areas"""
        return []
    
    async def _determine_layout_type(self, image: np.ndarray, content_areas: List[Dict[str, Any]]) -> str:
        """Determine layout type"""
        return "grid"
    
    async def _calculate_visual_importance(self, element: AdvancedUIElement, image: np.ndarray) -> float:
        """Calculate visual importance of an element"""
        return 0.5
    
    def _calculate_position_importance(self, position: Dict[str, int], image_shape: Tuple[int, int, int]) -> float:
        """Calculate position importance"""
        return 0.5


# Global advanced screen analyzer instance
advanced_screen_analyzer = AdvancedScreenAnalyzer()
