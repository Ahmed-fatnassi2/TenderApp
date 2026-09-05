# services/agent_service.py

import os
import re
import json
import logging
import unicodedata
import time

from concurrent.futures import ThreadPoolExecutor, as_completed

from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

from openai import OpenAI

from services.openrag_client import OpenRAGClient


logger = logging.getLogger(__name__)


class TenderAgent:
    """
    AI-powered Tunisian tender search agent.

    Retrieval strategy
    ------------------

    Instead of relying on a single top-K OpenRAG query, we use
    multiple semantic queries.

    Example:

        "software development"

    becomes:

        1. software development
        2. développement logiciel
        3. développement application
        4. conception développement système informatique
        5. application informatique

    Each query retrieves up to RETRIEVAL_TOP_K documents.

    Results are then:

        retrieve
          ↓
        merge
          ↓
        deduplicate
          ↓
        local pre-ranking
          ↓
        OpenAI classification
          ↓
        status filtering
          ↓
        category filtering
          ↓
        final ranking

    This improves recall while avoiding sending hundreds of
    documents directly to OpenAI.
    """

    # ============================================================
    # CONFIGURATION
    # ============================================================

    # Number of documents retrieved for EACH OpenRAG query.
    #
    # 50 is deliberately used here.
    #
    # If we have 5 retrieval queries, we can potentially obtain
    # up to 250 candidates before deduplication.
    RETRIEVAL_TOP_K = 50

    # Maximum number of candidates sent to OpenAI.
    # 75 gives a good balance between recall and latency.
    # We retrieve more than this, then locally pre-rank them.
    OPENAI_CLASSIFICATION_LIMIT = 60

    # Minimum OpenRAG similarity.
    SIMILARITY_THRESHOLD = 0.20

    # Number of semantic query variants.
    MAX_QUERY_VARIANTS = 6

    # Maximum number of final results.
    MAX_FINAL_RESULTS = 20

    # Maximum number of OpenRAG searches executed concurrently.
    MAX_RETRIEVAL_WORKERS = 6

    # Keep prompts small to reduce OpenAI latency.
    OPENAI_CONTENT_LIMIT = 900

    # Short TTL prevents active/expired results from becoming stale.
    SEARCH_CACHE_TTL_SECONDS = 180

    # ============================================================
    # CATEGORIES
    # ============================================================

    ALLOWED_CATEGORIES = {
        "software_development",
        "software_acquisition",
        "hardware",
        "networking",
        "cybersecurity",
        "cloud",
        "ai_ml",
        "database",
        "it_services",
        "telecommunications",
        "other",
    }

    # ============================================================
    # INITIALIZATION
    # ============================================================

    def __init__(
        self,
        openai_api_key: Optional[str] = None
    ):

        self.openai_api_key = (
            openai_api_key
            or os.getenv("OPENAI_API_KEY")
        )

        if not self.openai_api_key:

            raise ValueError(
                "OPENAI_API_KEY environment variable is required"
            )

        self.client = OpenAI(
            api_key=self.openai_api_key
        )

        self.openrag = OpenRAGClient()

        # cache_key -> (created_at_monotonic, results)
        self.search_cache = {}

        logger.info(
            "🤖 TenderAgent initialized successfully"
        )

    # ============================================================
    # MAIN SEARCH
    # ============================================================
    # services/agent_service.py - Ajouter cette méthode

    def _enrich_with_source_url(self, results: List[Dict]) -> List[Dict]:
        """Ajouter source_url à chaque résultat"""
        from models.tender import Tender
    
        enriched = []
        for result in results:
            reference = result.get('reference')
            if reference:
                tender = Tender.query.filter_by(reference=reference).first()
                result['source_url'] = tender.source_url if tender else None
            else:
                result['source_url'] = None
            enriched.append(result)
    
        return enriched
    def search_tenders(
        self,
        query: str,
        category: Optional[str] = None,
        status: str = "active"
    ) -> List[Dict[str, Any]]:

        start_time = time.perf_counter()

        try:

            # ====================================================
            # VALIDATION
            # ====================================================

            if not query or not query.strip():

                return []

            query = query.strip()

            status = (
                str(status)
                .lower()
                .strip()
            )

            if status not in {
                "active",
                "expired",
                "all"
            }:

                status = "active"

            if category:

                category = (
                    str(category)
                    .lower()
                    .strip()
                )

                if category not in (
                    self.ALLOWED_CATEGORIES
                ):

                    logger.warning(
                        f"Unknown category '{category}'"
                    )

                    category = None

            # ====================================================
            # QUERY INTENT / STRICT CATEGORY DETECTION
            # ====================================================

            query_category = (
                category
                or self._detect_query_category(query)
            )

            logger.info(
                f"Detected query category: {query_category}"
            )

            # ====================================================
            # LOGGING
            # ====================================================

            logger.info("=" * 70)
            logger.info("🔍 TENDER SEARCH")
            logger.info(f"Original query: {query}")
            logger.info(f"Category filter: {category}")
            logger.info(f"Status filter: {status}")

            # ====================================================
            # CACHE
            # ====================================================

            cache_key = (
                f"{self._normalize_text(query)}|"
                f"{category}|"
                f"{query_category}|"
                f"{status}"
            )

            cached = self.search_cache.get(cache_key)
            if cached:
                cached_at, cached_results = cached
                age = time.monotonic() - cached_at
                if age < self.SEARCH_CACHE_TTL_SECONDS:
                    logger.info(
                        f"⚡ Returning cached results ({age:.1f}s old)"
                    )
                    return cached_results
                self.search_cache.pop(cache_key, None)

            # ====================================================
            # BUILD MULTIPLE RETRIEVAL QUERIES
            # ====================================================

            retrieval_queries = (
                self._build_retrieval_queries(
                    query
                )
            )

            logger.info(
                f"🔎 Retrieval queries: "
                f"{len(retrieval_queries)}"
            )

            for index, rq in enumerate(
                retrieval_queries,
                1
            ):

                logger.info(
                    f"   {index}. {rq}"
                )

            # ====================================================
            # PARALLEL MULTI-QUERY OPENRAG RETRIEVAL
            # ====================================================

            retrieval_start = time.perf_counter()
            all_documents = []

            with ThreadPoolExecutor(
                max_workers=min(
                    self.MAX_RETRIEVAL_WORKERS,
                    len(retrieval_queries)
                )
            ) as executor:

                future_to_query = {
                    executor.submit(
                        self._retrieve_from_openrag,
                        retrieval_query
                    ): retrieval_query
                    for retrieval_query in retrieval_queries
                }

                for future in as_completed(
                    future_to_query
                ):
                    retrieval_query = future_to_query[future]

                    try:
                        documents = future.result()

                        logger.info(
                            f"📚 '{retrieval_query}' "
                            f"→ {len(documents)} documents"
                        )

                        all_documents.extend(documents)

                    except Exception as e:
                        logger.exception(
                            f"❌ OpenRAG query failed: "
                            f"{retrieval_query} | {e}"
                        )

            logger.info(
                f"⚡ Parallel retrieval completed in "
                f"{time.perf_counter() - retrieval_start:.2f}s"
            )

            logger.info(
                f"📚 Total raw retrieved documents: "
                f"{len(all_documents)}"
            )

            if not all_documents:

                logger.warning(
                    "⚠️ No documents retrieved"
                )

                return []

            # ====================================================
            # EXTRACT TENDERS
            # ====================================================

            tenders = self._extract_tenders(
                all_documents
            )

            logger.info(
                f"📋 Extracted tenders before "
                f"deduplication: {len(tenders)}"
            )

            # ====================================================
            # DEDUPLICATE
            # ====================================================

            tenders = self._deduplicate_tenders(
                tenders
            )

            logger.info(
                f"📋 Unique tenders after "
                f"deduplication: {len(tenders)}"
            )

            if not tenders:

                return []

            # ====================================================
            # LOCAL PRE-RANKING
            # ====================================================

            for tender in tenders:

                (
                    is_it,
                    matches,
                    confidence,
                    it_score
                ) = self._classify_it_locally(
                    tender["title"],
                    tender["content"]
                )

                tender["is_it"] = is_it
                tender["it_matches"] = matches
                tender["it_confidence"] = confidence
                tender["it_score"] = it_score

                # Local relevance score against the query.
                tender[
                    "query_match_score"
                ] = self._calculate_query_match_score(
                    query,
                    tender
                )

            # ====================================================
            # STRICT CATEGORY PREFILTER
            # ====================================================

            if query_category in self.STRICT_QUERY_CATEGORIES:
                before_count = len(tenders)
                tenders = [
                    tender
                    for tender in tenders
                    if self._has_category_evidence(
                        query_category,
                        tender
                    )
                ]
                logger.info(
                    f"🧹 Strict category prefilter "
                    f"({query_category}): "
                    f"{before_count} -> {len(tenders)}"
                )

            if not tenders:
                logger.info("No candidates remain after strict category prefilter")
                return []

            # ====================================================
            # PRE-RANK BEFORE OPENAI
            # ====================================================

            tenders.sort(
                key=lambda x: (
                    -x.get(
                        "query_match_score",
                        0
                    ),

                    -x.get(
                        "it_score",
                        0
                    ),

                    -x.get(
                        "retrieval_score",
                        0
                    )
                )
            )

            logger.info(
                f"📊 Candidates after local "
                f"pre-ranking: {len(tenders)}"
            )

            # ====================================================
            # IMPORTANT:
            #
            # We DO NOT classify every retrieved document with
            # OpenAI.
            #
            # We retrieve broadly, then classify the strongest
            # candidates.
            # ====================================================

            openai_candidates = tenders[
                :self.OPENAI_CLASSIFICATION_LIMIT
            ]

            logger.info(
                f"🧠 OpenAI classification for "
                f"{len(openai_candidates)} "
                f"of {len(tenders)} candidates"
            )

            # ====================================================
            # OPENAI CLASSIFICATION
            # ====================================================

            ai_results = (
                self._openai_classify_tenders(
                    tenders=openai_candidates,
                    query=query,
                    query_category=query_category
                )
            )

            # ====================================================
            # ATTACH AI RESULTS
            # ====================================================

            for tender in tenders:

                reference = tender[
                    "reference"
                ]

                ai_data = ai_results.get(
                    reference
                )

                if ai_data:

                    tender[
                        "ai_relevant"
                    ] = ai_data.get(
                        "relevant",
                        False
                    )

                    tender[
                        "ai_score"
                    ] = ai_data.get(
                        "score",
                        0
                    )

                    tender[
                        "category"
                    ] = ai_data.get(
                        "category",
                        "other"
                    )

                    tender[
                        "match_type"
                    ] = ai_data.get(
                        "match_type",
                        "unknown"
                    )

                    tender[
                        "relevance_reason"
                    ] = ai_data.get(
                        "reason",
                        ""
                    )

                else:

                    tender[
                        "ai_relevant"
                    ] = False

                    tender[
                        "ai_score"
                    ] = 0

                    tender[
                        "category"
                    ] = "other"

                    tender[
                        "match_type"
                    ] = "unknown"

                    tender[
                        "relevance_reason"
                    ] = ""

            # ====================================================
            # AI RELEVANCE
            # ====================================================

            ai_relevant = [

                tender

                for tender in tenders

                if tender.get(
                    "ai_relevant"
                ) is True

            ]

            logger.info(
                f"🧠 OpenAI found "
                f"{len(ai_relevant)} relevant "
                f"tenders"
            )

            # ====================================================
            # HARD RELEVANCE RULES
            # ====================================================

            filtered_relevant = []

            for tender in ai_relevant:

                if self._passes_query_relevance_rules(
                    query,
                    tender,
                    query_category=query_category
                ):

                    filtered_relevant.append(
                        tender
                    )

                else:

                    logger.info(
                        f"🚫 Removed by relevance "
                        f"rule: "
                        f"{tender['reference']} | "
                        f"{tender.get('match_type')} | "
                        f"{tender.get('category')}"
                    )

            logger.info(
                f"🎯 After relevance rules: "
                f"{len(filtered_relevant)}"
            )

            # ====================================================
            # STATUS FILTER
            # ====================================================

            status_filtered = []

            for tender in filtered_relevant:

                tender_status = tender.get(
                    "status",
                    "unknown"
                )

                if status == "all":

                    status_filtered.append(
                        tender
                    )

                elif status == "active":

                    if tender_status in {"active", "unknown"}:

                        status_filtered.append(
                            tender
                        )

                elif status == "expired":

                    if tender_status == "expired":

                        status_filtered.append(
                            tender
                        )

            logger.info(
                f"📅 After status filter: "
                f"{len(status_filtered)}"
            )

            # ====================================================
            # CATEGORY FILTER
            # ====================================================

            if category:

                status_filtered = [

                    tender

                    for tender in status_filtered

                    if tender.get(
                        "category"
                    ) == category

                ]

                logger.info(
                    f"🏷️ After category filter: "
                    f"{len(status_filtered)}"
                )

            # ====================================================
            # FINAL SCORE
            # ====================================================

            for tender in status_filtered:

                tender[
                    "final_score"
                ] = self._calculate_final_score(
                    tender
                )

            # ====================================================
            # FINAL SORTING
            # ====================================================

            status_filtered.sort(
                key=lambda tender: (
                    -tender.get(
                        "final_score",
                        0
                    ),

                    -tender.get(
                        "ai_score",
                        0
                    ),

                    -tender.get(
                        "query_match_score",
                        0
                    ),

                    -tender.get(
                        "retrieval_score",
                        0
                    )
                )
            )

            # ====================================================
            # FINAL DEDUPLICATION
            # ====================================================

            final_results = (
                self._semantic_deduplicate_results(
                    status_filtered
                )
            )

            # ====================================================
            # LIMIT FINAL RESULTS
            # ====================================================

            final_results = final_results[
                :self.MAX_FINAL_RESULTS
            ]

            # ====================================================
            # CACHE
            # ====================================================

            self.search_cache[
                cache_key
            ] = (time.monotonic(), final_results)

            # ====================================================
            # FINAL LOGGING
            # ====================================================

            logger.info(
                f"✅ FINAL RESULTS: "
                f"{len(final_results)}"
            )

            for index, tender in enumerate(
                final_results,
                1
            ):

                logger.info(
                    f"#{index} | "
                    f"{tender.get('reference')} | "
                    f"{tender.get('category')} | "
                    f"match={tender.get('match_type')} | "
                    f"AI={tender.get('ai_score', 0):.2f} | "
                    f"final={tender.get('final_score', 0):.2f} | "
                    f"status={tender.get('status')}"
                )

            logger.info(
                f"🚀 TOTAL SEARCH TIME: "
                f"{time.perf_counter() - start_time:.2f}s"
            )

            logger.info("=" * 70)
            
            return self._enrich_with_source_url(final_results)

        except Exception as e:

            logger.exception(
                f"❌ Tender search failed: {e}"
            )

            return []

    # ============================================================
    # OPENRAG RETRIEVAL HELPER
    # ============================================================

    def _retrieve_from_openrag(
        self,
        retrieval_query: str
    ) -> List[Dict[str, Any]]:
        """Run one OpenRAG retrieval request."""

        try:
            rag_results = self.openrag.search(
                query=retrieval_query,
                top_k=self.RETRIEVAL_TOP_K,
                partition_name="tenders",
                similarity_threshold=self.SIMILARITY_THRESHOLD
            )

            if not rag_results:
                return []

            documents = rag_results.get(
                "documents",
                []
            )

            processed = []

            for doc in documents:
                if not isinstance(doc, dict):
                    continue

                item = dict(doc)
                item["_retrieval_query"] = retrieval_query
                processed.append(item)

            return processed

        except Exception as e:
            logger.exception(
                f"❌ OpenRAG retrieval failed for "
                f"'{retrieval_query}': {e}"
            )
            return []

    # ============================================================
    # RETRIEVAL QUERY GENERATION
    # ============================================================

    def _build_retrieval_queries(
        self,
        query: str
    ) -> List[str]:
        """
        Generate multiple retrieval queries.

        This is one of the most important changes.

        Instead of:

            top_k=50

        from one query, we do:

            query 1 → 50
            query 2 → 50
            query 3 → 50
            ...

        Then merge/deduplicate.

        This improves recall.
        """

        query_normalized = (
            self._normalize_text(query)
        )

        queries = []

        # --------------------------------------------------------
        # Original query
        # --------------------------------------------------------

        queries.append(
            query.strip()
        )

        # --------------------------------------------------------
        # Translation / synonym mapping
        # --------------------------------------------------------

        expansions = {

            "software development": [
                "développement logiciel",
                "développement application",
                "conception développement logiciel",
                "développement système informatique",
                "application informatique"
            ],

            "développement logiciel": [
                "software development",
                "développement application",
                "conception développement logiciel",
                "développement système informatique",
                "application informatique"
            ],

            "development": [
                "développement logiciel",
                "développement application",
                "software development",
                "application informatique"
            ],

            "développement": [
                "développement logiciel",
                "développement application",
                "software development",
                "application informatique"
            ],

            "web development": [
                "développement web",
                "application web",
                "création plateforme web",
                "développement logiciel web"
            ],

            "mobile development": [
                "développement mobile",
                "application mobile",
                "application Android",
                "application iOS"
            ],

            "cybersecurity": [
                "cybersécurité",
                "sécurité informatique",
                "sécurité des systèmes d'information",
                "information security"
            ],

            "security": [
                "sécurité informatique",
                "cybersécurité",
                "information security",
                "cybersecurity"
            ],

            "network": [
                "réseau informatique",
                "réseaux informatiques",
                "infrastructure réseau",
                "network infrastructure"
            ],

            "networks": [
                "réseau informatique",
                "réseaux informatiques",
                "infrastructure réseau",
                "network infrastructure"
            ],

            "cloud": [
                "cloud computing",
                "informatique cloud",
                "infrastructure cloud",
                "services cloud",
                "cloud computing services"
            ],

            "artificial intelligence": [
                "intelligence artificielle",
                "AI",
                "machine learning",
                "apprentissage automatique"
            ],

            "ai": [
                "intelligence artificielle",
                "artificial intelligence",
                "machine learning",
                "apprentissage automatique"
            ],

            "database": [
                "base de données",
                "bases de données",
                "database",
                "système de gestion de base de données"
            ],

            "erp": [
                "ERP",
                "progiciel de gestion",
                "système ERP",
                "Enterprise Resource Planning"
            ],
        }

        # --------------------------------------------------------
        # Exact expansion
        # --------------------------------------------------------

        if query_normalized in expansions:

            queries.extend(
                expansions[
                    query_normalized
                ]
            )

        else:

            # ----------------------------------------------------
            # Word-level expansion
            # ----------------------------------------------------

            for english, french_terms in (
                expansions.items()
            ):

                if english in query_normalized:

                    queries.extend(
                        french_terms
                    )

            # ----------------------------------------------------
            # Common IT query additions
            # ----------------------------------------------------

            if (
                "software" in query_normalized
                or "logiciel" in query_normalized
                or "developpement" in query_normalized
                or "développement" in query.lower()
            ):

                queries.extend([
                    "développement logiciel",
                    "développement application",
                    "application informatique",
                    "conception développement système"
                ])

        # --------------------------------------------------------
        # Clean / unique
        # --------------------------------------------------------

        result = []

        seen = set()

        for q in queries:

            q = str(
                q
            ).strip()

            if not q:
                continue

            key = self._normalize_text(
                q
            )

            if key in seen:
                continue

            seen.add(key)

            result.append(q)

        return result[
            :self.MAX_QUERY_VARIANTS
        ]

    # ============================================================
    # DOCUMENT EXTRACTION
    # ============================================================

    def _extract_tenders(
        self,
        documents: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        tenders = []

        for index, doc in enumerate(
            documents
        ):

            try:

                metadata = (
                    doc.get(
                        "metadata"
                    )
                    or {}
                )

                content = (
                    doc.get(
                        "content"
                    )
                    or ""
                )

                # ------------------------------------------------
                # Retrieval score
                # ------------------------------------------------

                retrieval_score = (
                    doc.get(
                        "score"
                    )
                    or doc.get(
                        "similarity"
                    )
                    or metadata.get(
                        "score"
                    )
                    or metadata.get(
                        "similarity"
                    )
                    or 0
                )

                try:

                    retrieval_score = float(
                        retrieval_score
                    )

                except (
                    TypeError,
                    ValueError
                ):

                    retrieval_score = 0

                # ------------------------------------------------
                # Metadata
                # ------------------------------------------------

                title = (
                    metadata.get(
                        "title"
                    )
                    or self._extract_field(
                        content,
                        "Title"
                    )
                    or "Untitled"
                )

                reference = (
                    metadata.get(
                        "reference"
                    )
                    or self._extract_field(
                        content,
                        "Reference"
                    )
                    or f"UNKNOWN-{index}"
                )

                buyer = (
                    metadata.get(
                        "buyer"
                    )
                    or self._extract_field(
                        content,
                        "Buyer"
                    )
                    or "Unknown"
                )

                deadline = (
                    metadata.get(
                        "deadline"
                    )
                    or self._extract_field(
                        content,
                        "Deadline"
                    )
                    or "N/A"
                )

                publication_date = (
                    metadata.get(
                        "publication_date"
                    )
                    or self._extract_field(
                        content,
                        "Publication Date"
                    )
                    or "N/A"
                )

                source = (
                    metadata.get(
                        "source"
                    )
                    or "OpenRAG"
                )

                # ------------------------------------------------
                # Status
                # ------------------------------------------------

                status = (
                    self._get_tender_status(
                        deadline
                    )
                )

                tenders.append({

                    "reference":
                        str(
                            reference
                        ).strip(),

                    "title":
                        str(
                            title
                        ).strip(),

                    "buyer":
                        str(
                            buyer
                        ).strip(),

                    "deadline":
                        str(
                            deadline
                        ).strip(),

                    "publication_date":
                        str(
                            publication_date
                        ).strip(),

                    "source":
                        str(
                            source
                        ).strip(),

                    "content":
                        str(
                            content
                        ).strip()[:3000],

                    "status":
                        status,

                    "retrieval_score":
                        retrieval_score,

                    "retrieval_queries":
                        [
                            doc.get(
                                "_retrieval_query"
                            )
                        ],

                    "is_it":
                        False,

                    "it_matches":
                        [],

                    "it_confidence":
                        "None",

                    "it_score":
                        0,

                    "query_match_score":
                        0,

                    "ai_relevant":
                        False,

                    "ai_score":
                        0,

                    "category":
                        "other",

                    "match_type":
                        "unknown",

                    "relevance_reason":
                        "",

                    "final_score":
                        0
                })

            except Exception as e:

                logger.warning(
                    f"Could not extract "
                    f"document {index}: {e}"
                )

        return tenders

    # ============================================================
    # FIELD EXTRACTION
    # ============================================================

    @staticmethod
    def _extract_field(
        content: str,
        field_name: str
    ) -> Optional[str]:

        if not content:
            return None

        pattern = (
            rf"{re.escape(field_name)}"
            rf"\s*:\s*([^\n]+)"
        )

        match = re.search(
            pattern,
            content,
            re.IGNORECASE
        )

        if not match:
            return None

        value = match.group(
            1
        ).strip()

        return value

    # ============================================================
    # DATE PARSING
    # ============================================================

    @staticmethod
    def _parse_datetime(
        value: str
    ) -> Optional[datetime]:

        if not value:
            return None

        value = str(
            value
        ).strip()

        if not value:
            return None

        if value.upper() in {
            "N/A",
            "NA",
            "NONE",
            "UNKNOWN"
        }:

            return None

        value = value.replace(
            "Z",
            ""
        )

        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d",
            "%d/%m/%Y %H:%M:%S",
            "%d/%m/%Y %H:%M",
            "%d/%m/%Y",
        ]

        try:

            dt = datetime.fromisoformat(
                value
            )

            return dt.replace(
                tzinfo=None
            )

        except ValueError:
            pass

        for fmt in formats:

            try:

                return datetime.strptime(
                    value,
                    fmt
                )

            except ValueError:
                continue

        return None

    # ============================================================
    # STATUS
    # ============================================================

    @classmethod
    def _get_tender_status(
        cls,
        deadline: str
    ) -> str:

        deadline_dt = (
            cls._parse_datetime(
                deadline
            )
        )

        if not deadline_dt:

            return "unknown"

        if deadline_dt >= datetime.now():

            return "active"

        return "expired"

    # ============================================================
    # NORMALIZE TEXT
    # ============================================================

    @staticmethod
    def _normalize_text(
        text: str
    ) -> str:

        if not text:
            return ""

        text = str(
            text
        ).lower()

        text = unicodedata.normalize(
            "NFKD",
            text
        )

        text = "".join(
            char
            for char in text
            if not unicodedata.combining(
                char
            )
        )

        text = re.sub(
            r"[^a-z0-9\s]",
            " ",
            text
        )

        text = re.sub(
            r"\s+",
            " ",
            text
        ).strip()

        return text

    # ============================================================
    # DEDUPLICATION
    # ============================================================

    def _deduplicate_tenders(
        self,
        tenders: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Deduplicate both repeated retrieval hits and cross-source mirrors.

        A reference is useful for exact duplicates, but HAICOP/TUNEPS can
        publish the same tender with different references.  Therefore a
        second identity is built from normalized title + buyer + deadline.
        Publication date is intentionally excluded because mirrors may have
        different publication timestamps.
        """
        unique_by_reference: Dict[str, Dict[str, Any]] = {}
        unique_cross_source: Dict[str, Dict[str, Any]] = {}

        for tender in tenders:
            reference = self._normalize_text(tender.get("reference", ""))
            title = self._normalize_text(tender.get("title", ""))
            buyer = self._normalize_text(tender.get("buyer", ""))
            deadline = self._normalize_deadline_key(tender.get("deadline", ""))

            if not title:
                title = self._normalize_text(tender.get("content", ""))[:180]

            ref_key = (
                reference
                if reference and not reference.startswith("unknown")
                else ""
            )
            cross_key = (
                f"cross:{title}|{buyer}|{deadline}"
                if title and buyer and deadline
                else ""
            )

            # Exact reference dedupe first.
            if ref_key:
                existing = unique_by_reference.get(ref_key)
                if existing is not None:
                    self._merge_duplicate_tender(existing, tender)
                    continue
                unique_by_reference[ref_key] = tender

            # Cross-source dedupe: same tender title/buyer/deadline.
            if cross_key:
                existing = unique_cross_source.get(cross_key)
                if existing is not None:
                    # If this mirror was already registered by its own reference,
                    # remove that object so only the canonical representative remains.
                    if ref_key:
                        unique_by_reference.pop(ref_key, None)
                    self._merge_duplicate_tender(existing, tender)
                    continue
                unique_cross_source[cross_key] = tender

        # Keep insertion order while removing objects that were merged into
        # an earlier cross-source representative.
        seen_ids = set()
        result = []
        for tender in unique_by_reference.values():
            ident = id(tender)
            if ident not in seen_ids:
                result.append(tender)
                seen_ids.add(ident)

        # Tenders without usable references were not put in unique_by_reference.
        for tender in unique_cross_source.values():
            ident = id(tender)
            if ident not in seen_ids:
                result.append(tender)
                seen_ids.add(ident)

        return result

    def _normalize_deadline_key(self, value: Any) -> str:
        """Normalize a deadline to a stable YYYY-MM-DD HH:MM key."""
        if not value:
            return ""
        raw = str(value).strip()
        parsed = self._parse_datetime(raw)
        if parsed is not None:
            return parsed.strftime("%Y-%m-%d %H:%M")
        return self._normalize_text(raw)

    def _merge_duplicate_tender(
        self,
        existing: Dict[str, Any],
        incoming: Dict[str, Any]
    ) -> None:
        """Merge mirror metadata and keep the strongest retrieval representative."""
        existing_queries = existing.get("retrieval_queries", []) or []
        incoming_queries = incoming.get("retrieval_queries", []) or []
        existing["retrieval_queries"] = list(dict.fromkeys(
            existing_queries + incoming_queries
        ))

        refs = existing.get("references", []) or [existing.get("reference", "")]
        incoming_refs = incoming.get("references", []) or [incoming.get("reference", "")]
        existing["references"] = list(dict.fromkeys(
            [str(x) for x in refs + incoming_refs if x]
        ))

        sources = existing.get("sources", []) or [existing.get("source", "")]
        incoming_sources = incoming.get("sources", []) or [incoming.get("source", "")]
        existing["sources"] = list(dict.fromkeys(
            [str(x) for x in sources + incoming_sources if x]
        ))

        existing_score = float(existing.get("retrieval_score", 0) or 0)
        incoming_score = float(incoming.get("retrieval_score", 0) or 0)
        if incoming_score > existing_score:
            # Preserve merged metadata before copying the stronger record.
            merged_refs = existing["references"]
            merged_sources = existing["sources"]
            merged_queries = existing["retrieval_queries"]
            existing.update(incoming)
            existing["references"] = merged_refs
            existing["sources"] = merged_sources
            existing["retrieval_queries"] = merged_queries

    # ============================================================
    # LOCAL IT CLASSIFIER
    # ============================================================

    def _classify_it_locally(
        self,
        title: str,
        content: str
    ) -> Tuple[
        bool,
        List[str],
        str,
        int
    ]:

        text = self._normalize_text(
            f"{title} {content}"
        )

        keywords = {

            "informatique": 4,
            "logiciel": 5,
            "software": 5,

            "developpement logiciel": 6,
            "developpement informatique": 6,

            "application web": 5,
            "application mobile": 5,
            "application informatique": 5,

            "systeme d information": 5,
            "systeme informatique": 5,

            "base de donnees": 5,
            "database": 5,

            "serveur": 4,
            "server": 4,

            "cloud": 5,

            "intelligence artificielle": 6,
            "artificial intelligence": 6,

            "machine learning": 6,

            "cybersecurite": 6,
            "cybersecurity": 6,

            "programmation": 5,
            "programming": 5,

            "devops": 5,

            "api": 4,

            "reseau informatique": 5,
            "reseaux informatiques": 5,

            "network infrastructure": 5,

            "firewall": 5,
            "pare feu": 5,
        }

        negative_keywords = {

            "construction": -3,
            "travaux publics": -3,
            "plomberie": -3,
            "beton": -3,
            "asphalte": -3,
            "canalisation": -3,
            "reseau electrique": -3,
            "reseau d eau": -3,
            "reseau routier": -3,
            "eclairage public": -3,
        }

        score = 0

        matches = []

        for keyword, weight in (
            keywords.items()
        ):

            if keyword in text:

                score += weight

                matches.append(
                    keyword
                )

        for keyword, weight in (
            negative_keywords.items()
        ):

            if keyword in text:

                score += weight

        is_it = score >= 4

        if score >= 10:

            confidence = "High"

        elif score >= 7:

            confidence = "Medium"

        elif score >= 4:

            confidence = "Low"

        else:

            confidence = "None"

        return (
            is_it,
            list(
                dict.fromkeys(
                    matches
                )
            )[:10],
            confidence,
            score
        )

    # ============================================================
    # QUERY MATCH SCORE
    # ============================================================

    def _calculate_query_match_score(
        self,
        query: str,
        tender: Dict[str, Any]
    ) -> float:
        """
        Lightweight local pre-ranking.

        This does NOT decide relevance.

        Its purpose is only to decide which candidates should
        be sent to OpenAI when retrieval returns a large number
        of documents.
        """

        query_text = self._normalize_text(
            query
        )

        tender_text = self._normalize_text(
            f"""
            {tender.get('title', '')}
            {tender.get('content', '')}
            """
        )

        if not query_text:

            return 0

        query_words = set(
            query_text.split()
        )

        tender_words = set(
            tender_text.split()
        )

        if not query_words:

            return 0

        # --------------------------------------------------------
        # Word overlap
        # --------------------------------------------------------

        overlap = (
            len(
                query_words
                &
                tender_words
            )
            /
            len(query_words)
        )

        # --------------------------------------------------------
        # Exact phrase
        # --------------------------------------------------------

        phrase_bonus = 0

        if query_text in tender_text:

            phrase_bonus = 0.35

        # --------------------------------------------------------
        # IT bonus
        # --------------------------------------------------------

        it_bonus = min(
            tender.get(
                "it_score",
                0
            ) / 20,
            0.25
        )

        score = (
            overlap * 0.45
            +
            phrase_bonus
            +
            it_bonus
        )

        return min(
            score,
            1.0
        )

    # ============================================================
    # STRICT QUERY CATEGORIES
    # ============================================================

    STRICT_QUERY_CATEGORIES = {
        "ai_ml",
        "cloud",
        "cybersecurity",
        "networking",
        "database",
        "software_acquisition",
        "hardware",
        "telecommunications",
    }

    CATEGORY_TERMS = {
        "ai_ml": {
            "ai", "artificial intelligence", "intelligence artificielle",
            "machine learning", "apprentissage automatique", "deep learning",
            "deep neural", "neural network", "neural networks",
            "reseau de neurones", "reseaux de neurones", "nlp",
            "natural language processing", "traitement du langage naturel",
            "computer vision", "vision par ordinateur", "modele predictif",
            "modeles predictifs", "predictive model", "predictive analytics",
            "generative ai", "genai", "llm", "large language model",
            "large language models", "transformer model", "chatbot intelligent",
            "reconnaissance d image", "classification automatique",
        },
        "cloud": {
            "cloud", "cloud computing", "cloud services", "private cloud",
            "cloud prive", "cloud public", "public cloud", "hybrid cloud",
            "saas", "iaas", "paas", "hebergement cloud", "hosting cloud",
            "infrastructure cloud", "virtualisation cloud",
        },
        "cybersecurity": {
            "cybersecurity", "cyber security", "cybersecurite",
            "securite informatique", "information security", "pentest",
            "penetration testing", "test d intrusion", "siem", "soc",
            "security operations", "vulnerability assessment",
            "gestion des vulnerabilites", "antivirus", "edr", "xdr",
            "pare feu", "firewall",
        },
        "networking": {
            "network", "networking", "reseau", "reseaux",
            "network infrastructure", "infrastructure reseau", "router",
            "routeur", "switch", "commutateur", "wifi", "lan", "wan",
            "sd wan", "vpn", "dns", "dhcp",
        },
        "database": {
            "database", "databases", "base de donnees", "bases de donnees",
            "postgresql", "mysql", "oracle database", "sql server",
            "mongodb", "mariadb", "nosql", "data warehouse",
        },
        "software_acquisition": {
            "software license", "software licenses", "licence logiciel",
            "licences logicielles", "acquisition logiciel", "acquisition de logiciels",
            "achat logiciel", "achat de logiciels", "software acquisition",
        },
        "hardware": {
            "computer", "computers", "ordinateur", "ordinateurs", "laptop",
            "desktop", "server", "serveur", "servers", "imprimante",
            "printer", "workstation", "materiel informatique", "hardware",
        },
        "telecommunications": {
            "telecommunication", "telecommunications", "fibre optique",
            "mobile network", "4g", "5g", "voip", "telephone system",
        },
    }

    @staticmethod
    def _contains_term(text: str, term: str) -> bool:
        """Match short acronyms as words and longer phrases semantically."""
        if not text or not term:
            return False
        term = term.strip().lower()
        if len(term) <= 3 and " " not in term:
            return re.search(rf"(?<![a-z0-9]){re.escape(term)}(?![a-z0-9])", text) is not None
        return term in text

    def _contains_any_term(self, text: str, terms: set) -> bool:
        return any(self._contains_term(text, term) for term in terms)

    def _detect_query_category(self, query: str) -> Optional[str]:
        text = self._normalize_text(query)
        if not text:
            return None

        # Specific intents first to avoid generic IT terms winning.
        priority = [
            "ai_ml", "cybersecurity", "cloud", "database",
            "networking", "telecommunications", "software_acquisition",
            "hardware",
        ]
        for category in priority:
            if self._contains_any_term(text, self.CATEGORY_TERMS[category]):
                return category

        if (
            ("software" in text and "development" in text)
            or "developpement logiciel" in text
            or "developpement application" in text
            or "application informatique" in text
            or "information system development" in text
            or "developpement systeme" in text
        ):
            return "software_development"

        return None

    def _has_category_evidence(
        self,
        category: str,
        tender: Dict[str, Any]
    ) -> bool:
        """Fast deterministic evidence gate used before the OpenAI call."""
        title = self._normalize_text(tender.get("title", ""))
        content = self._normalize_text(tender.get("content", ""))
        text = f"{title} {content}".strip()

        if category == "software_acquisition":
            terms = self.CATEGORY_TERMS[category]
            return self._contains_any_term(text, terms)

        if category == "hardware":
            return self._contains_any_term(text, self.CATEGORY_TERMS[category])

        if category == "telecommunications":
            return any(term in text for term in self.CATEGORY_TERMS[category])

        return self._contains_any_term(text, self.CATEGORY_TERMS.get(category, set()))

    # ============================================================
    # OPENAI CLASSIFICATION
    # ============================================================

    def _openai_classify_tenders(
        self,
        tenders: List[Dict[str, Any]],
        query: str,
        query_category: Optional[str] = None
    ) -> Dict[str, Dict[str, Any]]:

        if not tenders:

            return {}

        try:

            # ====================================================
            # BUILD INPUT
            # ====================================================

            blocks = []

            for tender in tenders:

                blocks.append(
                    f"""
REFERENCE: {tender['reference']}

TITLE:
{tender['title']}

BUYER:
{tender['buyer']}

PUBLICATION DATE:
{tender['publication_date']}

DEADLINE:
{tender['deadline']}

CONTENT:
{tender['content'][:self.OPENAI_CONTENT_LIMIT]}
""".strip()
                )

            tender_text = (
                "\n\n"
                "================ TENDER ================\n\n"
                .join(
                    blocks
                )
            )

            # ====================================================
            # PROMPT
            # ====================================================

            prompt = f"""
You are an expert Tunisian public procurement
classification system.

USER SEARCH QUERY:

"{query}"

The documents below were retrieved from a semantic
search engine.

Detected query category: {query_category or "generic"}

Your task is to identify tenders relevant to the EXACT USER SEARCH QUERY,
not merely tenders that belong to the general IT domain.

Return ONLY tenders that are genuinely relevant to the USER SEARCH QUERY.
Do NOT return a generic IT tender when the requested technology/domain is
more specific.

For each relevant tender, return:

- reference
- relevant
- score
- category
- match_type
- reason

============================================================
VERY IMPORTANT: SEARCH INTENT
============================================================

Relevance must be judged against the USER'S ACTUAL QUERY.

Do NOT classify a tender as relevant merely because
it is generally related to IT.

For example, if the user searches:

"software development"

then:

A tender for developing an application:
YES — strongly relevant.

A tender for developing an information system:
YES — strongly relevant.

A tender for custom software:
YES — strongly relevant.

A tender explicitly requesting software customization:
YES — relevant.

A tender for ERP development/customization:
YES — if development/customization is explicitly
part of the procurement.

A tender for ERP implementation only:
NO.

A tender for ERP selection / AMOA:
NO.

A tender for deployment of an existing ERP:
NO.

A tender for software licenses:
NO.

A tender for purchasing computers:
NO.

A tender for servers:
NO.

A tender for network equipment:
NO.

A tender for maintenance/support only:
NO, unless the user explicitly asks for maintenance.

============================================================
STRICT CATEGORY RULES
============================================================

If the detected query category is AI/ML (ai_ml):
- The tender MUST explicitly involve AI, machine learning, deep learning,
  neural networks, NLP, computer vision, predictive models/analytics, LLMs,
  generative AI, or another clearly equivalent AI/ML technology.
- Generic application development, software development, information
  systems, ERP, websites, mobile apps, databases, cloud hosting, or IT
  services are NOT AI/ML by themselves.
- A tender for developing an ordinary application MUST be rejected for an
  AI/ML query unless the tender explicitly includes AI/ML functionality.

If the detected query category is cloud:
- The tender MUST explicitly involve cloud computing, cloud hosting, private
  or public cloud, SaaS, IaaS, PaaS, cloud infrastructure, or equivalent.
- An ordinary software-development tender is NOT a cloud tender unless the
  cloud component is part of the requested work.

If the detected query category is cybersecurity:
- Require explicit cybersecurity/information-security work such as
  penetration testing, SIEM/SOC, vulnerability management, EDR/XDR,
  firewalls, security audits, or equivalent.

If the detected query category is networking:
- Require explicit networking/infrastructure work such as routers, switches,
  LAN/WAN, VPN, Wi-Fi, DNS/DHCP, or network infrastructure.

If the detected query category is database:
- Require explicit database technology, database management, SQL/NoSQL,
  PostgreSQL, MySQL, Oracle, MongoDB, data warehouse, or equivalent.

If the detected query category is software_acquisition:
- Require actual software/license acquisition rather than development or
  implementation alone.

If the detected query category is hardware:
- Require actual hardware/equipment procurement or supply.

If the detected query category is telecommunications:
- Require telecommunications services/infrastructure such as fibre, mobile,
  VoIP, 4G/5G, or equivalent.

============================================================
MATCH TYPES
============================================================

Choose exactly ONE:

direct_development
software_customization
software_implementation
software_acquisition
erp_implementation
erp_consulting
hardware
networking
cybersecurity
cloud
ai_ml
database
it_services
other

============================================================
SOFTWARE DEVELOPMENT QUERY
============================================================

For "software development" or "développement logiciel":

HIGH relevance:

- development of software
- development of applications
- development of web applications
- development of mobile applications
- development of information systems
- development of digital platforms
- custom software development
- programming
- software engineering
- software customization

NOT relevant:

- ERP selection
- ERP consulting
- AMOA for ERP
- ERP implementation
- deployment of existing software
- software acquisition
- software licensing
- hardware acquisition
- network equipment
- general IT support

Unless the tender explicitly states that software
development/customization is part of the actual work.

============================================================
CATEGORIES
============================================================

Use exactly one:

software_development
software_acquisition
hardware
networking
cybersecurity
cloud
ai_ml
database
it_services
telecommunications
other

============================================================
SCORE
============================================================

0.90 - 1.00:
Direct and very strong match.

0.75 - 0.89:
Strong match.

0.50 - 0.74:
Moderate match.

0.25 - 0.49:
Weak match.

0.00 - 0.24:
Not relevant.

For irrelevant tenders, use a score below 0.25.

============================================================
IMPORTANT
============================================================

Return ONLY relevant tenders.

If no tender is relevant, return an empty results array.

Do not invent information.

Return ONLY valid JSON.

Format:

{{
  "results": [
    {{
      "reference": "REFERENCE",
      "relevant": true,
      "score": 0.95,
      "category": "software_development",
      "match_type": "direct_development",
      "reason": "The tender explicitly requests development of an application."
    }}
  ]
}}

============================================================
TENDERS
============================================================

{tender_text}
"""

            # ====================================================
            # OPENAI REQUEST
            # ====================================================

            response = (
                self.client
                .chat
                .completions
                .create(
                    model="gpt-4o-mini",

                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a precise "
                                "Tunisian public procurement "
                                "classification system. "
                                "Return only valid JSON."
                            )
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],

                    temperature=0,

                    response_format={
                        "type": "json_object"
                    }
                )
            )

            response_text = (
                response
                .choices[0]
                .message
                .content
                .strip()
            )

            logger.info(
                f"OpenAI response: "
                f"{response_text[:4000]}"
            )

            data = json.loads(
                response_text
            )

            results = data.get(
                "results",
                []
            )

            output = {}

            valid_match_types = {

                "direct_development",
                "software_customization",
                "software_implementation",
                "software_acquisition",
                "erp_implementation",
                "erp_consulting",
                "hardware",
                "networking",
                "cybersecurity",
                "cloud",
                "ai_ml",
                "database",
                "it_services",
                "other"
            }

            for item in results:

                reference = str(
                    item.get(
                        "reference",
                        ""
                    )
                ).strip()

                if not reference:

                    continue

                relevant = bool(
                    item.get(
                        "relevant",
                        False
                    )
                )

                try:

                    score = float(
                        item.get(
                            "score",
                            0
                        )
                    )

                except (
                    TypeError,
                    ValueError
                ):

                    score = 0

                score = max(
                    0,
                    min(
                        1,
                        score
                    )
                )

                category = str(
                    item.get(
                        "category",
                        "other"
                    )
                ).strip().lower()

                if category not in (
                    self.ALLOWED_CATEGORIES
                ):

                    category = "other"

                match_type = str(
                    item.get(
                        "match_type",
                        "other"
                    )
                ).strip().lower()

                if match_type not in (
                    valid_match_types
                ):

                    match_type = "other"

                reason = str(
                    item.get(
                        "reason",
                        ""
                    )
                ).strip()

                output[
                    reference
                ] = {

                    "relevant":
                        relevant,

                    "score":
                        score,

                    "category":
                        category,

                    "match_type":
                        match_type,

                    "reason":
                        reason
                }

            logger.info(
                f"🧠 OpenAI classified "
                f"{len(output)} tenders"
            )

            relevant_count = sum(
                1
                for item in output.values()
                if item.get(
                    "relevant"
                )
            )

            logger.info(
                f"🧠 OpenAI found "
                f"{relevant_count} relevant tenders"
            )

            return output

        except Exception as e:

            logger.exception(
                f"❌ OpenAI classification failed: {e}"
            )

            return {}

    # ============================================================
    # HARD RELEVANCE RULES
    # ============================================================

    def _passes_query_relevance_rules(
        self,
        query: str,
        tender: Dict[str, Any],
        query_category: Optional[str] = None
    ) -> bool:
        """
        Deterministic final guardrail. OpenAI provides semantic judgment,
        while this function prevents category drift and obvious false positives.
        """
        query_text = self._normalize_text(query)
        category = query_category or self._detect_query_category(query)
        ai_category = tender.get("category", "other")
        match_type = tender.get("match_type", "other")

        # For strict categories, require evidence in the actual tender text.
        if category in self.STRICT_QUERY_CATEGORIES:
            if not self._has_category_evidence(category, tender):
                return False
            if ai_category not in {category, "it_services", "other"}:
                return False

        # AI/ML is intentionally strict: generic software development is not AI.
        if category == "ai_ml":
            if ai_category not in {"ai_ml", "it_services", "other"}:
                return False
            if match_type not in {"ai_ml", "it_services", "other"}:
                return False
            return self._has_category_evidence("ai_ml", tender)

        # Cloud requires an explicit cloud component.
        if category == "cloud":
            if match_type not in {"cloud", "it_services", "other"}:
                return False
            return self._has_category_evidence("cloud", tender)

        # Cybersecurity should not be confused with generic IT or physical security.
        if category == "cybersecurity":
            if match_type not in {"cybersecurity", "it_services", "other"}:
                return False
            return self._has_category_evidence("cybersecurity", tender)

        # Networking.
        if category == "networking":
            if match_type not in {"networking", "it_services", "other"}:
                return False
            return self._has_category_evidence("networking", tender)

        # Database.
        if category == "database":
            if match_type not in {"database", "it_services", "other"}:
                return False
            return self._has_category_evidence("database", tender)

        # Software development: preserve the previous strong exclusions.
        software_development_query = (
            ("software" in query_text and "development" in query_text)
            or "developpement logiciel" in query_text
            or "developpement application" in query_text
            or "application informatique" in query_text
            or "developpement systeme" in query_text
        )

        if software_development_query:
            forbidden_match_types = {
                "erp_implementation",
                "erp_consulting",
                "software_acquisition",
                "software_implementation",
                "hardware",
                "networking",
                "cybersecurity",
                "cloud",
                "telecommunications",
            }
            if match_type in forbidden_match_types:
                return False
            if ai_category == "it_services" and match_type not in {
                "direct_development",
                "software_customization",
            }:
                return False

        return True

    # ============================================================
    # FINAL SCORE
    # ============================================================

    @staticmethod
    def _calculate_final_score(
        tender: Dict[str, Any]
    ) -> float:

        ai_score = float(
            tender.get(
                "ai_score",
                0
            )
        )

        query_score = float(
            tender.get(
                "query_match_score",
                0
            )
        )

        retrieval_score = float(
            tender.get(
                "retrieval_score",
                0
            )
        )

        # --------------------------------------------------------
        # AI = primary signal
        # Local query = secondary
        # Retrieval = tertiary
        # --------------------------------------------------------

        final_score = (

            ai_score * 0.70

            +

            query_score * 0.20

            +

            retrieval_score * 0.10

        )

        return round(
            min(
                final_score,
                1
            ),
            4
        )

    # ============================================================
    # SEMANTIC RESULT DEDUPLICATION
    # ============================================================

    def _semantic_deduplicate_results(
        self,
        tenders: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        results = []

        for tender in tenders:

            duplicate = False

            title = self._normalize_text(
                tender.get(
                    "title",
                    ""
                )
            )

            buyer = self._normalize_text(
                tender.get(
                    "buyer",
                    ""
                )
            )

            for existing in results:

                existing_title = (
                    self._normalize_text(
                        existing.get(
                            "title",
                            ""
                        )
                    )
                )

                existing_buyer = (
                    self._normalize_text(
                        existing.get(
                            "buyer",
                            ""
                        )
                    )
                )

                existing_deadline = self._normalize_deadline_key(
                    existing.get("deadline", "")
                )
                current_deadline = self._normalize_deadline_key(
                    tender.get("deadline", "")
                )

                # Same buyer + highly overlapping title + same deadline.
                # Requiring the deadline avoids collapsing genuinely different
                # procurements that happen to have similar titles.
                if (
                    buyer
                    and buyer == existing_buyer
                    and current_deadline
                    and current_deadline == existing_deadline
                    and self._title_similarity(
                        title,
                        existing_title
                    ) >= 0.75
                ):
                    duplicate = True
                    break

            if not duplicate:

                results.append(
                    tender
                )

        return results

    # ============================================================
    # TITLE SIMILARITY
    # ============================================================

    @staticmethod
    def _title_similarity(
        title_a: str,
        title_b: str
    ) -> float:

        if not title_a or not title_b:

            return 0

        words_a = set(
            title_a.split()
        )

        words_b = set(
            title_b.split()
        )

        if not words_a or not words_b:

            return 0

        intersection = (
            words_a & words_b
        )

        union = (
            words_a | words_b
        )

        return (
            len(intersection)
            /
            len(union)
        )

    # ============================================================
    # CHAT
    # ============================================================

    def chat(
        self,
        message: str,
        thread_id: str = "default"
    ) -> str:

        try:

            tenders = self.search_tenders(
                query=message,
                status="active"
            )

            if not tenders:

                return (
                    "No relevant active tenders "
                    "were found for your request."
                )

            response = (
                f"🎯 Found {len(tenders)} "
                f"relevant active tender"
                f"{'s' if len(tenders) != 1 else ''}:\n\n"
            )

            for index, tender in enumerate(
                tenders[:10],
                1
            ):

                response += (
                    f"{index}. "
                    f"**{tender['title']}**\n"
                )

                response += (
                    f"   Reference: "
                    f"{tender['reference']}\n"
                )

                response += (
                    f"   Category: "
                    f"{tender.get('category')}\n"
                )

                response += (
                    f"   Buyer: "
                    f"{tender.get('buyer')}\n"
                )

                response += (
                    f"   Deadline: "
                    f"{tender.get('deadline')}\n"
                )

                response += (
                    f"   Relevance: "
                    f"{tender.get('ai_score', 0):.0%}\n"
                )

                response += "\n"

            return response

        except Exception as e:

            logger.exception(
                f"❌ Chat error: {e}"
            )

            return (
                "An error occurred while searching "
                "for tenders."
            )

    # ============================================================
    # ANALYZE TENDER
    # ============================================================

    def analyze_tender(
        self,
        tender_id: str
    ) -> Optional[Dict[str, Any]]:

        try:

            from models import Tender

            tender = (
                Tender.query
                .filter(
                    Tender.reference == tender_id
                )
                .first()
            )

            if not tender:

                return None

            title = getattr(
                tender,
                "title",
                ""
            )

            content = getattr(
                tender,
                "description",
                ""
            )

            if not content:

                content = getattr(
                    tender,
                    "content",
                    ""
                )

            deadline = getattr(
                tender,
                "deadline",
                ""
            )

            prompt = f"""
Analyze this Tunisian public tender.

Reference:
{tender_id}

Title:
{title}

Deadline:
{deadline}

Content:
{content}

Provide:

- Summary
- Main objective
- IT relevance
- Category
- Important requirements
- Potential technologies or solutions
- Deadline
- Risks or points requiring attention

Do not invent information.
"""

            response = (
                self.client
                .chat
                .completions
                .create(
                    model="gpt-4o-mini",

                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are an expert "
                                "public procurement analyst."
                            )
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],

                    temperature=0.2
                )
            )

            return {

                "reference":
                    tender_id,

                "title":
                    title,

                "analysis":
                    response
                    .choices[0]
                    .message
                    .content
            }

        except Exception as e:

            logger.exception(
                f"❌ Tender analysis failed: {e}"
            )

            return None

    # ============================================================
    # CACHE
    # ============================================================

    def clear_cache(self):

        self.search_cache.clear()

        logger.info(
            "🧹 Tender search cache cleared"
        )


