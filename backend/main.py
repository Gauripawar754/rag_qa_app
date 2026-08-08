from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models import AskRequest, AskResponse, UploadResponse, HealthResponse
import rag

app = FastAPI(
    title="RAG Q&A API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)






@app.post("/upload", response_model=UploadResponse)
async def upload(file: UploadFile = File(...)):

    if not file.filename or not file.filename.endswith(".txt"):
        raise HTTPException(
            status_code=415,
            detail="Only .txt files are allowed"
        )

    try:
        content = await file.read()
        text = content.decode("utf-8", errors="replace").strip()
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Failed to read file"
        )

    if not text:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty"
        )

    try:
        doc_id, total_chunks = rag.index_document(file.filename, text)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error indexing document: {str(e)}"
        )

    return UploadResponse(
        document_id=doc_id,
        filename=file.filename,
        total_chunks=total_chunks
    )



@app.post("/ask", response_model=AskResponse)
async def ask(body: AskRequest):

    if not body.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    try:
        answer, sources = rag.answer_question(
            body.document_id,
            body.question
        )
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail="Document not found. Please upload first."
        )
    # except Exception as e:
    #     raise HTTPException(
    #         status_code=500,
    #         detail=f"LLM error: {str(e)}"
    #     )

    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"LLM service unavailable: {str(e)}"
        )

    return AskResponse(
        answer=answer,
        sources=sources
    )



@app.get("/health", response_model=HealthResponse)
async def health():
    llm_model, embedding_model = rag.get_model_info()

    return HealthResponse(
        status="ok",
        llm_model=llm_model,
        embedding_model=embedding_model
    )
