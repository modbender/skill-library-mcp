import argparse
from tiktok_content_gen import generate


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('topic')
    parser.add_argument('--out', default='images')
    parser.add_argument('--slides', type=int, default=6)
    parser.add_argument('--persona', default=None)
    args = parser.parse_args()
    result = generate(args.topic, out_dir=args.out, slides=args.slides, persona=args.persona)
    print('Generated:', result)


if __name__ == '__main__':
    main()
