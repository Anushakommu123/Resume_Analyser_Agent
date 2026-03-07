"""Tuning agent for customizing resumes for specific job descriptions."""
import json
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from app.config import settings
from app.utils.prompts import TUNING_SYSTEM_PROMPT, TUNING_USER_PROMPT_TEMPLATE


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
    
    async def tune(self, resume_text: str, job_description: str, analysis_summary: Dict[str, Any]) -> Dict[str, Any]:
        """
        Tune resume for a specific job description.
        
        Args:
            resume_text: Original resume text
            job_description: Job description text
            analysis_summary: Analysis results from AnalysisAgent
            
        Returns:
            Dictionary containing tuned resume data
        """
        # Format analysis summary as string
        analysis_str = json.dumps(analysis_summary, indent=2)
        
        # Format the prompt
        prompt = self.prompt_template.format_messages(
            resume=resume_text,
            job_description=job_description,
            analysis_summary=analysis_str
        )
        
        # Get LLM response
        response = await self.llm.ainvoke(prompt)
        
        # Parse JSON response
        try:
            # Extract JSON from response (handle markdown code blocks if present)
            content = response.content.strip()
            if content.startswith("```json"):
                content = content[7:]  # Remove ```json
            if content.startswith("```"):
                content = content[3:]  # Remove ```
            if content.endswith("```"):
                content = content[:-3]  # Remove closing ```
            
            tuned_resume = json.loads(content.strip())
            return tuned_resume
        except json.JSONDecodeError as e:
            # Fallback: try to extract JSON from text
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                tuned_resume = json.loads(json_match.group())
                return tuned_resume
            else:
                # Return error structure if parsing fails
                return {
                    "error": f"Error parsing tuned resume: {str(e)}",
                    "original_resume": resume_text
                }

