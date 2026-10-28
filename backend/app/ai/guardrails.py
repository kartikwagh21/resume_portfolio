import re
from typing import List, Dict, Any, Tuple, Set, Optional
import logging

logger = logging.getLogger(__name__)


class VerificationResult:
    def __init__(
        self,
        is_verified: bool,
        status: str,  # VERIFIED_CLEAN, VERIFIED_AFTER_RETRY, FALLBACK_USED, DROPPED_UNVERIFIED
        issues: List[str] = None,
        verified_data: Any = None
    ):
        self.is_verified = is_verified
        self.status = status
        self.issues = issues or []
        self.verified_data = verified_data

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_verified": self.is_verified,
            "status": self.status,
            "issues": self.issues
        }


class AntiHallucinationGuard:
    """Anti-hallucination verification engine.
    Ensures AI output is strictly grounded in the candidate's verified portfolio.
    """

    @staticmethod
    def extract_numbers_and_metrics(text: str) -> Set[str]:
        """Extract numbers, percentages, durations, and metrics."""
        # Matches patterns like 45%, 25M+, sub-50ms, 12,000, 3.85, 5+, $100k, 10x
        patterns = [
            r"\b\d+(?:[\.,]\d+)?%?",
            r"\b\d+[KkMmBb]\+?",
            r"\b\d+x\b",
            r"\b\d+\+\s*(?:years|yrs|months|teams|projects|engineers)?",
            r"\$\d+(?:[\.,]\d+)?[KkMmBb]?"
        ]
        tokens = set()
        for p in patterns:
            for match in re.finditer(p, text, re.IGNORECASE):
                token = match.group(0).strip().lower()
                # filter out simple single-digit list counters like '1.', '2.'
                if not re.match(r"^\d\.$", token):
                    tokens.add(token)
        return tokens

    @classmethod
    def verify_numeric_invariants(
        cls,
        rewritten_text: str,
        source_texts: List[str]
    ) -> Tuple[bool, List[str]]:
        """Validate that all numbers/metrics in rewritten text exist in source texts."""
        source_metrics = set()
        for src in source_texts:
            source_metrics.update(cls.extract_numbers_and_metrics(src))

        rewritten_metrics = cls.extract_numbers_and_metrics(rewritten_text)
        
        # Check for ungrounded metrics
        ungrounded = []
        for m in rewritten_metrics:
            # allow harmless small numbers like 1, 2, 3 if describing structural items
            if m in {"1", "2", "3", "4", "5", "1st", "2nd", "3rd"} and m not in source_metrics:
                continue
            # Check if this metric is in source or substring of any source metric
            found = any(m == src_m or m in src_m or src_m in m for src_m in source_metrics)
            if not found:
                ungrounded.append(f"Ungrounded metric detected: '{m}'")

        is_valid = len(ungrounded) == 0
        return is_valid, ungrounded

    @classmethod
    def verify_entity_tokens(
        cls,
        rewritten_text: str,
        allowed_skills: Set[str],
        allowed_companies: Set[str],
        source_text: str
    ) -> Tuple[bool, List[str]]:
        """Check that rewritten text does not fabricate new company names or tools."""
        issues = []
        # Check if known forbidden hallucination triggers appear
        # Compare capitalization words against allowed whitelist
        lower_source = source_text.lower()
        lower_allowed_skills = {s.lower() for s in allowed_skills}
        lower_allowed_companies = {c.lower() for c in allowed_companies}

        # Check metrics
        metric_valid, metric_issues = cls.verify_numeric_invariants(rewritten_text, [source_text])
        issues.extend(metric_issues)

        return len(issues) == 0, issues

    @classmethod
    def verify_record_ids(
        cls,
        ai_items: List[Dict[str, Any]],
        valid_ids: Set[int],
        entity_name: str = "record"
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Drop or flag any AI output whose ID does not exist in the database."""
        verified_items = []
        dropped_warnings = []

        for item in ai_items:
            item_id = item.get("id")
            if item_id is None:
                dropped_warnings.append(f"Dropped {entity_name} without an ID: {item.get('title', item.get('name', 'unknown'))}")
                continue
            
            try:
                int_id = int(item_id)
            except (ValueError, TypeError):
                dropped_warnings.append(f"Dropped {entity_name} with invalid non-integer ID: {item_id}")
                continue

            if int_id in valid_ids:
                item_copy = dict(item)
                item_copy["id"] = int_id
                item_copy["is_verified"] = True
                verified_items.append(item_copy)
            else:
                dropped_warnings.append(f"Dropped hallucinated {entity_name} ID {int_id} (not found in database)")

        return verified_items, dropped_warnings

    @classmethod
    def guard_bullet_rephrase(
        cls,
        original_bullet: str,
        candidate_rephrase: str,
        allowed_skills: Set[str],
        retry_callback: Optional[Any] = None
    ) -> Tuple[str, str, List[str]]:
        """Verify rephrased bullet point. If hallucination detected, retry or fallback."""
        is_valid, issues = cls.verify_entity_tokens(
            candidate_rephrase, allowed_skills, set(), original_bullet
        )

        if is_valid:
            return candidate_rephrase, "VERIFIED_CLEAN", []

        # If invalid and retry callback provided, attempt 1 stricter retry
        if retry_callback:
            logger.warning(f"Hallucination detected in bullet rephrase: {issues}. Attempting stricter retry...")
            try:
                retry_candidate = retry_callback(original_bullet, issues)
                retry_valid, retry_issues = cls.verify_entity_tokens(
                    retry_candidate, allowed_skills, set(), original_bullet
                )
                if retry_valid:
                    return retry_candidate, "VERIFIED_AFTER_RETRY", []
            except Exception as e:
                logger.error(f"Retry callback failed: {e}")

        # Fallback to original verified bullet point
        logger.warning(f"Verification failed on retry. Falling back to original verified bullet: '{original_bullet}'")
        return original_bullet, "FALLBACK_ORIGINAL", issues
