import json

from channels.generic.websocket import AsyncWebsocketConsumer


class UpdateExport(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("export_order", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("export_order", self.channel_name)

    async def update_export(self, event):
        export_id = event.get("text").get("id")
        percentage = event.get("text").get("percentage")
        status = event.get("text").get("status")
        finished_at = event.get("text").get("finished_at")
        duration = event.get("text").get("duration")
        url = event.get("text").get("url")

        await self.send(text_data=json.dumps({"id": export_id,
                                              "percentage": percentage,
                                              "status": status,
                                              "finished_at": finished_at,
                                              "duration": duration,
                                              "url": url,
                                              })
                        )
