from fastapi import APIRouter
from fastapi.responses import HTMLResponse

websocket_router = APIRouter(prefix="/ws")


@websocket_router.get("/")
async def test_websocket():  # pragma: no cover
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <body>
    <button onclick="sendMessage();">Send Message</button>
    <script>
    let clientId = "client123";
    let ws = new WebSocket("ws://" + location.host + "/ws/" + clientId);
    function sendMessage() {
        console.log("test");
        ws.send(JSON.stringify({action: "hello"}));
    }

    ws.onmessage = (event) => console.log("Received:", event.data);
    ws.onopen = () => {
        console.log("Connected");
        sendMessage();
    };
    </script>
    </body>
    </html>
    """)
