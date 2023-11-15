import asyncio
import openai


class OpenAIProcessor:
    def __init__(self, api_key: str):
        openai.api_key = api_key
        self.colors = {
            "#FF2364": "vivid pink",
            "#4D1BF3": "bright blue",
            "#3E16C2": "deep violet",
            "#8664F7": "soft purple",
            "#ffae00": "sunny yellow",
            "#ff8a19": "warm orange",
            "#ff6831": "vibrant coral",
            "#ff454a": "strong red",
        }
        self.website_images = [
            "https://www.predicthq.com/icons/large/event-cat-lg/icon-lg-non-attendance-based.svg",
            "https://www.predicthq.com/icons/large/event-cat-lg/icon-lg-attendance-based.svg",
            "https://www.predicthq.com/icons/large/event-cat-lg/icon-lg-unscheduled.svg",
            "https://www.predicthq.com/icons/large/event-cat-lg/icon-lg-live-tv-events.svg",
            "https://images.ctfassets.net/ihlmn42cjuv0/1h2RcWfL67OGrsd9vwPQ9s/28b56a8f304c0021c365b8e323d3d5cd/demand_forecasting.svg",
        ]

    async def process(self, event: dict) -> any:
        client = openai.OpenAI(api_key=openai.api_key)
        venues = [e for e in event["entities"] if e["type"] == "venue"]

        response = client.images.generate(
            model="dall-e-3",
            prompt=f"""
            Create a single minimalist icon for the event {event["title"]} for category {event["category"]}, representing {event["labels"]}.
            The icon should be on a distinct white background, with a modern and clean aesthetic, using a restrained color palette: {[k + "(" + v + ")" for k,v in self.colors.items()]}.
            """
            + f"""
            Incorporate location design in the background for {[v["name"] for v in venues]} but priorities
            the abstract and clean aesthetic.
            """
            if venues
            else ""
            + f"""
            The design should incorporate key elements that are iconic to each label in {event["labels"]}, utilizing minimalist geometric shapes and colors sparingly for elegant outlines and subtle detail. Emphasize the silhouette and negative space to create a visually impactful icon that remains easily scalable and recognizable at different sizes, maintaining uniform line weights and a refined style suitable for digital platforms and user interfaces.
            Take the following images for examples: {self.website_images}
            """,
            # It should be in white background that incorporate these colors: {self.colors}
            size="1024x1024",
            quality="standard",
            n=1,
        )

        image_url = response.data[0].url

        return image_url


async def processor():
    app = OpenAIProcessor(api_key="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")

    import json

    output = {}
    with open("event.json", "r") as f:
        events = json.load(f)
        for event in events["data"]:
            url = await app.process(event)
            output[event["id"]] = {"img": url}
            output[event["id"]].update(
                {
                    k: v
                    for k, v in event.items()
                    if k in ["title", "category", "entities", "labels"]
                }
            )
            print(url)
    with open("output.json", "w") as f:
        f.write(json.dumps(output, indent=4))


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(processor())
    loop.run_until_complete(future)
