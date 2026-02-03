from celery.utils.log import get_task_logger
from celery import shared_task

import os
import zipfile
import asyncio

from app.core.celery_config import celery_app
from app.config import settings
from app.services.candidate_service import create_candidate_from_parsed
from app.database import async_session_maker
from app.services.ai_service_client import AIServiceClient


logger = get_task_logger(__name__)

# async def process_resume_batch(zip_path):
#     """
#     Synchronous Celery task:
#     - extracts zip to uploads/batches/<task_id>
#     - iterates supported files -> calls AI service -> persists candidate via async DB helper
#     Returns stats dict.
#     """
#     logger.info(f"Processing batch from {zip_path}")
#     stats = {"processed": 0, "failed": []}
    
#     # Check if zip file exists
#     if not os.path.exists(zip_path):
#         error = f"Zip file not found: {zip_path}"
#         logger.error(error)
#         stats["failed"].append(error)
#         return stats
    
#     extract_dir = os.path.dirname(zip_path)
    
#     try:
#         # Extract zip file
#         with zipfile.ZipFile(zip_path, "r") as zf:
#             zf.extractall(extract_dir)
        
#         # Collect all valid files first
#         files_to_process = []
#         for root, _, files in os.walk(extract_dir):
#             # Skip __MACOSX folder
#             if '__MACOSX' in root:
#                 continue
            
#             for fn in files:
                
#                 # Skip macOS metadata files and hidden files
#                 if fn.startswith('.') or fn.startswith('._') :
#                     logger.info("Skipping the hidden files")
#                     continue
                
#                 # Only process PDF and DOCX files
#                 if fn.lower().endswith((".pdf", ".docx")):
#                     file_path = os.path.join(root, fn)
#                     files_to_process.append((file_path, fn))
        
#         logger.info(f"Found {len(files_to_process)} files to process")
        

#         ai_client = AIServiceClient()
#         async def process_file(file_path, file_name):
#             try:
#                 parsed = ai_client.parse_resume(file_path = file_path)
#                 async with async_session_maker() as db:
#                     await create_candidate_from_parsed(db, file_path, parsed)
#                 return True, file_name
#             except Exception as e:
#                 logger.error(f"Failed {file_name}: {e}")
#                 return False, file_name
            
#             results  = await asyncio.gather(
#                 *(process_file(fp, fn) for fp, fn in files_to_process),
#                 return_exceptions = False
#             )
            
#             for ok, name in results:
#                 if ok:
#                     stats["processed"] += 1
#                 else:
#                     stats["failed"].append(name)
            
#     except zipfile.BadZipFile as e:
#         logger.error(f"Invalid zip file: {str(e)}")
#         stats["failed"].append(f"Invalid zip file: {str(e)}")
#     except Exception as e:
#         logger.error(f"Batch processing failed: {str(e)}")
#         stats["failed"].append(f"Batch processing error: {str(e)}")
#     finally:
#         # Cleanup zip file
#         try:
#             if os.path.exists(zip_path):
#                 os.remove(zip_path)
#                 logger.info(f"Cleaned up zip file: {zip_path}")
#         except Exception as e:
#             logger.error(f"Failed to cleanup zip file: {str(e)}")

#     logger.info(f"Batch processing complete. Processed: {stats['processed']}, Failed: {len(stats['failed'])}")
#     return stats
# 
async def process_resume(ctx, file_path: str,original_filename: str):
    """
    arq task to process a single resume.
    'ctx' is a context dictionary provided by arq.
    """
    logger.info(f"Processing resume: {original_filename}")
    try:
        ai_client = AIServiceClient()
        parsed_data = await ai_client.parse_resume(file_path = file_path)
        
        async with async_session_maker() as db:
            await create_candidate_from_parsed(db, file_path, parsed_data)
        logger.info(f"Successfully processed: {original_filename}")
        return {"status": "success", "filename": original_filename}
        
    except Exception as e:
        logger.error(f"Failed to process {original_filename} due to {str(e)}")
        return {"status": "failed", "filename": original_filename, "error": str(e) }