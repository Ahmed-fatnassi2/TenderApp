# # routes/agent_routes.py

# from flask import Blueprint, request, jsonify
# from services.agent_service import TenderAgent

# import logging
# import os

# logger = logging.getLogger(__name__)
# agent_bp = Blueprint('agent', __name__, url_prefix='/api/agent')

# # Initialize agent (singleton)
# _agent_instance = None

# def get_agent():
#     """Get or create agent instance"""
#     global _agent_instance
#     if _agent_instance is None:
#         openai_api_key = os.getenv('OPENAI_API_KEY')
#         if not openai_api_key:
#             raise ValueError("OPENAI_API_KEY environment variable is required")
#         _agent_instance = TenderAgent(openai_api_key)
#     return _agent_instance

# @agent_bp.route('/chat', methods=['POST'])
# def chat():
#     """Chat with the tender agent"""
#     try:
#         data = request.get_json()
#         message = data.get('message')
#         thread_id = data.get('thread_id', 'default')
        
#         if not message:
#             return jsonify({"success": False, "error": "Message required"}), 400
        
#         agent = get_agent()
#         response = agent.chat(message, thread_id)
        
#         return jsonify({
#             "success": True,
#             "response": response,
#             "thread_id": thread_id
#         })
        
#     except Exception as e:
#         logger.error(f"Chat error: {e}")
#         return jsonify({"success": False, "error": str(e)}), 500

# @agent_bp.route('/search', methods=['POST'])
# def search():
#     """Simple semantic search via agent"""
#     try:
#         data = request.get_json()
#         query = data.get('query')
        
#         if not query:
#             return jsonify({"success": False, "error": "Query required"}), 400
        
#         agent = get_agent()
#         results = agent.search_tenders(query)
        
#         return jsonify({
#             "success": True,
#             "query": query,
#             "count": len(results),
#             "results": results
#         })
        
#     except Exception as e:
#         logger.error(f"Search error: {e}")
#         return jsonify({"success": False, "error": str(e)}), 500

# @agent_bp.route('/analyze', methods=['POST'])
# def analyze():
#     """Analyze a tender using the agent"""
#     try:
#         data = request.get_json()
#         tender_id = data.get('tender_id')
#         query = data.get('query')
        
#         if not tender_id and not query:
#             return jsonify({"success": False, "error": "tender_id or query required"}), 400
        
#         agent = get_agent()
        
#         if tender_id:
#             # Analyze specific tender
#             from models import Tender
#             tender = Tender.query.filter(Tender.reference == tender_id).first()
#             if not tender:
#                 return jsonify({"success": False, "error": "Tender not found"}), 404
            
#             analysis = agent._analyze_tender_tool(tender_id)
#         else:
#             # Search and analyze
#             results = agent.search_tenders(query)
#             if not results:
#                 return jsonify({"success": False, "error": "No tenders found"}), 404
            
#             # Analyze first result
#             tender = results[0]
#             analysis = agent._analyze_tender_tool(tender['reference'])
        
#         return jsonify({
#             "success": True,
#             "analysis": analysis
#         })
        
#     except Exception as e:
#         logger.error(f"Analysis error: {e}")
#         return jsonify({"success": False, "error": str(e)}), 500



# ///////////////////////////////////////////////////////////////////////////////////////////////////////

# from flask import Blueprint, request, jsonify
# from services.agent_service import TenderAgent

# import logging
# import os


# logger = logging.getLogger(__name__)

# agent_bp = Blueprint(
#     "agent",
#     __name__,
#     url_prefix="/api/agent"
# )


# # ================================================================
# # Singleton Agent
# # ================================================================

# _agent_instance = None


# def get_agent() -> TenderAgent:

#     global _agent_instance

#     if _agent_instance is None:

#         openai_api_key = os.getenv(
#             "OPENAI_API_KEY"
#         )

#         if not openai_api_key:

#             raise ValueError(
#                 "OPENAI_API_KEY environment variable is required"
#             )

#         _agent_instance = TenderAgent(
#             openai_api_key
#         )

#     return _agent_instance


# # ================================================================
# # CHAT
# # ================================================================

# @agent_bp.route("/chat", methods=["POST"])
# def chat():

#     try:

#         data = request.get_json(
#             silent=True
#         ) or {}

#         message = data.get(
#             "message",
#             ""
#         ).strip()

#         thread_id = data.get(
#             "thread_id",
#             "default"
#         )

#         if not message:

#             return jsonify({
#                 "success": False,
#                 "error": "Message required"
#             }), 400

#         agent = get_agent()

#         response = agent.chat(
#             message=message,
#             thread_id=thread_id,
#             filter_it=True
#         )

#         return jsonify({
#             "success": True,
#             "response": response,
#             "thread_id": thread_id
#         })

#     except Exception as e:

#         logger.exception(
#             f"Chat error: {e}"
#         )

#         return jsonify({
#             "success": False,
#             "error": str(e)
#         }), 500


# # ================================================================
# # SEARCH
# # ================================================================

# @agent_bp.route("/search", methods=["POST"])
# def search():

#     try:

#         data = request.get_json(
#             silent=True
#         ) or {}

#         query = data.get(
#             "query",
#             ""
#         ).strip()

#         if not query:

#             return jsonify({
#                 "success": False,
#                 "error": "Query required"
#             }), 400

#         agent = get_agent()

#         results = agent.search_tenders(
#             query=query,
#             filter_it_only=True
#         )

#         return jsonify({
#             "success": True,
#             "query": query,
#             "count": len(results),
#             "results": results
#         })

#     except Exception as e:

#         logger.exception(
#             f"Search error: {e}"
#         )

#         return jsonify({
#             "success": False,
#             "error": str(e)
#         }), 500


# # ================================================================
# # ANALYZE
# # ================================================================

# @agent_bp.route("/analyze", methods=["POST"])
# def analyze():

#     try:

#         data = request.get_json(
#             silent=True
#         ) or {}

#         tender_id = data.get(
#             "tender_id"
#         )

#         query = data.get(
#             "query"
#         )

#         if not tender_id and not query:

#             return jsonify({
#                 "success": False,
#                 "error": (
#                     "tender_id or query required"
#                 )
#             }), 400

#         agent = get_agent()

#         # --------------------------------------------------------
#         # Specific tender
#         # --------------------------------------------------------

#         if tender_id:

#             analysis = agent.analyze_tender(
#                 tender_id
#             )

#             if analysis is None:

#                 return jsonify({
#                     "success": False,
#                     "error": "Tender not found"
#                 }), 404

#         # --------------------------------------------------------
#         # Search first
#         # --------------------------------------------------------

#         else:

#             results = agent.search_tenders(
#                 query=query,
#                 filter_it_only=True
#             )

#             if not results:

#                 return jsonify({
#                     "success": False,
#                     "error": "No tenders found"
#                 }), 404

#             first_tender = results[0]

#             analysis = agent.analyze_tender(
#                 first_tender["reference"]
#             )

#         return jsonify({
#             "success": True,
#             "analysis": analysis
#         })

#     except Exception as e:

#         logger.exception(
#             f"Analysis error: {e}"
#         )

#         return jsonify({
#             "success": False,
#             "error": str(e)
#         }), 500








from flask import Blueprint, request, jsonify

from services.agent_service import TenderAgent

import logging
import os


logger = logging.getLogger(__name__)

agent_bp = Blueprint(
    "agent",
    __name__,
    url_prefix="/api/agent"
)


# ================================================================
# Singleton Agent
# ================================================================

_agent_instance = None


def get_agent() -> TenderAgent:

    global _agent_instance

    if _agent_instance is None:

        openai_api_key = os.getenv(
            "OPENAI_API_KEY"
        )

        if not openai_api_key:

            raise ValueError(
                "OPENAI_API_KEY environment variable "
                "is required"
            )

        _agent_instance = TenderAgent(
            openai_api_key
        )

    return _agent_instance


# ================================================================
# CHAT
# ================================================================

@agent_bp.route(
    "/chat",
    methods=["POST"]
)
def chat():

    try:

        data = (
            request.get_json(
                silent=True
            )
            or {}
        )

        message = str(
            data.get(
                "message",
                ""
            )
        ).strip()

        thread_id = data.get(
            "thread_id",
            "default"
        )

        if not message:

            return jsonify({
                "success": False,
                "error": "Message required"
            }), 400

        agent = get_agent()

        response = agent.chat(
            message=message,
            thread_id=thread_id
        )

        return jsonify({
            "success": True,
            "response": response,
            "thread_id": thread_id
        })

    except Exception as e:

        logger.exception(
            f"Chat error: {e}"
        )

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ================================================================
# SEARCH
# ================================================================


@agent_bp.route('/search', methods=['POST'])
def search():
    """Search tenders using the AI tender agent."""

    try:
        data = request.get_json(silent=True) or {}

        query = str(
            data.get('query', '')
        ).strip()

        category = data.get('category')

        status = data.get(
            'status',
            'active'
        )

        if not query:
            return jsonify({
                "success": False,
                "error": "Query required"
            }), 400

        agent = get_agent()

        results = agent.search_tenders(
            query=query,
            category=category,
            status=status
        )

        return jsonify({
            "success": True,
            "query": query,
            "category": category,
            "status": status,
            "count": len(results),
            "results": results
        })

    except Exception as e:

        logger.exception(
            f"Search error: {e}"
        )

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500




# ================================================================
# ANALYZE
# ================================================================

@agent_bp.route(
    "/analyze",
    methods=["POST"]
)
def analyze():

    try:

        data = (
            request.get_json(
                silent=True
            )
            or {}
        )

        tender_id = data.get(
            "tender_id"
        )

        query = data.get(
            "query"
        )

        if not tender_id and not query:

            return jsonify({
                "success": False,
                "error": (
                    "tender_id or query required"
                )
            }), 400

        agent = get_agent()

        # --------------------------------------------------------
        # Specific tender
        # --------------------------------------------------------

        if tender_id:

            analysis = agent.analyze_tender(
                tender_id
            )

            if analysis is None:

                return jsonify({
                    "success": False,
                    "error": "Tender not found"
                }), 404

        # --------------------------------------------------------
        # Search then analyze
        # --------------------------------------------------------

        else:

            results = agent.search_tenders(
                query=query,
                status="active"
            )

            if not results:

                return jsonify({
                    "success": False,
                    "error": "No tenders found"
                }), 404

            first_tender = results[0]

            analysis = agent.analyze_tender(
                first_tender["reference"]
            )

            if analysis is None:

                return jsonify({
                    "success": False,
                    "error": "Tender not found"
                }), 404

        return jsonify({
            "success": True,
            "analysis": analysis
        })

    except Exception as e:

        logger.exception(
            f"Analysis error: {e}"
        )

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500