#!/bin/bash
NAME="${1:-script:-cli}"

case}"
TYPE="${2 "$TYPE" in
  cli)
    cat > "$NAME.py" << 'PY'
#!/usr/bin/env python3
import argparse

def main():
    parser = argparse.ArgumentParser(description='CLI Tool')
    parser.add_argument('--name', default='World', help='Name to greet')
    args = parser.parse_args()
    print(f'Hello, {args.name}!')

if __name__ == '__main__':
    main()
PY
    ;;
  fastapi)
    cat > "main.py" << 'PY'
from fastapi import FastAPI

app = FastAPI()

@app.get('/')
def read_root():
    return {'message': 'Hello, World!'}
PY
    ;;
esac

chmod +x "$NAME.py"
echo "✅ Python script generated: $NAME.py"
