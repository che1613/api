from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from uuid import uuid4
from pathlib import Path

# Initialize FastAPI app
app = FastAPI()

# Folder to save uploaded files
upload_folder = Path("uploads")
if not upload_folder.exists():
    upload_folder.mkdir()  # Create folder if it doesn't exist

# Dictionary to store file information
file_info = {}

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    """
    Endpoint to upload a file.
    """
    # Generate a unique file ID
    file_id = str(uuid4())

    # Validate that the file is an image
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed.")

    # Save the file in the uploads folder
    file_path = upload_folder / f"{file_id}_{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Store file information
    file_info[file_id] = {"filename": file.filename, "status": "uploaded"}

    return {"file_id": file_id, "filename": file.filename}

@app.get("/status/{file_id}/")
def get_status(file_id: str):
    """
    Endpoint to check the status of an uploaded file.
    """
    if file_id not in file_info:
        raise HTTPException(status_code=404, detail="File not found.")

    return file_info[file_id]

@app.get("/files/{file_id}/")
def get_file(file_id: str):
    """
    Endpoint to retrieve a file by its unique ID.
    """
    if file_id not in file_info:
        raise HTTPException(status_code=404, detail="File not found.")

    file_path = upload_folder / f"{file_id}_{file_info[file_id]['filename']}"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk.")

    return FileResponse(file_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
