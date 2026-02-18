import asyncio
import uvicorn

if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    uvicorn.run(
        "app.main:app",
        host="localhost",
        port=8000,
    )
