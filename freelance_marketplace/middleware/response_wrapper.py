from fastapi import Response
import time
import datetime
import json

async def transform_response_middleware(request, call_next):
    """
    Transforms the response by adding processing time and request ID.
    It calculates the processing time, formats the response, and attaches it to the state.
    This function ensures that the response is formatted consistently before being returned.
    """
    
    if request.url.path in ["/docs", "/openapi.json", "/redoc"]:
        return await call_next(request)
    
    start_time = time.time()
    response = await call_next(request)

    chunks = []
    async for chunk in response.body_iterator:
        chunks.append(chunk)
    response_body = b''.join(chunks)

    content = response_body.decode() if response_body else None

    try:
        data = json.loads(content) if content else None
    except json.JSONDecodeError:
        data = content

    request.state.processing_time = round(time.time() - start_time, 4)
    
    formatted_response = {
        "status": "success" if response.status_code < 400 else "error",
        "code": response.status_code,
        "data": data,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "processing_time": request.state.processing_time,
        "metadata": {
            "api_version": "v1",
            "path": request.url.path,
            "method": request.method
        }
    }

    request.state.formatted_response = formatted_response

    modified_response = json.dumps(formatted_response).encode("utf-8")
    response.headers["Content-Length"] = str(len(modified_response))

    return Response(
        content=modified_response,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.media_type,
    )
