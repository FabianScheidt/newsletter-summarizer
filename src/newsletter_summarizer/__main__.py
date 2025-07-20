import json
import pathlib

from newsletter_summarizer import lambda_handler


if __name__ == "__main__":
    dir = pathlib.Path(__file__).parent.resolve()
    with open(dir / "../../sample-data/events/sample.json", "r") as f:
        event = json.load(f)
        lambda_handler(event, {})
