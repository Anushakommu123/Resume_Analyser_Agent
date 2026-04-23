"""Tuning agent for customizing resumes for specific job descriptions."""
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from app.config import settings
from app.database import db
from app.utils.prompts import TUNING_SYSTEM_PROMPT, TUNING_USER_PROMPT_TEMPLATE

logger = logging.getLogger(__name__)

MIN_ATS_SCORE = 90
MAX_TUNING_ATTEMPTS = 3


class TuningAgent:
    """Agent responsible for tuning resumes to match job descriptions."""

    def __init__(self):
        """Initialize the tuning agent with LLM."""
        import os
        # Validate API key
        api_key = settings.openai_api_key
        if not api_key or api_key.strip() == "":
            raise ValueError(
                "OpenAI API key is not set. Please set OPENAI_API_KEY in your .env file. "
                "Get your API key from: https://platform.openai.com/account/api-keys"
            )

        # Set API key as environment variable for langchain compatibility
        os.environ["OPENAI_API_KEY"] = api_key
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.4,
            api_key=api_key  # Also pass directly for reliability
        )
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", TUNING_SYSTEM_PROMPT),
            ("human", TUNING_USER_PROMPT_TEMPLATE)
        ])

    async def tune(
        self,
        resume_text: str,
        job_description: str,
        analysis_summary: Dict[str, Any],
        job_id: Optional[str] = None,
        jd_filename: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Tune resume for a specific job description, targeting ATS score >= 90.

        Args:
            resume_text: Original resume text
            job_description: Job description text
            analysis_summary: Analysis results from AnalysisAgent
            job_id: Optional job identifier used to persist the ATS score in MongoDB
            jd_filename: Optional JD filename stored alongside the ATS score

        Returns:
            Dictionary containing tuned resume data (including ats_score)
        """
        analysis_str = json.dumps(analysis_summary, indent=2)

        tuned_resume: Dict[str, Any] = {}
        last_error: Optional[str] = None

        for attempt in range(1, MAX_TUNING_ATTEMPTS + 1):
            human_message = (
                f"Original Resume:\n{resume_text}\n\n"
                f"Job Description:\n{job_description}\n\n"
                f"Analysis Summary:\n{analysis_str}\n\n"
                "Produce the ATS-optimized tuned resume as a single JSON object. "
                f"Ensure ats_score is >= {MIN_ATS_SCORE} — revise internally until it is."
            )
            if attempt > 1 and tuned_resume:
                human_message += (
                    f"\n\nPrevious attempt returned ats_score={tuned_resume.get('ats_score')}, "
                    f"which is below the required {MIN_ATS_SCORE}. "
                    "Rewrite the resume with stronger ATS keyword coverage, richer quantified impact, "
                    "and tighter alignment with the job description so the new ats_score is >= 90."
                )

            prompt = self.prompt_template.format_messages(
                resume=resume_text,
                job_description=job_description,
                analysis_summary=analysis_str,
            )
            # Replace the last human message with the reinforced one on retries
            if attempt > 1:
                prompt[-1].content = human_message

            response = await self.llm.ainvoke(prompt)

            parsed = self._parse_response(response.content)
            if "error" in parsed:
                last_error = parsed["error"]
                continue

            tuned_resume = parsed
            ats_score = self._coerce_score(tuned_resume.get("ats_score"))
            tuned_resume["ats_score"] = ats_score

            if ats_score >= MIN_ATS_SCORE:
                break

        if not tuned_resume:
            return {
                "error": last_error or "Failed to tune resume",
                "original_resume": resume_text,
            }

        await self._store_ats_score(
            job_id=job_id,
            jd_filename=jd_filename,
            ats_score=tuned_resume.get("ats_score", 0),
            ats_score_breakdown=tuned_resume.get("ats_score_breakdown"),
        )

        return tuned_resume

    @staticmethod
    def _parse_response(content: str) -> Dict[str, Any]:
        """Parse the LLM JSON response, tolerating markdown code fences."""
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]

        try:
            return json.loads(content.strip())
        except json.JSONDecodeError as e:
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass
            return {"error": f"Error parsing tuned resume: {str(e)}"}

    @staticmethod
    def _coerce_score(value: Any) -> int:
        """Coerce any LLM-returned ats_score into an int in [0, 100]."""
        try:
            score = int(round(float(value)))
        except (TypeError, ValueError):
            return 0
        return max(0, min(100, score))

    async def _store_ats_score(
        self,
        job_id: Optional[str],
        jd_filename: Optional[str],
        ats_score: int,
        ats_score_breakdown: Optional[Dict[str, Any]],
    ) -> None:
        """Persist the tuned-resume ATS score to the `analysis_result` collection."""
        if not job_id or not db.is_connected():
            if not db.is_connected():
                logger.warning("MongoDB not connected; skipping ATS score persistence.")
            return

        document = {
            "job_id": job_id,
            "jd_filename": jd_filename,
            "ats_score": ats_score,
            "ats_score_breakdown": ats_score_breakdown,
            "meets_threshold": ats_score >= MIN_ATS_SCORE,
            "updated_at": datetime.now(timezone.utc),
        }

        try:
            collection = db.get_collection("analysis_result")
            await collection.update_one(
                {"job_id": job_id},
                {"$set": document, "$setOnInsert": {"created_at": document["updated_at"]}},
                upsert=True,
            )
            logger.info(f"Stored ATS score {ats_score} for job_id={job_id} in analysis_result.")
        except Exception as e:
            logger.error(f"Failed to store ATS score for job_id={job_id}: {e}")

