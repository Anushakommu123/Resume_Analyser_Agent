"""Orchestrates resume processing: input -> analysis -> tuning -> output."""
import uuid
from typing import List
from fastapi import UploadFile

from app.agents.input_processor import InputProcessor
from app.agents.output_agent import OutputAgent


class Orchestrator:
    """Coordinates resume parsing, analysis, tuning, and output generation."""

    def __init__(self, output_dir: str = "outputs"):
        self.input_processor = InputProcessor()
        self.output_agent = OutputAgent(output_dir=output_dir)
        self._analysis_agent = None
        self._tuning_agent = None

    @property
    def analysis_agent(self):
        if self._analysis_agent is None:
            from app.agents.analysis_agent import AnalysisAgent
            self._analysis_agent = AnalysisAgent()
        return self._analysis_agent

    @property
    def tuning_agent(self):
        if self._tuning_agent is None:
            from app.agents.tuning_agent import TuningAgent
            self._tuning_agent = TuningAgent()
        return self._tuning_agent

    async def process_resume_and_jds(
        self,
        resume: UploadFile,
        job_descriptions: List[UploadFile],
    ) -> dict:
        """
        Process one resume against multiple job descriptions.
        Returns dict with batch_id, total_jds, results (list of {job_id, jd_filename, status}).
        """
        batch_id = str(uuid.uuid4())
        resume_text = await self.input_processor.process_resume(resume)
        jd_list = await self.input_processor.process_job_descriptions(job_descriptions)
        results = []

        for jd_filename, jd_text in jd_list:
            job_id = str(uuid.uuid4())
            try:
                analysis = await self.analysis_agent.analyze(resume_text, jd_text)
                tuned_resume = await self.tuning_agent.tune(
                    resume_text, jd_text, analysis
                )
                if "error" in tuned_resume:
                    results.append({
                        "job_id": job_id,
                        "jd_filename": jd_filename,
                        "status": "error",
                    })
                    continue
                self.output_agent.generate_outputs(
                    job_id=job_id,
                    tuned_resume=tuned_resume,
                    analysis_summary=analysis,
                    jd_filename=jd_filename,
                )
                results.append({
                    "job_id": job_id,
                    "jd_filename": jd_filename,
                    "status": "success",
                })
            except Exception:
                results.append({
                    "job_id": job_id,
                    "jd_filename": jd_filename,
                    "status": "error",
                })

        return {
            "batch_id": batch_id,
            "total_jds": len(results),
            "results": results,
        }
