// swift-tools-version:5.9
import PackageDescription

let package = Package(
    name: "StellaVoice",
    platforms: [.macOS(.v14)],
    dependencies: [
        .package(url: "https://github.com/FluidInference/FluidAudio.git", from: "0.12.0"),
        .package(url: "https://github.com/hummingbird-project/hummingbird.git", from: "2.0.0"),
    ],
    targets: [
        .executableTarget(
            name: "StellaVoice",
            dependencies: [
                .product(name: "FluidAudio", package: "FluidAudio"),
                .product(name: "FluidAudioTTS", package: "FluidAudio"),
                .product(name: "Hummingbird", package: "hummingbird"),
            ]
        ),
    ]
)
