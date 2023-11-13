# TC2008B Modelación de Sistemas Multiagentes con gráficas computacionales
# Python server to interact with Unity via POST
# Sergio Ruiz-Loza, Ph.D. March 2021

from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import json

from StorageModel import StorageModel


MAX_STEPS = 1500
GRID_WIDTH = 20
GRID_HEIGH = 20
N_EXPLORERS = 3
N_COLELCTORS = 2
MAX_FOOD = 47


class Server(BaseHTTPRequestHandler):

    @property
    def api_response(self):
        model = StorageModel(GRID_WIDTH, GRID_HEIGH,
                             N_EXPLORERS, N_COLELCTORS, MAX_FOOD)

        for _ in range(MAX_STEPS):
            model.step()
            if not model.running:
                break
        data = model.datacollector.get_model_vars_dataframe().get("Data")
        data = list(data)

        return json.dumps({"steps": len(data), "data": data}).encode()

    def do_GET(self):
        if self.path == '/':
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(bytes(self.api_response))


def run(server_class=HTTPServer, handler_class=Server, port=8585):
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info("Starting httpd...\n")  # HTTPD is HTTP Daemon!
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:   # CTRL+C stops the server
        pass
    httpd.server_close()
    logging.info("Stopping httpd...\n")


if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
