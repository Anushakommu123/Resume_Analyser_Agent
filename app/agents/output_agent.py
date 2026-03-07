"""Output agent for generating formatted resumes and summaries."""
import os
import json
from typing import Dict, Any
from pathlib import Path
from app.utils.formatters import format_resume_markdown, format_resume_docx


class OutputAgent:
    """Agent responsible for generating output files."""
    
    def __init__(self, output_dir: str = "outputs"):
        """
        Initialize the output agent.
        
        Args:
            output_dir: Directory for output files
        """
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_outputs(
        self,
        job_id: str,
        tuned_resume: Dict[str, Any],
        analysis_summary: Dict[str, Any],
        jd_filename: str
    ) -> Dict[str, str]:
        """
        Generate Markdown and DOCX resumes plus JSON summary.
        
        Args:
            job_id: Unique identifier for this job analysis
            tuned_resume: Tuned resume data dictionary
            analysis_summary: Analysis results dictionary
            jd_filename: Original JD filename
            
        Returns:
            Dictionary with paths to generated files
        """
        # Create job-specific directory
        job_dir = os.path.join(self.output_dir, job_id)
        os.makedirs(job_dir, exist_ok=True)
        
        # Generate filenames
        base_name = Path(jd_filename).stem if jd_filename else job_id
        
        # Generate Markdown resume
        md_path = os.path.join(job_dir, f"{base_name}_resume.md")
        md_content = format_resume_markdown(tuned_resume)
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        # Generate DOCX resume
        docx_path = os.path.join(job_dir, f"{base_name}_resume.docx")
        format_resume_docx(tuned_resume, docx_path)
        
        # Generate JSON summary
        summary_path = os.path.join(job_dir, f"{base_name}_analysis.json")
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(analysis_summary, f, indent=2, ensure_ascii=False)
        
        # Generate Markdown summary (human-readable)
        md_summary_path = os.path.join(job_dir, f"{base_name}_analysis.md")
        md_summary_content = self._format_summary_markdown(analysis_summary, jd_filename)
        with open(md_summary_path, 'w', encoding='utf-8') as f:
            f.write(md_summary_content)
        
        return {
            "markdown_resume": md_path,
            "docx_resume": docx_path,
            "json_summary": summary_path,
            "markdown_summary": md_summary_path
        }
    
    def _format_summary_markdown(self, analysis: Dict[str, Any], jd_filename: str) -> str:
        """
        Format analysis summary as Markdown.
        
        Args:
            analysis: Analysis results dictionary
            jd_filename: Job description filename
            
        Returns:
            Formatted Markdown string
        """
        lines = []
        lines.append(f"# Resume Analysis Summary\n")
        lines.append(f"**Job Description:** {jd_filename}\n")
        lines.append(f"**Fit Score:** {analysis.get('fit_score', 'N/A')}/100\n")
        
        lines.append("\n## Summary\n")
        lines.append(analysis.get('summary', 'No summary available.'))
        lines.append("")
        
        lines.append("\n## Matching Skills\n")
        matching_skills = analysis.get('matching_skills', [])
        if matching_skills:
            for skill in matching_skills:
                lines.append(f"- {skill}")
        else:
            lines.append("No matching skills identified.")
        lines.append("")
        
        lines.append("\n## Missing Skills\n")
        missing_skills = analysis.get('missing_skills', [])
        if missing_skills:
            for skill in missing_skills:
                lines.append(f"- {skill}")
        else:
            lines.append("No missing skills identified.")
        lines.append("")
        
        lines.append("\n## Strengths\n")
        strengths = analysis.get('strengths', [])
        if strengths:
            for strength in strengths:
                lines.append(f"- {strength}")
        else:
            lines.append("No specific strengths identified.")
        lines.append("")
        
        lines.append("\n## Weaknesses\n")
        weaknesses = analysis.get('weaknesses', [])
        if weaknesses:
            for weakness in weaknesses:
                lines.append(f"- {weakness}")
        else:
            lines.append("No specific weaknesses identified.")
        lines.append("")
        
        lines.append("\n## Suggestions for Improvement\n")
        suggestions = analysis.get('suggestions', [])
        if suggestions:
            for i, suggestion in enumerate(suggestions, 1):
                lines.append(f"{i}. {suggestion}")
        else:
            lines.append("No specific suggestions available.")
        lines.append("")
        
        lines.append("\n## Missing ATS Keywords\n")
        missing_keywords = analysis.get('ats_keywords_missing', [])
        if missing_keywords:
            lines.append(", ".join(missing_keywords))
        else:
            lines.append("No missing keywords identified.")
        lines.append("")
        
        return "\n".join(lines)

