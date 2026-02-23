from functools import wraps
import asyncio
from sqlalchemy.orm.exc import StaleDataError
from core.db.session import session

def transactional(func):
    @wraps(func)
    async def _transactional(*args, **kwargs):
        if session.in_transaction():
            return await func(*args, **kwargs)

        max_retry = 3
        retry_count = 0
        backoff_factor = 0.1 # 100ms

        while True:
            async with session() as db_session:
                async with db_session.begin():
                    try:
                        result = await func(*args, **kwargs)
                        await db_session.commit()
                        return result
                    except StaleDataError as e:
                        await db_session.rollback()
                        retry_count += 1
                        if retry_count > max_retry:
                            raise e
                        
                        # Exponential backoff
                        await asyncio.sleep(backoff_factor * (2 ** (retry_count - 1)))
                        # Clear session for retry
                        await db_session.close()
                        continue
                    except Exception as e:
                        await db_session.rollback()
                        raise e
                    finally:
                        await db_session.close()

    return _transactional
