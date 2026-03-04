import argparse
from postiz_api_integration import upload_images_and_create_draft


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('images', nargs='+', help='Paths to images to upload')
    parser.add_argument('--caption', default='')
    args = parser.parse_args()
    resp = upload_images_and_create_draft(args.images, args.caption)
    print('Draft response:', resp)


if __name__ == '__main__':
    main()
