import Foundation
import FluidAudio
import FluidAudioTTS
import Hummingbird
import NIOCore

// ============ TTS Service ============

actor TTSService {
    private var manager: KokoroTtsManager?
    private let voice: String
    
    init(voice: String) {
        self.voice = voice
    }
    
    func initialize() async throws {
        let mgr = KokoroTtsManager(defaultVoice: voice)
        try await mgr.initialize(preloadVoices: [voice])
        self.manager = mgr
    }
    
    func synthesize(text: String, speed: Float = 1.0, deEss: Bool = true) async throws -> Data {
        guard let mgr = manager else {
            throw VoiceError.notInitialized
        }
        return try await mgr.synthesize(text: text, voice: voice, voiceSpeed: speed, deEss: deEss)
    }
}

// ============ STT Service ============

actor STTService {
    private var asrManager: AsrManager?
    private var models: AsrModels?
    
    func initialize() async throws {
        models = try await AsrModels.downloadAndLoad(version: .v3)
        let manager = AsrManager(config: .default)
        try await manager.initialize(models: models!)
        self.asrManager = manager
    }
    
    func transcribe(audioData: Data) async throws -> String {
        guard let manager = asrManager else {
            throw VoiceError.notInitialized
        }
        
        // Write to temp file (AsrManager needs a file URL for non-streaming)
        let tempURL = FileManager.default.temporaryDirectory.appendingPathComponent("stt_\(UUID().uuidString).wav")
        try audioData.write(to: tempURL)
        defer { try? FileManager.default.removeItem(at: tempURL) }
        
        let result = try await manager.transcribe(tempURL)
        return result.text
    }
}

// ============ Errors ============

enum VoiceError: Error {
    case notInitialized
    case invalidAudio
}

// ============ Request Types ============

struct SynthesizeRequest: Codable {
    let text: String
    let speed: Float?
    let deEss: Bool?
}

// ============ Main ============

@main
struct StellaVoice {
    static func main() async throws {
        print("🚀 StellaVoice starting (TTS + STT)...")
        
        // Initialize TTS
        print("📦 Loading TTS model (Kokoro af_sky)...")
        let ttsStart = Date()
        let tts = TTSService(voice: "af_sky")
        try await tts.initialize()
        print("✅ TTS loaded in \(String(format: "%.2f", Date().timeIntervalSince(ttsStart)))s")
        
        // Initialize STT
        print("📦 Loading STT model (Parakeet v3)...")
        let sttStart = Date()
        let stt = STTService()
        try await stt.initialize()
        print("✅ STT loaded in \(String(format: "%.2f", Date().timeIntervalSince(sttStart)))s")
        
        // Create HTTP server
        let router = Router()
        
        router.get("/health") { _, _ in
            return "ok"
        }
        
        // ========== TTS Endpoints ==========
        
        router.post("/synthesize") { request, context in
            let body = try await request.body.collect(upTo: 1024 * 1024)
            let text = String(buffer: body)
            guard !text.isEmpty else {
                return Response(status: .badRequest)
            }
            
            let speed = request.uri.queryParameters.get("speed").flatMap { Float($0) } ?? 1.0
            let deEss = request.uri.queryParameters.get("deess").map { $0 != "false" } ?? true
            
            let start = Date()
            let audio = try await tts.synthesize(text: text, speed: speed, deEss: deEss)
            let elapsed = Date().timeIntervalSince(start)
            
            print("🎤 TTS: \(text.count) chars in \(String(format: "%.3f", elapsed))s")
            
            return Response(
                status: .ok,
                headers: [.contentType: "audio/wav"],
                body: .init(byteBuffer: ByteBuffer(data: audio))
            )
        }
        
        router.post("/synthesize/json") { request, context in
            let body = try await request.body.collect(upTo: 1024 * 1024)
            let decoder = JSONDecoder()
            guard let req = try? decoder.decode(SynthesizeRequest.self, from: body) else {
                return Response(status: .badRequest)
            }
            
            let start = Date()
            let audio = try await tts.synthesize(text: req.text, speed: req.speed ?? 1.0, deEss: req.deEss ?? true)
            let elapsed = Date().timeIntervalSince(start)
            
            print("🎤 TTS: \(req.text.count) chars in \(String(format: "%.3f", elapsed))s")
            
            return Response(
                status: .ok,
                headers: [.contentType: "audio/wav"],
                body: .init(byteBuffer: ByteBuffer(data: audio))
            )
        }
        
        // ========== STT Endpoints ==========
        
        router.post("/transcribe") { request, context in
            let body = try await request.body.collect(upTo: 10 * 1024 * 1024)  // 10MB max
            let audioData = Data(buffer: body)
            
            guard !audioData.isEmpty else {
                return Response(status: .badRequest)
            }
            
            let start = Date()
            let text = try await stt.transcribe(audioData: audioData)
            let elapsed = Date().timeIntervalSince(start)
            
            print("👂 STT: \(String(format: "%.3f", elapsed))s -> \"\(text.prefix(50))...\"")
            
            // Return JSON with transcript
            let response = ["text": text]
            let jsonData = try JSONEncoder().encode(response)
            
            return Response(
                status: .ok,
                headers: [.contentType: "application/json"],
                body: .init(byteBuffer: ByteBuffer(data: jsonData))
            )
        }
        
        let app = Application(
            router: router,
            configuration: .init(address: .hostname("127.0.0.1", port: 18790))
        )
        
        print("🎧 StellaVoice listening on http://127.0.0.1:18790")
        print("   TTS:")
        print("     POST /synthesize         - text body -> WAV")
        print("     POST /synthesize/json    - {text, speed?, deEss?} -> WAV")
        print("   STT:")
        print("     POST /transcribe         - WAV body -> {text}")
        print("   GET  /health               - health check")
        
        try await app.run()
    }
}
