from flask import Flask, request, jsonify
import threading

class RobotApiServer:
    def __init__(self, robot_app, host='127.0.0.1', port=5001):
        self.app = robot_app
        self.server = Flask(__name__)
        self._setup_routes()

    def _setup_routes(self):
        @self.server.route('/v1/vision/color', methods=['POST'])
        def set_color():
            color = request.json.get('color')
            if self.app.estimator.set_target_color(color):
                return jsonify({"status": "success", "target": color}), 200
            return jsonify({"status": "error"}), 400

    def start(self):
        t = threading.Thread(target=lambda: self.server.run(
            host='127.0.0.1', port=5001, debug=False, use_reloader=False), daemon=True)
        t.start()