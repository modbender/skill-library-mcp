import Foundation
import Vision
import AppKit

func run() {
    let tempPath = "/tmp/ocr_test_v6.png"
    
    // 1. 截图
    let process = Process()
    process.executableURL = URL(fileURLWithPath: "/usr/sbin/screencapture")
    process.arguments = ["-x", tempPath]
    try? process.run()
    process.waitUntilExit()

    guard let imageData = try? Data(contentsOf: URL(fileURLWithPath: tempPath)),
          let image = NSImage(data: imageData),
          let cgImage = image.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
        print("❌ 无法读取截图，请检查权限。")
        return
    }

    // 2. OCR 识别
    let request = VNRecognizeTextRequest()
    request.recognitionLanguages = ["zh-Hans", "en-US"]
    request.recognitionLevel = .accurate
    
    let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
    do {
        try handler.perform([request])
        guard let results = request.results else { 
            print("❌ 无结果。")
            return 
        }
        
        print("\n--- 🎯 本地 OCR 识别成功！(前 30 条) ---")
        if results.isEmpty {
            print("(未发现任何文字，请确保 Telegram 窗口未被遮挡)")
        } else {
            for (i, res) in results.prefix(30).enumerated() {
                if let top = res.topCandidates(1).first {
                    // 计算中心坐标
                    let box = res.boundingBox
                    let x = Int(box.midX * image.size.width)
                    let y = Int((1 - box.midY) * image.size.height)
                    print("[\(i)] 内容: \"\(top.string)\" | 坐标: [\(x), \(y)]")
                }
            }
        }
        print("------------------------------------------\n")
    } catch {
        print("❌ 识别出错: \(error)")
    }
}

run()
