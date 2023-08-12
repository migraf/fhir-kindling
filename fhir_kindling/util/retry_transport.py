import random
from datetime import datetime
from time import sleep
from typing import Iterable, Mapping, Union

import httpx

from fhir_kindling.util.date_utils import convert_to_local_datetime, parse_datetime


class RetryTransport(httpx.AsyncBaseTransport, httpx.BaseTransport):
    RETRYABLE_METHODS = frozenset(["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"])
    RETRYABLE_STATUS_CODES = frozenset([413, 429, 503, 504])

    MAX_BACKOFF_WAIT = 60

    def __init__(
        self,
        wrapped_transport: Union[httpx.BaseTransport, httpx.AsyncBaseTransport],
        max_attempts: int = 10,
        max_backoff_wait: float = MAX_BACKOFF_WAIT,
        backoff_factor: float = 0.1,
        jitter_ratio: float = 0.1,
        respect_retry_after_header: bool = True,
        retryable_methods: Iterable[str] = None,
        retry_status_codes: Iterable[int] = None,
    ) -> None:
        """
        A transport that retries requests that fail with retryable status codes.

        Args:
            wrapped_transport: The transport to wrap.
            max_attempts: The maximum number of attempts to make.
            max_backoff_wait: The maximum amount of time to wait between retries.
            backoff_factor: The amount of time to wait between retries, multiplied by
                the number of attempts made.
            jitter_ratio: The amount of jitter to add to the backoff time. This is
                multiplied by the backoff time and added or subtracted from the backoff
            time.
            respect_retry_after_header: Whether to respect the Retry-After header
                when retrying requests.
            retryable_methods: The HTTP methods that should be retried.
            retry_status_codes: The HTTP status codes that should be retried.
        """
        self.wrapped_transport = wrapped_transport
        if jitter_ratio < 0 or jitter_ratio > 0.5:
            raise ValueError(
                f"jitter ratio should be between 0 and 0.5, actual {jitter_ratio}"
            )

        self.max_attempts = max_attempts
        self.backoff_factor = backoff_factor
        self.respect_retry_after_header = respect_retry_after_header
        self.retryable_methods = (
            frozenset(retryable_methods)
            if retryable_methods
            else self.RETRYABLE_METHODS
        )
        self.retry_status_codes = (
            frozenset(retry_status_codes)
            if retry_status_codes
            else self.RETRYABLE_STATUS_CODES
        )
        self.jitter_ratio = jitter_ratio
        self.max_backoff_wait = max_backoff_wait

    def _calculate_sleep(
        self, attempts_made: int, headers: Union[httpx.Headers, Mapping[str, str]]
    ) -> float:
        retry_after_header = (headers.get("Retry-After") or "").strip()
        if self.respect_retry_after_header and retry_after_header:
            if retry_after_header.isdigit():
                return float(retry_after_header)

            try:
                # convert to local time
                parsed_date = convert_to_local_datetime(parse_datetime(retry_after_header)) 
                diff = (parsed_date - datetime.now().astimezone()).total_seconds()
                if diff > 0:
                    return min(diff, self.max_backoff_wait)
            except ValueError:
                pass

        backoff = self.backoff_factor * (2 ** (attempts_made - 1))
        jitter = (backoff * self.jitter_ratio) * random.choice([1, -1])
        total_backoff = backoff + jitter
        return min(total_backoff, self.max_backoff_wait)

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        response = self.wrapped_transport.handle_request(request)

        if request.method not in self.retryable_methods:
            return response

        remaining_attempts = self.max_attempts - 1
        attempts_made = 1

        while True:
            if (
                remaining_attempts < 1
                or response.status_code not in self.retry_status_codes
            ):
                return response

            response.close()

            sleep_for = self._calculate_sleep(attempts_made, response.headers)
            sleep(sleep_for)

            response = self.wrapped_transport.handle_request(request)

            attempts_made += 1
            remaining_attempts -= 1

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        response = await self.wrapped_transport.handle_async_request(request)

        if request.method not in self.retryable_methods:
            return response

        remaining_attempts = self.max_attempts - 1
        attempts_made = 1

        while True:
            if (
                remaining_attempts < 1
                or response.status_code not in self.retry_status_codes
            ):
                return response

            response.close()

            sleep_for = self._calculate_sleep(attempts_made, response.headers)
            sleep(sleep_for)

            response = await self.wrapped_transport.handle_async_request(request)

            attempts_made += 1
            remaining_attempts -= 1
