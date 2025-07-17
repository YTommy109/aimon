#!/usr/bin/env python3
"""Simple mock AI tool server for testing."""

import json
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MockAIHandler(BaseHTTPRequestHandler):
    def do_post(self) -> None:
        if self.path == '/api/ai':
            self._handle_api_ai()
        else:
            self._handle_not_found()

    def _handle_api_ai(self) -> None:
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        try:
            request_data = json.loads(post_data.decode('utf-8'))
            logger.info(f'Received request: {request_data}')
            response = {
                'result': 'Mock AI response: Processed successfully!',
                'processed_content': request_data.get('content', ''),
                'timestamp': '2025-07-24T23:40:00Z',
            }
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            logger.info(f'Sent response: {response}')
        except Exception as e:
            self._handle_error(e)

    def _handle_error(self, e: Exception) -> None:
        logger.error(f'Error processing request: {e}')
        self.send_response(500)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        error_response = {'error': str(e)}
        self.wfile.write(json.dumps(error_response).encode('utf-8'))

    def _handle_not_found(self) -> None:
        self.send_response(404)
        self.end_headers()

    def log_message(self, fmt: str, *args: object) -> None:
        # Override to use our logger
        logger.info(f'{self.address_string()} - {fmt % args}')


if __name__ == '__main__':
    server_address = ('localhost', 9999)
    httpd = HTTPServer(server_address, MockAIHandler)
    logger.info(f'Mock AI server starting on http://{server_address[0]}:{server_address[1]}')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info('Server stopped')
        httpd.server_close()
