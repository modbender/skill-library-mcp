import os
import json
import argparse
import urllib.request
import urllib.parse

class FigmaClient:
    def __init__(self, token):
        self.token = token

    def _request(self, endpoint, params=None):
        url = f"https://api.figma.com/v1/{endpoint}"
        if params:
            url += "?" + urllib.parse.urlencode(params)
        
        req = urllib.request.Request(url)
        req.add_header("X-Figma-Token", self.token)
        
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())

    def get_me(self):
        return self._request("me")

    def get_team_projects(self, team_id):
        return self._request(f"teams/{team_id}/projects")

    def get_project_files(self, team_id, project_id):
        return self._request(f"teams/{team_id}/projects/{project_id}/files")

    def get_file(self, file_key):
        return self._request(f"files/{file_key}")

    def get_comments(self, file_key):
        return self._request(f"files/{file_key}/comments")

    def get_image(self, file_key, ids, format="png", scale=1.0):
        params = {
            "ids": ids,
            "format": format,
            "scale": scale
        }
        return self._request(f"images/{file_key}", params)

def main():
    parser = argparse.ArgumentParser(description="Figma API Tool")
    parser.add_argument("action", choices=["get-file", "get-comments", "export", "get-me", "get-team-projects", "get-project-files"])
    parser.add_argument("id", nargs="?", help="The file key, team ID, or project ID")
    parser.add_argument("id2", nargs="?", help="The project ID (for get-project-files)")
    parser.add_argument("--ids", help="Comma-separated layer IDs for export")
    parser.add_argument("--format", default="png", choices=["png", "jpg", "svg", "pdf"])
    parser.add_argument("--scale", type=float, default=1.0)
    
    args = parser.parse_args()
    
    token = os.getenv("FIGMA_TOKEN")
    if not token:
        print("Error: FIGMA_TOKEN environment variable not set.")
        return

    client = FigmaClient(token)
    
    try:
        if args.action == "get-file":
            if not args.id:
                print("Error: file_key is required.")
                return
            result = client.get_file(args.id)
            print(json.dumps(result, indent=2))
        elif args.action == "get-comments":
            if not args.id:
                print("Error: file_key is required.")
                return
            result = client.get_comments(args.id)
            print(json.dumps(result, indent=2))
        elif args.action == "get-me":
            result = client.get_me()
            print(json.dumps(result, indent=2))
        elif args.action == "get-team-projects":
            if not args.id:
                print("Error: team_id is required.")
                return
            result = client.get_team_projects(args.id)
            print(json.dumps(result, indent=2))
        elif args.action == "get-project-files":
            if not args.id or not args.id2:
                print("Error: team_id and project_id are required.")
                return
            result = client.get_project_files(args.id, args.id2)
            print(json.dumps(result, indent=2))
        elif args.action == "export":
            if not args.id:
                print("Error: file_key is required.")
                return
            if not args.ids:
                print("Error: --ids is required.")
                return
            
            # 1. Get Image URL
            images_data = client.get_image(args.id, args.ids, args.format, args.scale)
            # print(f"DEBUG: {json.dumps(images_data)}") 
            if "err" in images_data and images_data["err"]:
                print(f"Error getting image URL: {images_data['err']}")
                return

            images = images_data.get("images", {})
            
            # 2. Download Images
            for layer_id, image_url in images.items():
                if not image_url:
                    print(f"No image URL for layer {layer_id}")
                    continue
                
                print(f"Downloading {layer_id} from {image_url}...")
                
                # Sanitize layer_id for filename
                safe_id = layer_id.replace(":", "_")
                filename = f"figma_export_{safe_id}.{args.format}"
                
                try:
                    with urllib.request.urlopen(image_url) as response:
                        with open(filename, "wb") as f:
                            f.write(response.read())
                    print(f"Saved to {filename}")
                except Exception as e:
                    print(f"Failed to download {image_url}: {e}")

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
