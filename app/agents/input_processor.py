"""Input processing agent for parsing resume and job descriptions."""
import os
import tempfile
from typing import List, Tuple
from fastapi import UploadFile
from app.utils.parsers import parse_file, save_uploaded_file


class InputProcessor:
    """Agent responsible for parsing input files."""
    
    def __init__(self, temp_dir: str = None):
        """
        Initialize the input processor.
        
        Args:
            temp_dir: Directory for temporary file storage
        """
        self.temp_dir = temp_dir or tempfile.gettempdir()
        self.upload_dir = os.path.join(self.temp_dir, "resume_uploads")
        os.makedirs(self.upload_dir, exist_ok=True)
    
    async def process_resume(self, resume_file: UploadFile) -> str:
        """
        Process and parse resume file.
        
        Args:
            resume_file: Uploaded resume file
            
        Returns:
            Extracted text content from resume
        """
        # Save uploaded file
        file_path = await save_uploaded_file(resume_file, self.upload_dir)
        
        try:
            # Parse the file
            resume_text = await parse_file(file_path)
            return resume_text
        finally:
            # Clean up temporary file
            if os.path.exists(file_path):
                os.remove(file_path)
    
    async def process_job_descriptions(self, jd_files: List[UploadFile]) -> List[Tuple[str, str]]:
        """
        Process and parse multiple job description files.
        
        Args:
            jd_files: List of uploaded job description files
            
        Returns:
            List of tuples (filename, extracted_text)
        """
        results = []
        
        for jd_file in jd_files:
            # Save uploaded file
            file_path = await save_uploaded_file(jd_file, self.upload_dir)
            
            try:
                # Parse the file
                jd_text = await parse_file(file_path)
                results.append((jd_file.filename, jd_text))
            finally:
                # Clean up temporary file
                if os.path.exists(file_path):
                    os.remove(file_path)
        
        return results

