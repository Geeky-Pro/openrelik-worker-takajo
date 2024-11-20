import os
import shutil
import subprocess
import time
from uuid import uuid4

from openrelik_worker_common.utils import (
    create_output_file,
    get_input_files,
    task_result,
)

from .app import celery

# Task name used to register and route the task to the correct queue.
TASK_NAME = "openrelik-worker-takajo.tasks.automagic_timeline"

# Task metadata for registration in the core system.
TASK_METADATA = {
    "display_name": "Takajo Automagic Timeline",
    "description": "Automagic analysis task for Hayabusa JSONL results",
}

@celery.task(bind=True, name=TASK_NAME, metadata=TASK_METADATA)
def automagic_timeline(
    self,
    pipe_result=None,
    input_files=[],
    output_path=None,
    workflow_id=None,
    task_config={},
) -> str:
    input_files = get_input_files(pipe_result, input_files or [])
    output_files = []

    # Create a unique output directory for Takajo results
    output_dir = os.path.join(output_path, f"takajo_results_{uuid4().hex}")
    os.mkdir(output_dir)

    # Create a temporary directory for input files
    temp_dir = os.path.join(output_path, uuid4().hex)
    os.mkdir(temp_dir)
    for file in input_files:
        filename = os.path.basename(file.get("path"))
        os.link(file.get("path"), os.path.join(temp_dir, filename))

    # Construct the automagic command
    command = [
        "/takajo/takajo",
        "automagic",           # Automagic command
        "-t", temp_dir,        # Input directory
        "-o", output_dir,      # Output directory
    ]

    INTERVAL_SECONDS = 2
    process = subprocess.Popen(command)
    while process.poll() is None:
        self.send_event("task-progress", data=None)
        time.sleep(INTERVAL_SECONDS)

    # Clean up the temporary input directory
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

    # Collect all files generated in the output directory
    if os.path.exists(output_dir):
        for root, _, files in os.walk(output_dir):
            for file in files:
                file_path = os.path.join(root, file)
                file_extension = os.path.splitext(file)[-1].lstrip(".").lower()
                
                # Create metadata for each result file
                output_file = create_output_file(
                    output_path,
                    filename=os.path.basename(file_path),
                    file_extension=file_extension,
                    data_type=f"openrelik:worker:takajo:file:{file_extension}",
                )
                
                # Link the actual file path
                os.link(file_path, output_file.path)

                # Append the result file metadata
                output_files.append(output_file.to_dict())

    if not output_files:
        raise RuntimeError("Automagic didn't generate any output files.")

    return task_result(
        output_files=output_files,
        workflow_id=workflow_id,
        command=" ".join(command),
    )
