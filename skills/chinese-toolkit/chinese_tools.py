            print("OCR识别结果:", result)
            
        elif args.command == 'pinyin':
            result = toolkit.to_pinyin(args.text, args.style)
            print("拼音结果:", result)
            
        elif args.command == 'stats':
            stats = toolkit.get_text_statistics(args.text)
            print("文本统计:")
            for key, value in stats.items():
                print(f"  {key}: {value}")
            
        else:
            parser.print_help()


if __name__ == '__main__':
    main()