#!/usr/bin/env swift
//
// image_tagger.swift - Comprehensive image tagging using Vision framework
// Usage: swift image_tagger.swift <image_path>
// Output: JSON with all detected elements
//

import Foundation
import Vision
import AppKit

// MARK: - Data Structures

struct ImageTags: Codable {
    let imagePath: String
    let timestamp: String
    let dimensions: ImageSize
    let faces: [FaceInfo]
    let objects: [ObjectInfo]
    let text: [TextInfo]
    let labels: [LabelInfo]
    let barcodes: [BarcodeInfo]
    let bodies: [BodyInfo]
    let hands: [HandInfo]
    let saliency: SaliencyInfo?
    let error: String?
}

struct ImageSize: Codable {
    let width: Int
    let height: Int
}

struct FaceInfo: Codable {
    let bbox: BoundingBox
    let confidence: Double
    let roll: Double?
    let yaw: Double?
    let pitch: Double?
    let landmarks: [String: [Double]]?
}

struct BoundingBox: Codable {
    let x: Double
    let y: Double
    let width: Double
    let height: Double
}

struct ObjectInfo: Codable {
    let label: String
    let confidence: Double
    let bbox: BoundingBox
}

struct TextInfo: Codable {
    let text: String
    let confidence: Double
    let bbox: BoundingBox
}

struct LabelInfo: Codable {
    let label: String
    let confidence: Double
}

struct BarcodeInfo: Codable {
    let payload: String
    let symbology: String
    let bbox: BoundingBox
}

struct BodyInfo: Codable {
    let joints: [String: JointInfo]
    let confidence: Double
}

struct JointInfo: Codable {
    let x: Double
    let y: Double
    let confidence: Double
}

struct HandInfo: Codable {
    let chirality: String  // left or right
    let joints: [String: JointInfo]
    let confidence: Double
}

struct SaliencyInfo: Codable {
    let attentionBased: [BoundingBox]
    let objectnessBased: [BoundingBox]
}

// MARK: - Main

func main() {
    guard CommandLine.arguments.count > 1 else {
        let error = ImageTags(
            imagePath: "", timestamp: ISO8601DateFormatter().string(from: Date()),
            dimensions: ImageSize(width: 0, height: 0),
            faces: [], objects: [], text: [], labels: [], barcodes: [], bodies: [], hands: [],
            saliency: nil, error: "Usage: image_tagger <image_path>"
        )
        printJSON(error)
        exit(1)
    }
    
    let imagePath = CommandLine.arguments[1]
    let result = analyzeImage(path: imagePath)
    printJSON(result)
}

func printJSON(_ value: ImageTags) {
    let encoder = JSONEncoder()
    encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
    if let data = try? encoder.encode(value), let str = String(data: data, encoding: .utf8) {
        print(str)
    }
}

func analyzeImage(path: String) -> ImageTags {
    let timestamp = ISO8601DateFormatter().string(from: Date())
    
    guard let image = NSImage(contentsOfFile: path),
          let cgImage = image.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
        return ImageTags(
            imagePath: path, timestamp: timestamp,
            dimensions: ImageSize(width: 0, height: 0),
            faces: [], objects: [], text: [], labels: [], barcodes: [], bodies: [], hands: [],
            saliency: nil, error: "Failed to load image"
        )
    }
    
    let dimensions = ImageSize(width: cgImage.width, height: cgImage.height)
    
    var faces: [FaceInfo] = []
    var objects: [ObjectInfo] = []
    var textResults: [TextInfo] = []
    var labels: [LabelInfo] = []
    var barcodes: [BarcodeInfo] = []
    var bodies: [BodyInfo] = []
    var hands: [HandInfo] = []
    var saliency: SaliencyInfo? = nil
    
    let group = DispatchGroup()
    let queue = DispatchQueue(label: "vision", attributes: .concurrent)
    
    // Face Detection with landmarks
    group.enter()
    queue.async {
        faces = detectFaces(cgImage: cgImage)
        group.leave()
    }
    
    // Text Recognition
    group.enter()
    queue.async {
        textResults = recognizeText(cgImage: cgImage)
        group.leave()
    }
    
    // Image Classification (labels)
    group.enter()
    queue.async {
        labels = classifyImage(cgImage: cgImage)
        group.leave()
    }
    
    // Barcode Detection
    group.enter()
    queue.async {
        barcodes = detectBarcodes(cgImage: cgImage)
        group.leave()
    }
    
    // Body Pose Detection
    group.enter()
    queue.async {
        bodies = detectBodies(cgImage: cgImage)
        group.leave()
    }
    
    // Hand Pose Detection
    group.enter()
    queue.async {
        hands = detectHands(cgImage: cgImage)
        group.leave()
    }
    
    // Saliency Detection
    group.enter()
    queue.async {
        saliency = detectSaliency(cgImage: cgImage)
        group.leave()
    }
    
    // Rectangle/Object Detection
    group.enter()
    queue.async {
        objects = detectRectangles(cgImage: cgImage)
        group.leave()
    }
    
    group.wait()
    
    return ImageTags(
        imagePath: path, timestamp: timestamp, dimensions: dimensions,
        faces: faces, objects: objects, text: textResults, labels: labels,
        barcodes: barcodes, bodies: bodies, hands: hands,
        saliency: saliency, error: nil
    )
}

// MARK: - Detection Functions

func detectFaces(cgImage: CGImage) -> [FaceInfo] {
    var results: [FaceInfo] = []
    let request = VNDetectFaceLandmarksRequest { req, _ in
        guard let observations = req.results as? [VNFaceObservation] else { return }
        for face in observations {
            let bbox = BoundingBox(
                x: face.boundingBox.origin.x,
                y: face.boundingBox.origin.y,
                width: face.boundingBox.width,
                height: face.boundingBox.height
            )
            
            var landmarks: [String: [Double]]? = nil
            if let lm = face.landmarks {
                var lmDict: [String: [Double]] = [:]
                if let leftEye = lm.leftEye?.normalizedPoints {
                    lmDict["leftEye"] = leftEye.flatMap { [$0.x, $0.y] }
                }
                if let rightEye = lm.rightEye?.normalizedPoints {
                    lmDict["rightEye"] = rightEye.flatMap { [$0.x, $0.y] }
                }
                if let nose = lm.nose?.normalizedPoints {
                    lmDict["nose"] = nose.flatMap { [$0.x, $0.y] }
                }
                if let outerLips = lm.outerLips?.normalizedPoints {
                    lmDict["outerLips"] = outerLips.flatMap { [$0.x, $0.y] }
                }
                if !lmDict.isEmpty { landmarks = lmDict }
            }
            
            results.append(FaceInfo(
                bbox: bbox,
                confidence: Double(face.confidence),
                roll: face.roll?.doubleValue.toDegrees,
                yaw: face.yaw?.doubleValue.toDegrees,
                pitch: face.pitch?.doubleValue.toDegrees,
                landmarks: landmarks
            ))
        }
    }
    try? VNImageRequestHandler(cgImage: cgImage).perform([request])
    return results
}

func recognizeText(cgImage: CGImage) -> [TextInfo] {
    var results: [TextInfo] = []
    let request = VNRecognizeTextRequest { req, _ in
        guard let observations = req.results as? [VNRecognizedTextObservation] else { return }
        for obs in observations {
            if let candidate = obs.topCandidates(1).first {
                results.append(TextInfo(
                    text: candidate.string,
                    confidence: Double(candidate.confidence),
                    bbox: BoundingBox(
                        x: obs.boundingBox.origin.x,
                        y: obs.boundingBox.origin.y,
                        width: obs.boundingBox.width,
                        height: obs.boundingBox.height
                    )
                ))
            }
        }
    }
    request.recognitionLevel = .accurate
    try? VNImageRequestHandler(cgImage: cgImage).perform([request])
    return results
}

func classifyImage(cgImage: CGImage) -> [LabelInfo] {
    var results: [LabelInfo] = []
    let request = VNClassifyImageRequest { req, _ in
        guard let observations = req.results as? [VNClassificationObservation] else { return }
        // Top 10 labels with confidence > 0.1
        for obs in observations.prefix(10) where obs.confidence > 0.1 {
            results.append(LabelInfo(
                label: obs.identifier,
                confidence: Double(obs.confidence)
            ))
        }
    }
    try? VNImageRequestHandler(cgImage: cgImage).perform([request])
    return results
}

func detectBarcodes(cgImage: CGImage) -> [BarcodeInfo] {
    var results: [BarcodeInfo] = []
    let request = VNDetectBarcodesRequest { req, _ in
        guard let observations = req.results as? [VNBarcodeObservation] else { return }
        for obs in observations {
            results.append(BarcodeInfo(
                payload: obs.payloadStringValue ?? "",
                symbology: obs.symbology.rawValue,
                bbox: BoundingBox(
                    x: obs.boundingBox.origin.x,
                    y: obs.boundingBox.origin.y,
                    width: obs.boundingBox.width,
                    height: obs.boundingBox.height
                )
            ))
        }
    }
    try? VNImageRequestHandler(cgImage: cgImage).perform([request])
    return results
}

func detectBodies(cgImage: CGImage) -> [BodyInfo] {
    var results: [BodyInfo] = []
    if #available(macOS 12.0, *) {
        let request = VNDetectHumanBodyPoseRequest { req, _ in
            guard let observations = req.results as? [VNHumanBodyPoseObservation] else { return }
            for obs in observations {
                var joints: [String: JointInfo] = [:]
                if let points = try? obs.recognizedPoints(.all) {
                    for (key, point) in points where point.confidence > 0.1 {
                        joints[key.rawValue.rawValue] = JointInfo(
                            x: point.location.x,
                            y: point.location.y,
                            confidence: Double(point.confidence)
                        )
                    }
                }
                results.append(BodyInfo(joints: joints, confidence: Double(obs.confidence)))
            }
        }
        try? VNImageRequestHandler(cgImage: cgImage).perform([request])
    }
    return results
}

func detectHands(cgImage: CGImage) -> [HandInfo] {
    var results: [HandInfo] = []
    if #available(macOS 12.0, *) {
        let request = VNDetectHumanHandPoseRequest { req, _ in
            guard let observations = req.results as? [VNHumanHandPoseObservation] else { return }
            for obs in observations {
                var joints: [String: JointInfo] = [:]
                if let points = try? obs.recognizedPoints(.all) {
                    for (key, point) in points where point.confidence > 0.1 {
                        joints[key.rawValue.rawValue] = JointInfo(
                            x: point.location.x,
                            y: point.location.y,
                            confidence: Double(point.confidence)
                        )
                    }
                }
                let chirality = obs.chirality == .left ? "left" : (obs.chirality == .right ? "right" : "unknown")
                results.append(HandInfo(chirality: chirality, joints: joints, confidence: Double(obs.confidence)))
            }
        }
        request.maximumHandCount = 2
        try? VNImageRequestHandler(cgImage: cgImage).perform([request])
    }
    return results
}

func detectSaliency(cgImage: CGImage) -> SaliencyInfo {
    var attention: [BoundingBox] = []
    var objectness: [BoundingBox] = []
    
    let attentionReq = VNGenerateAttentionBasedSaliencyImageRequest { req, _ in
        if let obs = req.results?.first as? VNSaliencyImageObservation,
           let objects = obs.salientObjects {
            attention = objects.map { BoundingBox(x: $0.boundingBox.origin.x, y: $0.boundingBox.origin.y, width: $0.boundingBox.width, height: $0.boundingBox.height) }
        }
    }
    
    let objectnessReq = VNGenerateObjectnessBasedSaliencyImageRequest { req, _ in
        if let obs = req.results?.first as? VNSaliencyImageObservation,
           let objects = obs.salientObjects {
            objectness = objects.map { BoundingBox(x: $0.boundingBox.origin.x, y: $0.boundingBox.origin.y, width: $0.boundingBox.width, height: $0.boundingBox.height) }
        }
    }
    
    try? VNImageRequestHandler(cgImage: cgImage).perform([attentionReq, objectnessReq])
    return SaliencyInfo(attentionBased: attention, objectnessBased: objectness)
}

func detectRectangles(cgImage: CGImage) -> [ObjectInfo] {
    var results: [ObjectInfo] = []
    let request = VNDetectRectanglesRequest { req, _ in
        guard let observations = req.results as? [VNRectangleObservation] else { return }
        for (i, obs) in observations.enumerated() {
            results.append(ObjectInfo(
                label: "rectangle_\(i)",
                confidence: Double(obs.confidence),
                bbox: BoundingBox(
                    x: obs.boundingBox.origin.x,
                    y: obs.boundingBox.origin.y,
                    width: obs.boundingBox.width,
                    height: obs.boundingBox.height
                )
            ))
        }
    }
    request.maximumObservations = 10
    try? VNImageRequestHandler(cgImage: cgImage).perform([request])
    return results
}

// MARK: - Helpers

extension Double {
    var toDegrees: Double { self * 180 / .pi }
}

main()
