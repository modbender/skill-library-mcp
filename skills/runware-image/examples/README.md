Examples for runware-image

1) Simple photorealistic portrait (sync):
   RUNWARE_API_KEY=<your_key> python scripts/generate_image.py --prompt "A photorealistic portrait of an adult (age 28), natural lighting" --sync --outfile "portrait.png"

2) Niagara jet ski example (sync):
   RUNWARE_API_KEY=<your_key> python scripts/generate_image.py --prompt "Photorealistic, cinematic shot of an adult female on a jet ski suspended in mid-air immediately after leaping off the edge of Niagara Falls..." --sync --outfile "niagara.png"

3) Async / webhooks: See Runware docs to configure a webhook endpoint; submit task without --sync and handle callbacks.
