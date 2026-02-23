from functools import wraps

import stamina
from sqlalchemy.orm.exc import StaleDataError

from core.db.session import session


def transactional(func):
    @wraps(func)
    async def _transactional(*args, **kwargs):
        if session.in_transaction():
            return await func(*args, **kwargs)

        # Use stamina for robust retry logic on StaleDataError (Optimistic Lock failure)
        # It handles exponential backoff and max attempts internally.
        @stamina.retry(
            on=StaleDataError,
            attempts=3,
            wait_initial=0.1,
        )
        async def _execute_with_retry():
            async with session() as db_session:
                async with db_session.begin():
                    try:
                        result = await func(*args, **kwargs)
                        await db_session.commit()
                        return result
                    except Exception as e:
                        await db_session.rollback()
                        raise e
                    finally:
                        await db_session.close()

        return await _execute_with_retry()

    return _transactional
