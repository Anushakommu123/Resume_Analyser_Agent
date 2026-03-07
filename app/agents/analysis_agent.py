"""Analysis agent for comparing resume against job descriptions."""
import json
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from app.config import settings
from app.utils.prompts import ANALYSIS_SYSTEM_PROMPT, ANALYSIS_USER_PROMPT_TEMPLATE
class AnalysisAgent:
    """Agent responsible for analyzing resume against job descriptions."""
    
    def __init__(self):
        """Initialize the analysis agent with LLM."""
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
            temperature=0.3,
            api_key=api_key  # Also pass directly for reliability
        )
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", ANALYSIS_SYSTEM_PROMPT),
            ("human", ANALYSIS_USER_PROMPT_TEMPLATE)
        ])
    
    async def analyze(self, resume_text: str, job_description: str) -> Dict[str, Any]:
        """
        Analyze resume against a job description.
        
        Args:
            resume_text: Text content of the resume
            job_description: Text content of the job description
            
        Returns:
            Dictionary containing analysis results
        """
        # Format the prompt
        prompt = self.prompt_template.format_messages(
            resume=resume_text,
            job_description=job_description
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
            
            analysis = json.loads(content.strip())
            return analysis
        except json.JSONDecodeError as e:
            # Fallback: try to extract JSON from text
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
                return analysis
            else:
                # Return error structure if parsing fails
                return {
                    "fit_score": 0,
                    "matching_skills": [],
                    "matching_experiences": [],
                    "missing_skills": [],
                    "missing_qualifications": [],
                    "strengths": [],
                    "weaknesses": ["Error parsing analysis response"],
                    "suggestions": ["Please review the analysis manually"],
                    "ats_keywords_missing": [],
                    "summary": f"Analysis error: {str(e)}"
                }

