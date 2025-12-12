from fastapi import FastAPI, status
from backend.app.api.main import api_router
from backend.app.core.config import settings
from contextlib import asynccontextmanager
from backend.app.core.db import init_db, engine
from backend.app.core.logging import get_logger
from fastapi.responses import JSONResponse
from backend.app.core.health import health_checker, ServiceStatus
import asyncio, time

logger = get_logger()

async def startup_health_check(timeout: float=90.0) -> bool:
    try:
        async with asyncio.timeout(timeout):
            retry_intervals = [1, 2, 5, 10, 15]
            start_time = time.time()
            while True:
                is_healthy = await health_checker.wait_for_services()
                if is_healthy:
                    logger.info("All services are healthy.")
                    return True
                
                elapsed_time = time.time() - start_time
                if elapsed_time >= timeout:
                    logger.error("Services failed health check during startup.")
                    return False
                
                wait_time = retry_intervals[
                    min(len(retry_intervals) - 1, int(elapsed_time / 10))
                ]
                logger.warning(f"Services not healthy yet. Retrying in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
    except asyncio.TimeoutError:
        logger.error(f"Startup health check timed out after {timeout} seconds.")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during startup health check: {e}")
        return False

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await init_db()
        logger.info("Database initialized successfully.")

        await health_checker.add_service("database", health_checker.check_database)
        await health_checker.add_service("redis", health_checker.check_redis)
        await health_checker.add_service("celery", health_checker.check_celery)

        if not await startup_health_check():
            logger.critical("Application startup aborted due to unhealthy services.")
            raise RuntimeError("Unhealthy services detected during startup.")
        
        logger.info("Application startup complete.")
        yield

    except Exception as e:
        logger.error(f"Application failed to start: {e}")
        await engine.dispose()
        await health_checker.cleanup()
        raise e

    finally:
        logger.info("Shutting down application...")
        await engine.dispose()
        await health_checker.cleanup()
    
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

@app.get("/health", response_class=JSONResponse)
async def health_check():
    try:
        health_status = await health_checker.check_all_services()

        if health_status["status"] == ServiceStatus.HEALTHY:
            status_code = status.HTTP_200_OK

        elif health_status["status"] == ServiceStatus.DEGRADED:
            status_code = status.HTTP_206_PARTIAL_CONTENT
        else:
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE

        return JSONResponse(status_code=status_code, content=health_status)
    
    except Exception as e:
        logger.error(f"Health check endpoint failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": ServiceStatus.UNHEALTHY, "details": str(e)},
        )
    
app.include_router(api_router, prefix=settings.API_V1_STR)