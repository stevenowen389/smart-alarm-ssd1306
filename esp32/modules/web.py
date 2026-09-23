"""Tiny web UI (microdot) to view/set the alarm — replaces Apache+WSGI."""
from microdot import Microdot

app = Microdot()


def _index_html():
    with open("web/index.html") as f:
        return f.read()


def serve(alarm_ctrl):
    @app.route("/", methods=["GET"])
    async def index(request):
        return _index_html(), 200, {"Content-Type": "text/html"}

    @app.route("/alarm", methods=["GET"])
    async def get_alarm(request):
        return alarm_ctrl.config

    @app.route("/set_alarm", methods=["POST"])
    async def set_alarm(request):
        form = request.form
        alarm_ctrl.save_config({
            "alarm_hour": int(form.get("hour", alarm_ctrl.config["alarm_hour"])),
            "alarm_minute": int(form.get("minute", alarm_ctrl.config["alarm_minute"])),
            "alarm_enabled": form.get("enabled") == "on",
            "volume": int(form.get("volume", alarm_ctrl.config["volume"])),
        })
        return {"status": "ok"}

    return app.start_server(port=80)
