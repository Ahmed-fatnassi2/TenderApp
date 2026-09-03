# # services/smart_construction_agent.py - PURE LLM-POWERED (No Hardcoded Keywords)
# import os
# import logging
# from typing import Dict, List, Any, Optional
# import re
# import json

# from langchain_openai import ChatOpenAI
# from langchain_core.tools import tool
# from langchain_core.messages import HumanMessage, SystemMessage
# from langchain.agents import create_agent

# from models.tender import Tender
# from database import db
# from services.openrag_client import OpenRAGClient

# logger = logging.getLogger(__name__)

# class SmartConstructionAgent:
#     """Pure LLM-powered agent - no hardcoded keywords"""
    
#     def __init__(self, openai_api_key: Optional[str] = None):
#         self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
#         if not self.openai_api_key:
#             raise ValueError("OPENAI_API_KEY is required")
        
#         self.llm = ChatOpenAI(
#             model="gpt-4o-mini",
#             temperature=0.1,
#             api_key=self.openai_api_key
#         )
        
#         self.openrag = OpenRAGClient()
#         self.agent = self._create_agent()
        
#         logger.info("🏗️ Smart Construction Agent ready")
    
#     def _create_agent(self):
#         @tool
#         def search_tenders(query: str) -> str:
#             """Search for construction tenders"""
#             return self._search_tenders(query)
        
#         @tool
#         def analyze_tender(reference: str) -> str:
#             """Analyze a specific tender by reference"""
#             return self._analyze_tender(reference)
        
#         tools = [search_tenders, analyze_tender]
        
#         agent = create_agent(
#             model=self.llm,
#             tools=tools,
#             system_prompt="""You are a highly intelligent Construction Tender Agent for Tunisia.

#             Your role is to:
#             1. Understand what the user is looking for through natural language understanding
#             2. Search for tenders using semantic understanding
#             3. Filter results intelligently based on the user's intent
#             4. Provide insightful analysis and recommendations

#             You understand construction terminology in French, English, and Arabic.
#             You know what a "tender" is, what "construction" means, and can identify 
#             different types of projects (roads, schools, hospitals, buildings, etc.)

#             Be helpful, practical, and specific. Always consider the Tunisian context.
#             """
#         )
        
#         return agent
    
#     def _understand_query(self, query: str) -> Dict[str, Any]:
#         """Pure LLM-powered query understanding - no hardcoded rules"""
#         try:
#             understanding_prompt = f"""
#             Analyze this user query about construction tenders:
#             "{query}"
            
#             Return a JSON with:
#             1. intent: What is the user looking for? Use natural language description
#             2. keywords: Extract the key terms (in the original language)
#             3. sector: What sector is this? (education, healthcare, infrastructure, etc.)
#             4. priority: How specific is this query? (very_specific, specific, general)
#             5. language: The language of the query (fr, en, ar)
#             6. category: The category of construction (roads, buildings, infrastructure, etc.)
#             7. description: A clear description of what the user wants
            
#             Be flexible - understand the query naturally, don't force categories.
#             """
            
#             response = self.llm.invoke(understanding_prompt)
#             result = json.loads(response.content)
#             logger.info(f"📊 Query understanding: {result}")
#             return result
            
#         except Exception as e:
#             logger.error(f"Query understanding error: {e}")
#             return {
#                 'intent': query,
#                 'keywords': [],
#                 'sector': 'general',
#                 'priority': 'general',
#                 'language': 'unknown',
#                 'category': 'general',
#                 'description': query
#             }
    
#     def _filter_by_intent(self, documents: List[Dict], query: str, intent: Dict) -> List[Dict]:
#         """Pure LLM-powered filtering - no hardcoded rules"""
#         try:
#             if not documents:
#                 return []
            
#             # Prepare documents for LLM
#             doc_summaries = []
#             for i, doc in enumerate(documents[:30]):
#                 metadata = doc.get('metadata', {})
#                 content = doc.get('content', '')
#                 title = metadata.get('title', '')
#                 buyer = metadata.get('buyer', '')
#                 deadline = metadata.get('deadline', '')
                
#                 text = f"""
#                 Document {i+1}:
#                 Title: {title}
#                 Buyer: {buyer}
#                 Deadline: {deadline}
#                 Description: {content[:400]}
#                 """
#                 doc_summaries.append(text)
            
#             # Pure LLM filtering - no hardcoded rules
#             filter_prompt = f"""
#             User Query: "{query}"
#             User Intent: {intent.get('description', '')}
            
#             Your task: Review each document and determine if it is relevant to the user's query.
            
#             Think like a human expert:
#             1. What is the user really looking for?
#             2. Does this document match what the user wants?
#             3. Is this document clearly relevant or only tangentially related?
            
#             Use your natural understanding of:
#             - What the user's query means
#             - What each document is about
#             - Whether there's a genuine match
            
#             Here are the documents:
            
#             {chr(10).join(doc_summaries)}
            
#             Return ONLY a JSON array of document numbers that are RELEVANT.
#             Example: [0, 2, 5]
            
#             If none are relevant, return: []
            
#             Only return the JSON array, nothing else.
#             """
            
#             response = self.llm.invoke(filter_prompt)
            
#             # Parse the response
#             try:
#                 content = response.content.strip()
#                 # Try to find JSON array
#                 match = re.search(r'\[([^\]]*)\]', content)
#                 if match:
#                     indices = json.loads(f'[{match.group(1)}]')
#                     filtered = [documents[i] for i in indices if i < len(documents)]
#                     logger.info(f"🎯 LLM filtered to {len(filtered)} documents (from {len(documents)})")
#                     return filtered
#                 else:
#                     # Try parsing the whole response as JSON
#                     data = json.loads(content)
#                     if isinstance(data, list):
#                         filtered = [documents[i] for i in data if i < len(documents)]
#                         return filtered
#             except Exception as e:
#                 logger.error(f"Parse error: {e}")
#                 # Ultimate fallback - let the LLM decide with a simpler prompt
#                 fallback_filter = f"""
#                 From this list of {len(documents)} documents, which ones are most relevant to: "{query}"
#                 Return a JSON array of indices.
#                 """
#                 try:
#                     fb_response = self.llm.invoke(fallback_filter)
#                     match = re.search(r'\[([^\]]*)\]', fb_response.content)
#                     if match:
#                         indices = json.loads(f'[{match.group(1)}]')
#                         return [documents[i] for i in indices if i < len(documents)]
#                 except:
#                     pass
                
#                 # Last resort - return first few documents
#                 return documents[:5]
            
#         except Exception as e:
#             logger.error(f"Filter error: {e}")
#             return documents[:5]
    
#     def _search_tenders(self, query: str) -> str:
#         """Search using OpenRAG with pure LLM understanding"""
#         try:
#             # 1. Let LLM understand the query
#             intent = self._understand_query(query)
            
#             # 2. Search OpenRAG (get more to filter)
#             results = self.openrag.search(
#                 query=query,
#                 top_k=30,
#                 partition_name='tenders',
#                 similarity_threshold=0.35
#             )
            
#             if results and 'documents' in results:
#                 docs = results['documents']
                
#                 # 3. Let LLM filter intelligently
#                 filtered_docs = self._filter_by_intent(docs, query, intent)
                
#                 # 4. Format results
#                 if filtered_docs:
#                     formatted = []
#                     for i, doc in enumerate(filtered_docs[:10], 1):
#                         metadata = doc.get('metadata', {})
#                         content = doc.get('content', '')
                        
#                         title = metadata.get('title', '')
#                         if not title:
#                             title_match = re.search(r'Title:\s*([^\n]+)', content)
#                             if title_match:
#                                 title = title_match.group(1).strip()
                        
#                         reference = metadata.get('reference', '')
#                         if not reference:
#                             ref_match = re.search(r'Reference:\s*([^\n]+)', content)
#                             if ref_match:
#                                 reference = ref_match.group(1).strip()
                        
#                         buyer = metadata.get('buyer', '')
#                         if not buyer:
#                             buyer_match = re.search(r'Buyer:\s*([^\n]+)', content)
#                             if buyer_match:
#                                 buyer = buyer_match.group(1).strip()
                        
#                         deadline = metadata.get('deadline', '')
#                         if not deadline:
#                             deadline_match = re.search(r'Deadline:\s*([^\n]+)', content)
#                             if deadline_match:
#                                 deadline = deadline_match.group(1).strip()
                        
#                         formatted.append(
#                             f"{i}. 📋 {title or 'Untitled'}\n"
#                             f"   Reference: {reference or 'N/A'}\n"
#                             f"   Buyer: {buyer or 'Unknown'}\n"
#                             f"   Deadline: {deadline or 'N/A'}"
#                         )
                    
#                     return f"🎯 Found {len(formatted)} relevant tenders for '{query}':\n\n" + "\n\n".join(formatted)
            
#             return f"No relevant tenders found for '{query}'. Try a different search term."
            
#         except Exception as e:
#             logger.error(f"Search error: {e}")
#             return f"Error searching: {str(e)}"
    
#     def search_tenders(self, query: str, top_k: int = 10) -> Dict[str, Any]:
#         """Public search method with pure LLM filtering"""
#         try:
#             # 1. Let LLM understand the query
#             intent = self._understand_query(query)
            
#             # 2. Search OpenRAG
#             results = self.openrag.search(
#                 query=query,
#                 top_k=top_k * 3,
#                 partition_name='tenders',
#                 similarity_threshold=0.35
#             )
            
#             if results and 'documents' in results:
#                 docs = results.get('documents', [])
                
#                 # 3. Let LLM filter intelligently
#                 filtered_docs = self._filter_by_intent(docs, query, intent)
                
#                 # 4. Format results
#                 formatted_docs = []
#                 for doc in filtered_docs[:top_k]:
#                     metadata = doc.get('metadata', {})
#                     content = doc.get('content', '')
                    
#                     title = metadata.get('title', '')
#                     if not title:
#                         title_match = re.search(r'Title:\s*([^\n]+)', content)
#                         if title_match:
#                             title = title_match.group(1).strip()
                    
#                     reference = metadata.get('reference', '')
#                     if not reference:
#                         ref_match = re.search(r'Reference:\s*([^\n]+)', content)
#                         if ref_match:
#                             reference = ref_match.group(1).strip()
                    
#                     buyer = metadata.get('buyer', '')
#                     if not buyer:
#                         buyer_match = re.search(r'Buyer:\s*([^\n]+)', content)
#                         if buyer_match:
#                             buyer = buyer_match.group(1).strip()
                    
#                     deadline = metadata.get('deadline', '')
#                     if not deadline:
#                         deadline_match = re.search(r'Deadline:\s*([^\n]+)', content)
#                         if deadline_match:
#                             deadline = deadline_match.group(1).strip()
                    
#                     formatted_docs.append({
#                         'metadata': {
#                             'title': title or 'Untitled',
#                             'reference': reference or 'N/A',
#                             'buyer': buyer or 'Unknown',
#                             'deadline': deadline or 'N/A',
#                             'intent': intent.get('intent', 'general'),
#                             'sector': intent.get('sector', 'general'),
#                             'category': intent.get('category', 'general')
#                         },
#                         'content': content
#                     })
                
#                 return {
#                     'success': True,
#                     'total_found': len(formatted_docs),
#                     'documents': formatted_docs,
#                     'query': query,
#                     'intent': intent,
#                     'source': 'openrag_filtered'
#                 }
            
#             return {
#                 'success': True,
#                 'total_found': 0,
#                 'documents': [],
#                 'query': query,
#                 'message': 'No tenders found'
#             }
            
#         except Exception as e:
#             logger.error(f"Search error: {e}")
#             return {
#                 'success': False,
#                 'error': str(e),
#                 'total_found': 0,
#                 'documents': []
#             }
    
#     def _analyze_tender(self, reference: str) -> str:
#         """Analyze a specific tender"""
#         try:
#             tender = Tender.query.filter_by(reference=reference).first()
#             if not tender:
#                 return f"Tender with reference '{reference}' not found."
            
#             tender_dict = tender.to_dict()
            
#             # Let LLM analyze
#             analysis_prompt = f"""
#             Analyze this construction tender:
            
#             Title: {tender_dict.get('title', 'N/A')}
#             Buyer: {tender_dict.get('buyer', 'N/A')}
#             Reference: {tender_dict.get('reference', 'N/A')}
#             Deadline: {tender_dict.get('deadline', 'N/A')}
#             Source: {tender_dict.get('source', 'N/A')}
            
#             Provide a brief analysis:
#             1. What type of project is this?
#             2. Key requirements
#             3. Who should bid on this?
#             4. Any important considerations
#             """
            
#             try:
#                 analysis = self.llm.invoke(analysis_prompt)
#                 return f"""
# 📋 TENDER ANALYSIS

# Title: {tender_dict.get('title', 'N/A')}
# Reference: {tender_dict.get('reference', 'N/A')}
# Buyer: {tender_dict.get('buyer', 'N/A')}
# Deadline: {tender_dict.get('deadline', 'N/A')}
# Source: {tender_dict.get('source', 'N/A')}

# {analysis.content}
# """
#             except:
#                 return f"""
# 📋 TENDER ANALYSIS

# Title: {tender_dict.get('title', 'N/A')}
# Reference: {tender_dict.get('reference', 'N/A')}
# Buyer: {tender_dict.get('buyer', 'N/A')}
# Deadline: {tender_dict.get('deadline', 'N/A')}
# Source: {tender_dict.get('source', 'N/A')}
# """
#         except Exception as e:
#             logger.error(f"Analysis error: {e}")
#             return f"Error analyzing tender: {str(e)}"
    
#     def chat(self, message: str) -> Dict[str, Any]:
#         """Main chat method"""
#         try:
#             response = self.agent.invoke(
#                 {"messages": [HumanMessage(content=message)]}
#             )
            
#             if isinstance(response, dict) and 'messages' in response:
#                 last_message = response['messages'][-1]
#                 output = last_message.content if hasattr(last_message, 'content') else str(last_message)
#             else:
#                 output = str(response)
            
#             return {
#                 'success': True,
#                 'response': output,
#                 'type': 'agent_response'
#             }
            
#         except Exception as e:
#             logger.error(f"Chat error: {e}")
#             return {
#                 'success': False,
#                 'error': str(e),
#                 'response': f"Error: {str(e)}"
#             }

# services/smart_construction_agent.py - COMPLETE FIXED VERSION
# services/smart_construction_agent.py - PROPERLY INDENTED
import os
import logging
from typing import Dict, List, Any, Optional
import re
import json

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.agents import create_agent

from models.tender import Tender
from database import db
from services.openrag_client import OpenRAGClient

logger = logging.getLogger(__name__)

class SmartConstructionAgent:
    """Smart construction agent with proper translation and filtering"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required")
        
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.1,
            api_key=self.openai_api_key
        )
        
        self.openrag = OpenRAGClient()
        self.agent = self._create_agent()
        
        logger.info("🏗️ Smart Construction Agent ready")
    
    def _create_agent(self):
        @tool
        def search_tenders(query: str) -> str:
            """Search for construction tenders"""
            return self._search_tenders(query)
        
        tools = [search_tenders]
        
        agent = create_agent(
            model=self.llm,
            tools=tools,
            system_prompt="""You are a Construction Tender Agent for Tunisia.
            You help users find construction tenders. Search and present results clearly.
            """
        )
        
        return agent
    
    def _translate_to_french(self, query: str) -> str:
        """Translate query to French using the most common phrasing"""
        try:
            translate_prompt = f"""You are a translator specializing in Tunisian construction tenders.
            
            Translate this text to French using the most common phrasing found in Tunisian government tenders.
            
            IMPORTANT GUIDELINES:
            - "road construction" → "construction de routes" (NOT "construction routière")
            - "school construction" → "construction d'écoles" 
            - "hospital construction" → "construction d'hôpitaux"
            - "building construction" → "construction de bâtiments"
            
            Use the most natural and common French phrasing for Tunisian tenders.
            Return ONLY the French translation, nothing else.
            
            Text to translate: "{query}"
            
            French translation (using common tender phrasing):"""
            
            response = self.llm.invoke(translate_prompt)
            french = response.content.strip().strip('"').strip("'")
            
            # Clean up common prefixes
            if french.startswith("French translation (using common tender phrasing):"):
                french = french.replace("French translation (using common tender phrasing):", "").strip()
            if french.startswith("French translation:"):
                french = french.replace("French translation:", "").strip()
            if french.startswith("Translation:"):
                french = french.replace("Translation:", "").strip()
            
            # Post-processing fixes for common phrases
            if "road" in query.lower() and "construction" in query.lower():
                # Ensure it's "construction de routes" not "construction routière"
                if "routière" in french.lower():
                    french = french.replace("routière", "de routes")
                if "construction routière" in french.lower():
                    french = french.replace("construction routière", "construction de routes")
            
            logger.info(f"📊 Translated: '{query}' → '{french}'")
            return french
            
        except Exception as e:
            logger.error(f"Translation error: {e}")
            # Manual fallback for common phrases
            if "road construction" in query.lower():
                return "construction de routes"
            return query
    
    def _is_english_query(self, query: str) -> bool:
        """Check if query is in English"""
        english_indicators = ['the', 'and', 'for', 'with', 'of', 'to', 'in', 'on', 'at']
        query_lower = query.lower()
        words = query_lower.split()
        
        if words:
            english_count = sum(1 for w in words if w in english_indicators)
            return english_count / len(words) > 0.2
        
        return False
    
    def _search_tenders(self, query: str) -> str:
        """Search for tenders with translation and filtering"""
        try:
            if self._is_english_query(query):
                french_query = self._translate_to_french(query)
            else:
                french_query = query
            
            results = self.openrag.search(
                query=french_query,
                top_k=30,
                partition_name='tenders',
                similarity_threshold=0.3
            )
            
            if not results or 'documents' not in results or not results['documents']:
                results = self.openrag.search(
                    query=query,
                    top_k=30,
                    partition_name='tenders',
                    similarity_threshold=0.3
                )
            
            if not results or 'documents' not in results:
                return "No tenders found. Try a different search term."
            
            docs = results['documents']
            
            tender_list = []
            for doc in docs:
                metadata = doc.get('metadata', {})
                content = doc.get('content', '')
                
                title = metadata.get('title', '')
                if not title:
                    title_match = re.search(r'Title:\s*([^\n]+)', content)
                    if title_match:
                        title = title_match.group(1).strip()
                
                reference = metadata.get('reference', '')
                if not reference:
                    ref_match = re.search(r'Reference:\s*([^\n]+)', content)
                    if ref_match:
                        reference = ref_match.group(1).strip()
                
                buyer = metadata.get('buyer', '')
                if not buyer:
                    buyer_match = re.search(r'Buyer:\s*([^\n]+)', content)
                    if buyer_match:
                        buyer = buyer_match.group(1).strip()
                
                deadline = metadata.get('deadline', '')
                if not deadline:
                    deadline_match = re.search(r'Deadline:\s*([^\n]+)', content)
                    if deadline_match:
                        deadline = deadline_match.group(1).strip()
                
                if title and title != 'Untitled':
                    tender_list.append({
                        'title': title,
                        'reference': reference or 'N/A',
                        'buyer': buyer or 'Unknown',
                        'deadline': deadline or 'N/A'
                    })
            
            if not tender_list:
                return "No tenders found. Try a different search term."
            
            result_text = f"🎯 Found {len(tender_list)} relevant tenders for '{query}':\n\n"
            for i, tender in enumerate(tender_list[:10], 1):
                result_text += f"{i}. 📋 {tender['title']}\n"
                result_text += f"   Reference: {tender['reference']}\n"
                result_text += f"   Buyer: {tender['buyer']}\n"
                result_text += f"   Deadline: {tender['deadline']}\n\n"
            
            return result_text
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return f"Error searching: {str(e)}"
    
    def search_tenders(self, query: str, top_k: int = 10) -> Dict[str, Any]:
        """Public search method - ALWAYS search in French with proper phrasing"""
        try:
            # ALWAYS translate to French using common tender phrasing
            french_query = self._translate_to_french(query)
            
            # Search OpenRAG with French query
            results = self.openrag.search(
                query=french_query,
                top_k=30,
                partition_name='tenders',
                similarity_threshold=0.3
            )
            
            # If no results, try the original query as fallback
            if not results or 'documents' not in results:
                results = self.openrag.search(
                    query=query,
                    top_k=30,
                    partition_name='tenders',
                    similarity_threshold=0.3
                )
            
            if not results or 'documents' not in results:
                return {
                    'success': True,
                    'total_found': 0,
                    'documents': [],
                    'query': query
                }
            
            docs = results.get('documents', [])
            
            # Extract tender info
            tender_list = []
            for doc in docs:
                metadata = doc.get('metadata', {})
                content = doc.get('content', '')
                
                title = metadata.get('title', '')
                if not title:
                    title_match = re.search(r'Title:\s*([^\n]+)', content)
                    if title_match:
                        title = title_match.group(1).strip()
                
                reference = metadata.get('reference', '')
                if not reference:
                    ref_match = re.search(r'Reference:\s*([^\n]+)', content)
                    if ref_match:
                        reference = ref_match.group(1).strip()
                
                buyer = metadata.get('buyer', '')
                if not buyer:
                    buyer_match = re.search(r'Buyer:\s*([^\n]+)', content)
                    if buyer_match:
                        buyer = buyer_match.group(1).strip()
                
                deadline = metadata.get('deadline', '')
                if not deadline:
                    deadline_match = re.search(r'Deadline:\s*([^\n]+)', content)
                    if deadline_match:
                        deadline = deadline_match.group(1).strip()
                
                if title and title != 'Untitled':
                    tender_list.append({
                        'title': title,
                        'reference': reference or 'N/A',
                        'buyer': buyer or 'Unknown',
                        'deadline': deadline or 'N/A',
                        'content': content[:300]
                    })
            
            if not tender_list:
                return {
                    'success': True,
                    'total_found': 0,
                    'documents': [],
                    'query': query
                }
            
            # Let LLM filter
            filter_prompt = f"""
            User Query: "{query}"
            French Query (Tunisian tender phrasing): "{french_query}"
            
            Here are {len(tender_list)} tenders found.
            
            Your task: Review each tender and determine if it is RELEVANT to what the user is looking for.
            
            Think about:
            1. What is the user really looking for?
            2. Does this tender match that intent?
            3. Is this clearly relevant?
            
            If the query is about roads, only include tenders about roads/highways/maintenance.
            Exclude schools, hospitals, agriculture, buildings, etc.
            
            Return ONLY a JSON array of the relevant tender numbers.
            Example: [0, 2, 5]
            
            Here are the tenders:
            """
            
            for i, tender in enumerate(tender_list):
                filter_prompt += f"""
                {i}. Title: {tender['title']}
                   Buyer: {tender['buyer']}
                   Deadline: {tender['deadline']}
                   Description: {tender['content'][:200]}
                """
            
            filter_prompt += """
            
            Return ONLY a JSON array of relevant numbers. If none, return: []
            """
            
            try:
                response = self.llm.invoke(filter_prompt)
                content = response.content.strip()
                
                match = re.search(r'\[([^\]]*)\]', content)
                if match:
                    indices = json.loads(f'[{match.group(1)}]')
                    filtered_tenders = [tender_list[i] for i in indices if 0 <= i < len(tender_list)]
                else:
                    try:
                        data = json.loads(content)
                        if isinstance(data, list):
                            filtered_tenders = [tender_list[i] for i in data if 0 <= i < len(tender_list)]
                        else:
                            filtered_tenders = tender_list[:top_k]
                    except:
                        filtered_tenders = tender_list[:top_k]
            except Exception as e:
                logger.error(f"Filter error: {e}")
                filtered_tenders = tender_list[:top_k]
            
            # Format results
            formatted_docs = []
            for tender in filtered_tenders[:top_k]:
                formatted_docs.append({
                    'metadata': {
                        'title': tender['title'],
                        'reference': tender['reference'],
                        'buyer': tender['buyer'],
                        'deadline': tender['deadline']
                    },
                    'content': tender.get('content', '')
                })
            
            return {
                'success': True,
                'total_found': len(formatted_docs),
                'documents': formatted_docs,
                'query': query,
                'french_query': french_query
            }
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return {
                'success': False,
                'error': str(e),
                'total_found': 0,
                'documents': []
            }
    
    def chat(self, message: str) -> Dict[str, Any]:
        """Main chat method"""
        try:
            response = self.agent.invoke(
                {"messages": [HumanMessage(content=message)]}
            )
            
            if isinstance(response, dict) and 'messages' in response:
                last_message = response['messages'][-1]
                output = last_message.content if hasattr(last_message, 'content') else str(last_message)
            else:
                output = str(response)
            
            return {
                'success': True,
                'response': output,
                'type': 'agent_response'
            }
            
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return {
                'success': False,
                'error': str(e),
                'response': f"Error: {str(e)}"
            }







        # def search_tenders(self, query: str, top_k: int = 10) -> Dict[str, Any]:
            #     """Public search method with strict filtering"""
            #     try:
            #         if self._is_english_query(query):
            #             french_query = self._translate_to_french(query)
            #         else:
            #             french_query = query
                    
            #         results = self.openrag.search(
            #             query=french_query,
            #             top_k=50,
            #             partition_name='tenders',
            #             similarity_threshold=0.3
            #         )
                    
            #         if not results or 'documents' not in results:
            #             return {
            #                 'success': True,
            #                 'total_found': 0,
            #                 'documents': [],
            #                 'query': query
            #             }
                    
            #         docs = results.get('documents', [])
                    
            #         query_lower = query.lower()
            #         road_keywords = ['route', 'road', 'routes', 'roads', 'highway', 'autoroute', 'pavement', 'asphalt']
            #         school_keywords = ['école', 'school', 'lycée', 'college', 'université', 'education', 'classe', 'prescolaire', 'maternelle']
            #         hospital_keywords = ['hôpital', 'hospital', 'clinique', 'medical', 'santé']
                    
            #         is_road_query = any(kw in query_lower for kw in road_keywords)
            #         is_school_query = any(kw in query_lower for kw in school_keywords)
            #         is_hospital_query = any(kw in query_lower for kw in hospital_keywords)
                    
            #         filtered_docs = []
            #         seen_refs = set()
                    
            #         for doc in docs:
            #             metadata = doc.get('metadata', {})
            #             content = doc.get('content', '')
                        
            #             reference = metadata.get('reference', '')
            #             if not reference:
            #                 ref_match = re.search(r'Reference:\s*([^\n]+)', content)
            #                 if ref_match:
            #                     reference = ref_match.group(1).strip()
                        
            #             if reference in seen_refs:
            #                 continue
            #             seen_refs.add(reference)
                        
            #             title = metadata.get('title', '')
            #             if not title:
            #                 title_match = re.search(r'Title:\s*([^\n]+)', content)
            #                 if title_match:
            #                     title = title_match.group(1).strip()
                        
            #             title_lower = title.lower()
            #             is_relevant = False
                        
            #             if is_road_query:
            #                 is_relevant = any(kw in title_lower for kw in ['route', 'road', 'chaussée', 'pavement', 'asphalt', 'entretien routier', 'réseau routier'])
            #             elif is_school_query:
            #                 is_relevant = any(kw in title_lower for kw in ['école', 'school', 'lycée', 'collège', 'université', 'classe', 'prescolaire', 'maternelle', 'éducation'])
            #             elif is_hospital_query:
            #                 is_relevant = any(kw in title_lower for kw in ['hôpital', 'hospital', 'clinique', 'medical', 'santé'])
            #             else:
            #                 is_relevant = True
                        
            #             if not is_relevant:
            #                 continue
                        
            #             buyer = metadata.get('buyer', '')
            #             if not buyer:
            #                 buyer_match = re.search(r'Buyer:\s*([^\n]+)', content)
            #                 if buyer_match:
            #                     buyer = buyer_match.group(1).strip()
                        
            #             deadline = metadata.get('deadline', '')
            #             if not deadline:
            #                 deadline_match = re.search(r'Deadline:\s*([^\n]+)', content)
            #                 if deadline_match:
            #                     deadline = deadline_match.group(1).strip()
                        
            #             filtered_docs.append({
            #                 'metadata': {
            #                     'title': title or 'Untitled',
            #                     'reference': reference or 'N/A',
            #                     'buyer': buyer or 'Unknown',
            #                     'deadline': deadline or 'N/A',
            #                     'relevance_type': 'school' if is_school_query else 'road' if is_road_query else 'general'
            #                 },
            #                 'content': content
            #             })
                        
            #             if len(filtered_docs) >= top_k:
            #                 break
                    
            #         return {
            #             'success': True,
            #             'total_found': len(filtered_docs),
            #             'documents': filtered_docs,
            #             'query': query,
            #             'french_query': french_query,
            #             'query_type': 'school' if is_school_query else 'road' if is_road_query else 'general'
            #         }
                    
            #     except Exception as e:
            #         logger.error(f"Search error: {e}")
            #         return {
            #             'success': False,
            #             'error': str(e),
            #             'total_found': 0,
            #             'documents': []
            #         }