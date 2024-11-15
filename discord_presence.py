import json, time, threading, websocket, requests
from typing import Any

class DiscordPresence:
    def __init__(self, token: str, application_id: int):
        if requests.get("https://discord.com/api/v10/users/@me", headers={"Authorization": token}).status_code == 401:
            raise Exception("Invalid Token")

        self.__presence_dict = {
            "op": 3,
            "d": {
                "since": None,
                "activities": [],
                "status": "online",
                "afk": False
            }
        }

        self.__token = token

        self.__login_dict = {
            "op": 2,
            "d": {
                "token": token,
                "properties": {
                    "os": "windows",
                    "browser": "chrome",
                    "device": "pc"
                }
            }
        }

        self.application_id = application_id

        self.__websocket = websocket.WebSocketApp("wss://gateway.discord.gg/?v=10&encoding", on_message=self.__on_message, on_open=self.__on_open)

    def __on_heartbeat(self, interval, ws: websocket.WebSocket):
        while True:
            time.sleep(interval / 1000)

            heartbeat_json = json.dumps({
                "op": 1,
                "d": None
            })

            ws.send(heartbeat_json)

    def __on_message(self, ws: websocket.WebSocket, message):
        json_data = json.loads(message)

        print(message)

        if json_data["op"] == 10:
            threading.Thread(target=self.__on_heartbeat, args=(json_data["d"]["heartbeat_interval"], ws)).start()
    def __on_open(self, ws: websocket.WebSocket):
        ws.send(json.dumps(self.__login_dict))
        ws.send(json.dumps(self.__presence_dict))

    def run(self):
        threading.Thread(target=self.__websocket.run_forever).start()

    def setPresence(self, presence_dict: dict[str, Any]):
        if not presence_dict:
            return

        presence_dict["application_id"] = self.application_id
        list.append(self.__presence_dict["d"]["activities"], presence_dict)

    def get_rpc_asset_id(self, asset_name: str) -> str:
        req = requests.get("https://discord.com/api/v9/oauth2/applications/1294321103803777085/assets?nocache=true", headers={"Authorization": self.__token})

        json_data = json.loads(req.text)

        for i in json_data:
            if i["name"] == asset_name:
                return i["id"]

        return ""