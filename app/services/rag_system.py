"""
RAG (Retrieval-Augmented Generation) system for knowledge base and app-specific guidance
"""
import json
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import logging
from app.services.ai_service import ai_service
from app.services.screen_analyzer import ScreenContext
import hashlib

logger = logging.getLogger(__name__)


class KnowledgeDocument:
    """Represents a knowledge document in the RAG system"""
    def __init__(self, 
                 doc_id: str,
                 title: str,
                 content: str,
                 doc_type: str,
                 app_context: Optional[str] = None,
                 tags: List[str] = None,
                 metadata: Dict[str, Any] = None):
        self.doc_id = doc_id
        self.title = title
        self.content = content
        self.doc_type = doc_type  # "app_guide", "troubleshooting", "faq", "tips"
        self.app_context = app_context
        self.tags = tags or []
        self.metadata = metadata or {}
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.usage_count = 0
        self.success_rate = 0.0


class RAGSystem:
    """RAG system for retrieving and generating contextual assistance"""
    
    def __init__(self):
        self.knowledge_base: Dict[str, KnowledgeDocument] = {}
        self.vector_embeddings: Dict[str, List[float]] = {}
        self.search_index: Dict[str, List[str]] = {}
        self.initialized = False
        
        # Initialize with default knowledge base
        self._initialize_default_knowledge()
    
    def _initialize_default_knowledge(self):
        """Initialize the knowledge base with default app guidance"""
        try:
            # Swiggy App Guide
            swiggy_guide = KnowledgeDocument(
                doc_id="swiggy_guide_001",
                title="How to Order Food on Swiggy",
                content="""
                Step-by-step guide to order food on Swiggy:
                1. Open the Swiggy app (orange icon with white spoon)
                2. Allow location access when prompted
                3. Browse restaurants or search for specific food
                4. Select a restaurant
                5. Choose your food items
                6. Add items to cart
                7. Review your order
                8. Select delivery address
                9. Choose payment method
                10. Place your order
                
                Tips:
                - You can filter restaurants by cuisine type
                - Check delivery time before ordering
                - Save your address for faster checkout
                - Use promo codes for discounts
                """,
                doc_type="app_guide",
                app_context="swiggy",
                tags=["food", "ordering", "delivery", "restaurant"]
            )
            
            # WhatsApp Guide
            whatsapp_guide = KnowledgeDocument(
                doc_id="whatsapp_guide_001",
                title="How to Send Messages on WhatsApp",
                content="""
                Step-by-step guide to send messages on WhatsApp:
                1. Open WhatsApp app (green icon with white phone)
                2. Tap on the chat icon (speech bubble) at the bottom
                3. Select a contact or start a new chat
                4. Type your message in the text box
                5. Tap the send button (paper plane icon)
                
                Additional features:
                - Send photos: Tap camera icon
                - Send voice message: Hold microphone icon
                - Make voice call: Tap phone icon
                - Make video call: Tap video icon
                
                Tips:
                - You can search for contacts using the search bar
                - Long press a message to reply or forward
                - Use emojis by tapping the smiley face icon
                """,
                doc_type="app_guide",
                app_context="whatsapp",
                tags=["messaging", "chat", "communication", "contacts"]
            )
            
            # Google Pay Guide
            gpay_guide = KnowledgeDocument(
                doc_id="gpay_guide_001",
                title="How to Make Payments with Google Pay",
                content="""
                Step-by-step guide to make payments with Google Pay:
                1. Open Google Pay app (blue icon with white "G")
                2. Set up your account if first time
                3. Add your bank account or card
                4. To send money: Tap "Send" button
                5. Enter recipient's phone number or scan QR code
                6. Enter amount
                7. Add note (optional)
                8. Tap "Pay" button
                9. Enter UPI PIN to confirm
                
                For bill payments:
                1. Tap "Pay bills" on home screen
                2. Select bill type (electricity, water, etc.)
                3. Enter bill details
                4. Confirm and pay
                
                Tips:
                - Keep your UPI PIN secure
                - Verify recipient details before sending
                - Check transaction history regularly
                """,
                doc_type="app_guide",
                app_context="google_pay",
                tags=["payment", "upi", "money", "bills", "banking"]
            )
            
            # Common Troubleshooting
            troubleshooting = KnowledgeDocument(
                doc_id="troubleshooting_001",
                title="Common App Issues and Solutions",
                content="""
                Common issues and their solutions:
                
                App won't open:
                - Restart your phone
                - Check internet connection
                - Update the app from Play Store
                - Clear app cache in settings
                
                App is slow:
                - Close other apps
                - Restart the app
                - Check internet speed
                - Clear app data if needed
                
                Can't find a feature:
                - Look for menu button (three lines)
                - Check settings or profile section
                - Search within the app
                - Ask for help in the app
                
                Payment issues:
                - Check internet connection
                - Verify bank account details
                - Try different payment method
                - Contact customer support
                """,
                doc_type="troubleshooting",
                app_context="general",
                tags=["troubleshooting", "issues", "problems", "solutions"]
            )
            
            # Add documents to knowledge base
            self._add_document(swiggy_guide)
            self._add_document(whatsapp_guide)
            self._add_document(gpay_guide)
            self._add_document(troubleshooting)
            
            # Build search index
            self._build_search_index()
            
            self.initialized = True
            logger.info("RAG system initialized with default knowledge base")
            
        except Exception as e:
            logger.error(f"Error initializing RAG system: {e}")
    
    def _add_document(self, document: KnowledgeDocument):
        """Add a document to the knowledge base"""
        self.knowledge_base[document.doc_id] = document
        
        # Generate embeddings (simplified - in production, use proper embedding model)
        embedding = self._generate_embedding(document.content)
        self.vector_embeddings[document.doc_id] = embedding
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text (simplified implementation)"""
        # In production, use a proper embedding model like OpenAI's text-embedding-ada-002
        # For now, create a simple hash-based embedding
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()
        
        # Convert to float vector
        embedding = []
        for i in range(0, len(hash_bytes), 4):
            chunk = hash_bytes[i:i+4]
            if len(chunk) == 4:
                value = int.from_bytes(chunk, byteorder='big')
                embedding.append(value / (2**32))  # Normalize to [0, 1]
        
        # Pad or truncate to fixed size
        target_size = 128
        while len(embedding) < target_size:
            embedding.append(0.0)
        embedding = embedding[:target_size]
        
        return embedding
    
    def _build_search_index(self):
        """Build search index for fast retrieval"""
        for doc_id, document in self.knowledge_base.items():
            # Index by app context
            if document.app_context:
                if document.app_context not in self.search_index:
                    self.search_index[document.app_context] = []
                self.search_index[document.app_context].append(doc_id)
            
            # Index by tags
            for tag in document.tags:
                if tag not in self.search_index:
                    self.search_index[tag] = []
                self.search_index[tag].append(doc_id)
            
            # Index by document type
            if document.doc_type not in self.search_index:
                self.search_index[document.doc_type] = []
            self.search_index[document.doc_type].append(doc_id)
    
    async def retrieve_relevant_documents(self, 
                                        query: str, 
                                        app_context: Optional[str] = None,
                                        doc_type: Optional[str] = None,
                                        limit: int = 5) -> List[KnowledgeDocument]:
        """Retrieve relevant documents based on query and context"""
        try:
            if not self.initialized:
                logger.warning("RAG system not initialized")
                return []
            
            # Generate query embedding
            query_embedding = self._generate_embedding(query)
            
            # Find relevant documents using improved search
            scored_docs = []
            
            # First, try keyword-based filtering for better relevance
            query_lower = query.lower()
            food_keywords = ['food', 'order', 'ordering', 'restaurant', 'restaurnt', 'swiggy', 'zomato', 'delivery', 'eat', 'meal', 'chosen', 'choose', 'select']
            is_food_query = any(keyword in query_lower for keyword in food_keywords)
            
            # Search all documents and score them
            for doc in self.knowledge_base.values():
                score = 0.0
                
                # Check if document type matches
                if doc_type and doc.doc_type != doc_type:
                    continue
                
                # Boost score for app context match
                if app_context and doc.app_context == app_context:
                    score += 0.3
                
                # Boost score for food-related queries matching food-related documents
                if is_food_query:
                    if doc.app_context in ['swiggy', 'zomato'] or any(tag in ['food', 'ordering', 'delivery', 'restaurant'] for tag in doc.tags):
                        score += 0.8  # Strong boost for food-related docs
                    elif doc.app_context in ['whatsapp', 'google_pay']:
                        score -= 0.5  # Strong penalty for non-food apps
                    elif doc.doc_type == 'troubleshooting':
                        score -= 0.3  # Penalty for troubleshooting docs
                
                # Boost score for keyword matches in title and content
                doc_text = (doc.title + " " + doc.content).lower()
                for keyword in food_keywords:
                    if keyword in doc_text:
                        score += 0.1
                
                # Add semantic similarity score
                if doc.doc_id in self.vector_embeddings:
                    similarity = self._calculate_similarity(query_embedding, self.vector_embeddings[doc.doc_id])
                    score += similarity * 0.3
                
                # Only include documents with positive scores
                if score > 0:
                    scored_docs.append((doc, score))
                    logger.info(f"RAG Search: {doc.title} - Score: {score:.2f}, App: {doc.app_context}, Type: {doc.doc_type}")
            
            # Sort by score and return top results
            scored_docs.sort(key=lambda x: x[1], reverse=True)
            return [doc for doc, score in scored_docs[:limit]]
            
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return []
    
    async def search(self, query: str, app_context: Optional[str] = None, limit: int = 5, top_k: Optional[int] = None) -> List[KnowledgeDocument]:
        """Search method - alias for retrieve_relevant_documents"""
        # Use top_k if provided, otherwise use limit
        search_limit = top_k if top_k is not None else limit
        return await self.retrieve_relevant_documents(query, app_context, limit=search_limit)
    
    def _calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        try:
            if len(embedding1) != len(embedding2):
                return 0.0
            
            dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
            magnitude1 = sum(a * a for a in embedding1) ** 0.5
            magnitude2 = sum(b * b for b in embedding2) ** 0.5
            
            if magnitude1 == 0 or magnitude2 == 0:
                return 0.0
            
            return dot_product / (magnitude1 * magnitude2)
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0
    
    async def generate_contextual_response(self, 
                                         query: str,
                                         screen_context: Optional[ScreenContext] = None,
                                         user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate contextual response using RAG"""
        try:
            # Determine app context
            app_context = None
            if screen_context and screen_context.app_name:
                app_context = screen_context.app_name.lower()
            
            # Retrieve relevant documents
            relevant_docs = await self.retrieve_relevant_documents(
                query=query,
                app_context=app_context,
                limit=3
            )
            
            if not relevant_docs:
                return {
                    "response": "I don't have specific guidance for that. Let me help you in a general way.",
                    "confidence": 0.3,
                    "sources": []
                }
            
            # Build context from relevant documents
            context = self._build_context_from_documents(relevant_docs)
            
            # Generate response using AI
            response = await self._generate_ai_response(query, context, user_context)
            
            # Update document usage
            for doc in relevant_docs:
                doc.usage_count += 1
            
            return {
                "response": response,
                "confidence": 0.8,
                "sources": [{"title": doc.title, "type": doc.doc_type} for doc in relevant_docs],
                "context": context
            }
            
        except Exception as e:
            logger.error(f"Error generating contextual response: {e}")
            return {
                "response": "I'm having trouble accessing my knowledge base. Let me help you in a general way.",
                "confidence": 0.2,
                "sources": []
            }
    
    def _build_context_from_documents(self, documents: List[KnowledgeDocument]) -> str:
        """Build context string from relevant documents"""
        context_parts = []
        
        for doc in documents:
            context_parts.append(f"Title: {doc.title}")
            context_parts.append(f"Content: {doc.content}")
            context_parts.append("---")
        
        return "\n".join(context_parts)
    
    async def _generate_ai_response(self, 
                                  query: str, 
                                  context: str, 
                                  user_context: Optional[Dict[str, Any]] = None) -> str:
        """Generate AI response using retrieved context"""
        try:
            # Build prompt with context
            prompt = f"""
            Based on the following knowledge base context, provide helpful guidance for the user's query.
            
            User Query: "{query}"
            
            Knowledge Base Context:
            {context}
            
            User Context: {user_context or "No additional context"}
            
            Please provide:
            1. Clear, step-by-step guidance
            2. Specific instructions relevant to the user's query
            3. Helpful tips and best practices
            4. Encouraging and patient tone suitable for seniors
            
            Keep the response concise but comprehensive.
            """
            
            # Generate response using AI
            response = await ai_service.generate_text(
                prompt=prompt,
                model="gpt-3.5-turbo",
                temperature=0.3,
                max_tokens=500
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return "I'm here to help you. Could you please tell me more about what you'd like to do?"
    
    async def add_document(self, 
                          title: str, 
                          content: str, 
                          doc_type: str,
                          app_context: Optional[str] = None,
                          tags: List[str] = None) -> str:
        """Add a new document to the knowledge base"""
        try:
            # Generate document ID
            doc_id = f"{doc_type}_{len(self.knowledge_base) + 1:03d}"
            
            # Create document
            document = KnowledgeDocument(
                doc_id=doc_id,
                title=title,
                content=content,
                doc_type=doc_type,
                app_context=app_context,
                tags=tags or []
            )
            
            # Add to knowledge base
            self._add_document(document)
            
            # Rebuild search index
            self._build_search_index()
            
            logger.info(f"Added document: {doc_id}")
            return doc_id
            
        except Exception as e:
            logger.error(f"Error adding document: {e}")
            return ""
    
    async def update_document_success(self, doc_id: str, success: bool):
        """Update document success rate based on user feedback"""
        try:
            if doc_id in self.knowledge_base:
                doc = self.knowledge_base[doc_id]
                # Simple success rate calculation
                if success:
                    doc.success_rate = min(doc.success_rate + 0.1, 1.0)
                else:
                    doc.success_rate = max(doc.success_rate - 0.1, 0.0)
                
                doc.updated_at = datetime.utcnow()
                
        except Exception as e:
            logger.error(f"Error updating document success: {e}")
    
    def get_knowledge_base_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base"""
        try:
            total_docs = len(self.knowledge_base)
            doc_types = {}
            app_contexts = {}
            
            for doc in self.knowledge_base.values():
                # Count by document type
                doc_types[doc.doc_type] = doc_types.get(doc.doc_type, 0) + 1
                
                # Count by app context
                if doc.app_context:
                    app_contexts[doc.app_context] = app_contexts.get(doc.app_context, 0) + 1
            
            return {
                "total_documents": total_docs,
                "document_types": doc_types,
                "app_contexts": app_contexts,
                "search_index_size": len(self.search_index),
                "initialized": self.initialized
            }
            
        except Exception as e:
            logger.error(f"Error getting knowledge base stats: {e}")
            return {}


# Global RAG system instance
rag_system = RAGSystem()
