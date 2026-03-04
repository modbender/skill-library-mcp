import yaml
import os

def create_config_template(path):
    config = {
        'developer_token': 'INSERT_DEVELOPER_TOKEN_HERE',
        'client_id': 'INSERT_CLIENT_ID_HERE',
        'client_secret': 'INSERT_CLIENT_SECRET_HERE',
        'refresh_token': 'INSERT_REFRESH_TOKEN_HERE',
        'use_proto_plus': True
    }
    with open(path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    print(f"Template created at {path}")

if __name__ == '__main__':
    target_path = os.path.expanduser('~/.google-ads.yaml')
    if not os.path.exists(target_path):
        create_config_template(target_path)
    else:
        print(f"Config already exists at {target_path}")
