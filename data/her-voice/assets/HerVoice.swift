import Cocoa
import AVFoundation

enum AnimMode: String {
    case classic
    case v2
}

var animMode: AnimMode = .v2

class HerVoiceView: NSView {
    static let segCount = 18
    static let barWidths: [CGFloat] = [42, 46, 42]
    static let segH: CGFloat = 6
    static let segGap: CGFloat = 3
    static let barGap: CGFloat = 8
    static let bgCornerRadius: CGFloat = 16
    static let bgPadding: CGFloat = 14

    static let segStride: CGFloat = segH + segGap
    static let barH: CGFloat = CGFloat(segCount) * segStride - segGap
    static let totalW: CGFloat = barWidths.reduce(0, +) + barGap * CGFloat(barWidths.count - 1)
    static let bgW: CGFloat = totalW + bgPadding * 2

    static let progressH: CGFloat = 2
    static let progressGap: CGFloat = 6
    static let fullBgH: CGFloat = barH + bgPadding * 2 + progressGap + progressH

    static let bgColor = CGColor(red: 0, green: 0, blue: 0, alpha: 1.0)
    static let unlitColor = CGColor(red: 0.06, green: 0.005, blue: 0.002, alpha: 1.0)
    static let progressBgColor = CGColor(red: 0.12, green: 0.01, blue: 0.005, alpha: 1.0)
    static let progressFgColor = CGColor(red: 0.65, green: 0.04, blue: 0.02, alpha: 1.0)

    var levels: [CGFloat] = [0, 0, 0]
    var progress: CGFloat = 0

    // Callback for drag-and-drop
    var onFileDrop: ((URL) -> Void)?

    override init(frame: NSRect) {
        super.init(frame: frame)
        self.wantsLayer = true
        self.layer?.backgroundColor = CGColor.clear
        registerForDraggedTypes([.fileURL])
    }
    required init?(coder: NSCoder) { fatalError() }

    // MARK: - Drag and Drop

    private static let audioExtensions: Set<String> = ["wav", "mp3", "aiff", "aif", "m4a", "caf", "aac"]

    override func draggingEntered(_ sender: NSDraggingInfo) -> NSDragOperation {
        guard let urls = fileURLs(from: sender),
              urls.contains(where: { Self.audioExtensions.contains($0.pathExtension.lowercased()) }) else {
            return []
        }
        return .copy
    }

    override func performDragOperation(_ sender: NSDraggingInfo) -> Bool {
        guard let urls = fileURLs(from: sender) else { return false }
        if let audioURL = urls.first(where: { Self.audioExtensions.contains($0.pathExtension.lowercased()) }) {
            onFileDrop?(audioURL)
            return true
        }
        return false
    }

    private func fileURLs(from info: NSDraggingInfo) -> [URL]? {
        return info.draggingPasteboard.readObjects(forClasses: [NSURL.self], options: [
            .urlReadingFileURLsOnly: true
        ]) as? [URL]
    }

    override func draw(_ dirtyRect: NSRect) {
        guard let ctx = NSGraphicsContext.current?.cgContext else { return }
        ctx.clear(dirtyRect)

        let segH = HerVoiceView.segH
        let segStride = HerVoiceView.segStride
        let center = HerVoiceView.segCount / 2

        let bgX = (bounds.width - HerVoiceView.bgW) / 2
        let bgY = (bounds.height - HerVoiceView.fullBgH) / 2
        let bgRect = CGRect(x: bgX, y: bgY, width: HerVoiceView.bgW, height: HerVoiceView.fullBgH)
        let bgPath = CGPath(roundedRect: bgRect, cornerWidth: HerVoiceView.bgCornerRadius, cornerHeight: HerVoiceView.bgCornerRadius, transform: nil)
        ctx.setFillColor(HerVoiceView.bgColor)
        ctx.addPath(bgPath)
        ctx.fillPath()

        var barX = (bounds.width - HerVoiceView.totalW) / 2
        let barY = bgY + HerVoiceView.bgPadding + HerVoiceView.progressGap + HerVoiceView.progressH

        for (i, width) in HerVoiceView.barWidths.enumerated() {
            let spread = Int(levels[i] * CGFloat(center))

            for s in 0..<HerVoiceView.segCount {
                let segY = barY + CGFloat(s) * segStride
                let segRect = CGRect(x: barX, y: segY, width: width, height: segH)
                let distFromCenter = abs(s - center)

                if spread > 0 && distFromCenter <= spread {
                    if animMode == .v2 {
                        let ratio: CGFloat = CGFloat(distFromCenter) / CGFloat(spread)
                        let r: CGFloat
                        let g: CGFloat
                        let b: CGFloat
                        if ratio <= 0.55 {
                            r = 0.90; g = 0.0; b = 0.0
                        } else if ratio <= 0.80 {
                            r = 0.45; g = 0.0; b = 0.0
                        } else {
                            r = 0.18; g = 0.0; b = 0.0
                        }
                        ctx.setFillColor(CGColor(red: r, green: g, blue: b, alpha: 1.0))
                    } else {
                        let normalizedDist = center > 0 ? CGFloat(distFromCenter) / CGFloat(center) : 0
                        let fade = pow(1.0 - normalizedDist, 3.5)
                        ctx.setFillColor(CGColor(red: 0.80 * fade + 0.18, green: 0.03 * fade, blue: 0.01 * fade, alpha: 1.0))
                    }
                } else {
                    ctx.setFillColor(HerVoiceView.unlitColor)
                }

                ctx.fill(segRect)
            }
            barX += width + HerVoiceView.barGap
        }

        // Progress bar
        let progX = bgX + HerVoiceView.bgPadding
        let progY = bgY + HerVoiceView.bgPadding
        let progW = HerVoiceView.totalW
        let progRect = CGRect(x: progX, y: progY, width: progW, height: HerVoiceView.progressH)
        ctx.setFillColor(HerVoiceView.progressBgColor)
        ctx.fill(progRect)

        if progress > 0 {
            let fillRect = CGRect(x: progX, y: progY, width: progW * progress, height: HerVoiceView.progressH)
            ctx.setFillColor(HerVoiceView.progressFgColor)
            ctx.fill(fillRect)
        }
    }
}

// ===== Streaming Audio Engine =====

class StreamingAudioEngine {
    let engine = AVAudioEngine()
    let playerNode = AVAudioPlayerNode()
    let format: AVAudioFormat
    let samplesPerChunk: Int

    var currentAmplitude: Float = 0
    var stdinEOF = false
    var scheduledBuffers: Int = 0
    var completedBuffers: Int = 0
    let lock = NSLock()

    var isFinished: Bool {
        lock.lock()
        let done = stdinEOF && completedBuffers >= scheduledBuffers
        lock.unlock()
        return done
    }

    init(sampleRate: Double = 24000, channels: UInt32 = 1) {
        self.format = AVAudioFormat(commonFormat: .pcmFormatFloat32, sampleRate: sampleRate, channels: channels, interleaved: false)!
        self.samplesPerChunk = Int(sampleRate * 0.2)

        engine.attach(playerNode)
        engine.connect(playerNode, to: engine.mainMixerNode, format: format)

        let tapBufferSize = AVAudioFrameCount(sampleRate / 60.0)
        playerNode.installTap(onBus: 0, bufferSize: tapBufferSize, format: format) { [weak self] buffer, _ in
            guard let self = self else { return }
            let ptr = buffer.floatChannelData![0]
            let count = Int(buffer.frameLength)
            var sum: Float = 0
            for i in 0..<count {
                sum += ptr[i] * ptr[i]
            }
            let rms = sqrt(sum / max(Float(count), 1))
            self.currentAmplitude = rms
        }
    }

    func start() {
        do {
            try engine.start()
            playerNode.play()
        } catch {
            fputs("Error starting audio engine: \(error)\n", stderr)
            exit(1)
        }
    }

    func startReadingStdin() {
        DispatchQueue.global(qos: .userInitiated).async { [self] in
            let handle = FileHandle.standardInput
            let bytesPerSample = 4
            let chunkBytes = samplesPerChunk * bytesPerSample

            while true {
                let data = handle.readData(ofLength: chunkBytes)
                if data.isEmpty {
                    lock.lock()
                    stdinEOF = true
                    lock.unlock()
                    break
                }

                let sampleCount = data.count / bytesPerSample
                guard sampleCount > 0 else { continue }

                guard let buffer = AVAudioPCMBuffer(pcmFormat: format, frameCapacity: AVAudioFrameCount(sampleCount)) else { continue }
                buffer.frameLength = AVAudioFrameCount(sampleCount)

                data.withUnsafeBytes { rawBuf in
                    let src = rawBuf.bindMemory(to: Float.self)
                    let dst = buffer.floatChannelData![0]
                    for i in 0..<sampleCount {
                        dst[i] = src[i]
                    }
                }

                lock.lock()
                scheduledBuffers += 1
                lock.unlock()

                playerNode.scheduleBuffer(buffer) { [self] in
                    lock.lock()
                    completedBuffers += 1
                    lock.unlock()
                }
            }
        }
    }

    func stop() {
        playerNode.removeTap(onBus: 0)
        playerNode.stop()
        engine.stop()
    }
}

// ===== MAIN =====

var audioFile: String?
var simulate = false
var streamMode = false
var persistMode = false
var streamSampleRate: Double = 24000
var streamChannels: UInt32 = 1
var i = 1
while i < CommandLine.arguments.count {
    switch CommandLine.arguments[i] {
    case "--help", "-h":
        fputs("Usage: her-voice-viz [OPTIONS] [audio_file]\n", stderr)
        fputs("  --audio <file>     Audio file to play\n", stderr)
        fputs("  --stream           Read raw PCM float32 from stdin\n", stderr)
        fputs("  --sample-rate <hz> Sample rate for stream mode (default: 24000)\n", stderr)
        fputs("  --channels <n>     Channel count for stream mode (default: 1)\n", stderr)
        fputs("  --mode <mode>      Animation mode: v2 (default), classic\n", stderr)
        fputs("  --demo             Run with simulated audio\n", stderr)
        fputs("  --persist          Stay open after playback ends (idle breathing)\n", stderr)
        fputs("  ESC=quit  SPACE=pause  LEFT/RIGHT=seek 5s  Cmd+V=paste-to-speak\n", stderr)
        exit(0)
    case "--audio" where i + 1 < CommandLine.arguments.count:
        i += 1
        audioFile = CommandLine.arguments[i]
    case "--stream":
        streamMode = true
    case "--persist":
        persistMode = true
    case "--sample-rate" where i + 1 < CommandLine.arguments.count:
        i += 1
        streamSampleRate = Double(CommandLine.arguments[i]) ?? 24000
    case "--channels" where i + 1 < CommandLine.arguments.count:
        i += 1
        streamChannels = UInt32(CommandLine.arguments[i]) ?? 1
    case "--demo", "--simulate":
        simulate = true
    case "--mode" where i + 1 < CommandLine.arguments.count:
        i += 1
        if let mode = AnimMode(rawValue: CommandLine.arguments[i]) {
            animMode = mode
        } else {
            fputs("Unknown mode: \(CommandLine.arguments[i]). Use 'v2' or 'classic'.\n", stderr)
            exit(1)
        }
    default:
        if audioFile == nil && !CommandLine.arguments[i].hasPrefix("-") {
            audioFile = CommandLine.arguments[i]
        }
    }
    i += 1
}

let levelMultiplier: CGFloat = animMode == .v2 ? 1.6 : 2.2

let app = NSApplication.shared
app.setActivationPolicy(.regular)

guard let screen = NSScreen.main else { exit(1) }
let winW: CGFloat = HerVoiceView.bgW + 4
let winH: CGFloat = HerVoiceView.fullBgH + 4

// Restore saved position or use default (top center)
let defaults = UserDefaults.standard
let savedX = defaults.double(forKey: "herVoiceWindowX")
let savedY = defaults.double(forKey: "herVoiceWindowY")
let hasSavedPosition = defaults.bool(forKey: "herVoiceHasPosition")

let initialRect: NSRect
if hasSavedPosition {
    initialRect = NSRect(x: savedX, y: savedY, width: winW, height: winH)
} else {
    initialRect = NSRect(x: (screen.frame.width - winW)/2, y: screen.frame.height - winH - 5, width: winW, height: winH)
}

class KeyableWindow: NSWindow {
    override var canBecomeKey: Bool { true }
    override var canBecomeMain: Bool { true }
}

let win = KeyableWindow(
    contentRect: initialRect,
    styleMask: [.borderless], backing: .buffered, defer: false
)
win.isOpaque = false
win.backgroundColor = .clear
win.level = .floating
win.hasShadow = false
win.isMovableByWindowBackground = true
win.collectionBehavior = [.canJoinAllSpaces, .fullScreenAuxiliary]

let voiceView = HerVoiceView(frame: NSRect(x: 0, y: 0, width: winW, height: winH))
win.contentView = voiceView
win.makeKeyAndOrderFront(nil)

var player: AVAudioPlayer?
var isPaused = false
var hasFinished = false
var isIdle = false  // persist mode: currently idle, showing breathing animation
var streamEngine: StreamingAudioEngine?
var breathPhase: Double = 0  // for idle breathing animation
var flashTimer: Double = 0   // for paste visual feedback

// Helper: load and play an audio file with visualization
func playAudioFile(_ url: URL) {
    // Stop any current playback
    player?.stop()
    streamEngine?.stop()
    streamEngine = nil

    do {
        let p = try AVAudioPlayer(contentsOf: url)
        p.isMeteringEnabled = true
        p.prepareToPlay()
        p.play()
        player = p
        isPaused = false
        hasFinished = false
        isIdle = false
    } catch {
        fputs("Error loading audio: \(error)\n", stderr)
    }
}

// Wire up drag-and-drop
voiceView.onFileDrop = { url in
    playAudioFile(url)
}

if streamMode {
    let engine = StreamingAudioEngine(sampleRate: streamSampleRate, channels: streamChannels)
    engine.start()
    engine.startReadingStdin()
    streamEngine = engine
} else if let file = audioFile {
    playAudioFile(URL(fileURLWithPath: file))
} else if !simulate && persistMode {
    // Launched with just --persist: start idle immediately
    isIdle = true
}

var smoothedLevel: Float = 0
var smoothedOuter: Float = 0
var pulsePhase: Double = 0

func enterIdleState() {
    hasFinished = true
    isIdle = true
    voiceView.levels = [0, 0, 0]
    voiceView.progress = 0
    breathPhase = 0
    voiceView.needsDisplay = true
}

func handlePlaybackFinished() {
    if persistMode {
        enterIdleState()
    } else {
        hasFinished = true
        voiceView.levels = [0, 0, 0]
        voiceView.needsDisplay = true
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) { NSApp.terminate(nil) }
    }
}

func updateAnimation(_ tmr: Timer) {
    // Flash feedback for paste (decays quickly)
    if flashTimer > 0 {
        flashTimer -= 1.0 / 60.0
        if flashTimer > 0 {
            let flash = CGFloat(min(1.0, flashTimer * 4.0))
            voiceView.levels = [flash * 0.6, flash, flash * 0.6]
            voiceView.progress = 0
            voiceView.needsDisplay = true
            return
        }
    }

    // Idle breathing animation (persist mode)
    if isIdle {
        voiceView.levels = [0, 0, 0]
        voiceView.progress = 0
        voiceView.needsDisplay = true
        return
    }

    var peak: Float = 0

    if let eng = streamEngine {
        let amp = eng.currentAmplitude
        let db: Float = amp > 0 ? 20.0 * log10(amp) : -60.0
        let linear: Float = max(0, (db + 55) / 55)
        peak = linear * linear

        pulsePhase += 1.0 / 30.0
        voiceView.progress = 1.0

        if eng.isFinished && !hasFinished {
            eng.stop()
            streamEngine = nil
            handlePlaybackFinished()
            return
        }
    } else if let p = player {
        if p.isPlaying {
            p.updateMeters()
            let db: Float = p.averagePower(forChannel: 0)
            let linear: Float = max(0, (db + 55) / 55)
            peak = linear * linear
        } else if !isPaused && !hasFinished {
            handlePlaybackFinished()
            return
        }
    } else if simulate {
        let t: Float = Float(CACurrentMediaTime())
        let e1: Float = sin(t * 2.8) * 0.35
        let e2: Float = sin(t * 1.3) * 0.3
        let e3: Float = sin(t * 4.7) * 0.15
        let envelope: Float = max(0, e1 + e2 + e3 + 0.3)
        let d1: Float = sin(t * 13) * 0.25
        let d2: Float = sin(t * 19) * 0.15
        let d3: Float = sin(t * 8) * 0.2
        let detail: Float = d1 + d2 + d3 + 0.5
        peak = envelope * detail / 3.0
        if t > 10 {
            simulate = false
            handlePlaybackFinished()
            return
        }
    }

    if animMode == .v2 {
        smoothedLevel = peak
    } else {
        smoothedLevel = smoothedLevel * 0.2 + peak * 0.8
    }
    let centerLevel: CGFloat = CGFloat(min(Float(1.0), smoothedLevel * Float(levelMultiplier)))

    voiceView.levels[1] = centerLevel
    if animMode == .v2 {
        smoothedOuter = smoothedOuter * 0.2 + peak * 0.8
        let outerBase: CGFloat = CGFloat(min(Float(1.0), smoothedOuter * Float(levelMultiplier)))
        let outerScale: CGFloat = 0.70 + 0.30 * outerBase * outerBase
        voiceView.levels[0] = outerBase * outerScale
        voiceView.levels[2] = outerBase * outerScale
    } else {
        let outerScale: CGFloat = 1.0 - centerLevel * 0.35
        voiceView.levels[0] = centerLevel * outerScale
        voiceView.levels[2] = centerLevel * outerScale
    }

    if let p = player {
        let dur: TimeInterval = p.duration
        if dur > 0 {
            voiceView.progress = CGFloat(p.currentTime / dur)
        }
    }

    voiceView.needsDisplay = true
}

let timer = Timer(timeInterval: 1.0/60.0, repeats: true, block: updateAnimation)
RunLoop.main.add(timer, forMode: .common)

// Stream text from TTS daemon into visualizer
func streamFromDaemon(text: String) {
    // Read config for voice/speed/socket if available
    let home = FileManager.default.homeDirectoryForCurrentUser.path
    var socketPath = home + "/.her-voice/tts.sock"
    var voice = "af_heart"
    var speed: Double = 1.05
    var lang = "a"
    let configPath = home + "/.her-voice/config.json"
    if let data = FileManager.default.contents(atPath: configPath),
       let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any] {
        if let v = json["voice"] as? String { voice = v }
        if let s = json["speed"] as? Double { speed = s }
        if let l = json["language"] as? String {
            // Mirrors LANG_MAP from scripts/config.py — keep in sync
            lang = ["en": "a", "en-us": "a", "en-gb": "b", "ja": "j", "zh": "z", "ko": "k"][l] ?? "a"
        }
        if let dp = json["daemon"] as? [String: Any], let sp = dp["socket_path"] as? String {
            socketPath = sp
        }
    }

    let fd = socket(AF_UNIX, SOCK_STREAM, 0)
    guard fd >= 0 else { return }

    var addr = sockaddr_un()
    addr.sun_family = sa_family_t(AF_UNIX)
    let maxSunPath = MemoryLayout.size(ofValue: addr.sun_path)
    guard socketPath.utf8.count < maxSunPath else {
        fputs("Socket path too long: \(socketPath)\n", stderr)
        close(fd)
        return
    }
    withUnsafeMutablePointer(to: &addr.sun_path) { ptr in
        socketPath.withCString { src in
            _ = strlcpy(UnsafeMutableRawPointer(ptr).assumingMemoryBound(to: CChar.self), src, maxSunPath)
        }
    }

    let connectResult = withUnsafePointer(to: &addr) { ptr in
        ptr.withMemoryRebound(to: sockaddr.self, capacity: 1) { sockPtr in
            Darwin.connect(fd, sockPtr, socklen_t(MemoryLayout<sockaddr_un>.size))
        }
    }
    guard connectResult == 0 else { close(fd); return }

    // Send request: 4-byte length + JSON
    let requestDict: [String: Any] = ["text": text, "voice": voice, "speed": speed, "lang": lang]
    guard let reqData = try? JSONSerialization.data(withJSONObject: requestDict) else { close(fd); return }
    var reqLen = UInt32(reqData.count).bigEndian
    _ = Darwin.send(fd, &reqLen, 4, 0)
    reqData.withUnsafeBytes { ptr in
        _ = Darwin.send(fd, ptr.baseAddress!, reqData.count, 0)
    }

    // Set up streaming engine on main thread
    DispatchQueue.main.sync {
        player?.stop()
        player = nil
        streamEngine?.stop()
        streamEngine = nil
        isIdle = false
        hasFinished = false

        let engine = StreamingAudioEngine(sampleRate: 24000, channels: 1)
        engine.start()
        streamEngine = engine
    }

    // Receive PCM chunks
    let maxTotalAudio = 500 * 1024 * 1024  // 500MB max total audio memory
    var totalReceived = 0
    while true {
        var headerBuf = [UInt8](repeating: 0, count: 4)
        var headerRead = 0
        while headerRead < 4 {
            let n = headerBuf.withUnsafeMutableBytes { ptr in
                Darwin.recv(fd, ptr.baseAddress! + headerRead, 4 - headerRead, 0)
            }
            if n <= 0 { close(fd); return }
            headerRead += n
        }

        let chunkLen = Int(UInt32(headerBuf[0]) << 24 | UInt32(headerBuf[1]) << 16 | UInt32(headerBuf[2]) << 8 | UInt32(headerBuf[3]))
        if chunkLen == 0 { break }  // End marker
        if chunkLen > 100 * 1024 * 1024 { close(fd); return }  // 100MB max chunk
        totalReceived += chunkLen
        if totalReceived > maxTotalAudio { close(fd); return }  // 500MB max total

        var chunkData = Data(count: chunkLen)
        var chunkRead = 0
        while chunkRead < chunkLen {
            let n = chunkData.withUnsafeMutableBytes { ptr in
                Darwin.recv(fd, ptr.baseAddress! + chunkRead, chunkLen - chunkRead, 0)
            }
            if n <= 0 { close(fd); return }
            chunkRead += n
        }

        // Feed PCM to streaming engine
        let sampleCount = chunkLen / 4
        guard sampleCount > 0, let eng = streamEngine else { continue }
        guard let buffer = AVAudioPCMBuffer(pcmFormat: eng.format, frameCapacity: AVAudioFrameCount(sampleCount)) else { continue }
        buffer.frameLength = AVAudioFrameCount(sampleCount)
        chunkData.withUnsafeBytes { rawBuf in
            let src = rawBuf.bindMemory(to: Float.self)
            let dst = buffer.floatChannelData![0]
            for i in 0..<sampleCount { dst[i] = src[i] }
        }
        eng.lock.lock()
        eng.scheduledBuffers += 1
        eng.lock.unlock()
        eng.playerNode.scheduleBuffer(buffer) {
            eng.lock.lock()
            eng.completedBuffers += 1
            eng.lock.unlock()
        }
    }

    close(fd)

    // Mark EOF
    streamEngine?.lock.lock()
    streamEngine?.stdinEOF = true
    streamEngine?.lock.unlock()
}

NSEvent.addLocalMonitorForEvents(matching: .keyDown) { event in
    switch event.keyCode {
    case 53: // ESC
        timer.invalidate()
        player?.stop()
        streamEngine?.stop()
        NSApp.terminate(nil)
        return nil
    case 49: // Spacebar
        if let p = player {
            if p.isPlaying {
                p.pause()
                isPaused = true
            } else {
                p.play()
                isPaused = false
            }
        }
        return nil
    case 123: // Left arrow
        if let p = player {
            p.currentTime = max(0, p.currentTime - 5)
        }
        return nil
    case 124: // Right arrow
        if let p = player {
            p.currentTime = min(p.duration, p.currentTime + 5)
        }
        return nil
    case 9: // V key
        // Cmd+V: paste text to speak
        if event.modifierFlags.contains(.command) {
            if let text = NSPasteboard.general.string(forType: .string), !text.isEmpty {
                flashTimer = 0.5
                let sanitized = text.replacingOccurrences(of: "\n", with: " ").trimmingCharacters(in: .whitespacesAndNewlines)
                // Stream from TTS daemon directly into visualizer
                DispatchQueue.global(qos: .userInitiated).async {
                    streamFromDaemon(text: sanitized)
                }
            }
            return nil
        }
        return event
    default:
        return event
    }
}

// Save window position periodically and on exit
func saveWindowPosition() {
    let frame = win.frame
    defaults.set(frame.origin.x, forKey: "herVoiceWindowX")
    defaults.set(frame.origin.y, forKey: "herVoiceWindowY")
    defaults.set(true, forKey: "herVoiceHasPosition")
}

// Save position every 2 seconds (catches drag moves)
let positionTimer = Timer(timeInterval: 2.0, repeats: true) { _ in
    saveWindowPosition()
}
RunLoop.main.add(positionTimer, forMode: .common)

// Save on exit
NotificationCenter.default.addObserver(
    forName: NSApplication.willTerminateNotification,
    object: nil, queue: .main
) { _ in
    let frame = win.frame
    defaults.set(frame.origin.x, forKey: "herVoiceWindowX")
    defaults.set(frame.origin.y, forKey: "herVoiceWindowY")
    defaults.set(true, forKey: "herVoiceHasPosition")
}

app.run()
