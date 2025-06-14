from fastapi import Response
import time
import datetime
from fastapi import Request
import json

async def transform_response_middleware(request : Request, call_next):
    """
    Transforms the response by adding processing time and request ID.
    It calculates the processing time, formats the response, and attaches it to the state.
    This function ensures that the response is formatted consistently before being returned.
    """
    if request.method == "OPTIONS":
        response = await call_next(request)
        return response

    start_time = time.time()
    if request.url.path in ["/docs", "/openapi.json", "/redoc"]:
        return await call_next(request)


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

    final_response = Response(
        content=modified_response,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.media_type,
    )

    # Copy Set-Cookie headers manually
    set_cookie_headers = [header for header in response.raw_headers if header[0].lower() == b'set-cookie']
    for header in set_cookie_headers:
        final_response.raw_headers.append(header)

    return final_response
