---
description: "PhotosPicker, camera, MapKit, and media patterns"
---
# SwiftUI Media Reference

## PhotosPicker

```swift
import PhotosUI

struct PhotoPickerView: View {
    @State private var selectedItem: PhotosPickerItem?
    @State private var selectedImage: Image?

    var body: some View {
        VStack {
            if let selectedImage {
                selectedImage
                    .resizable()
                    .aspectRatio(contentMode: .fit)
                    .frame(maxHeight: 300)
            }

            PhotosPicker("Select Photo", selection: $selectedItem, matching: .images)
        }
        .onChange(of: selectedItem) { _, newItem in
            Task {
                if let data = try? await newItem?.loadTransferable(type: Data.self),
                   let uiImage = UIImage(data: data) {
                    selectedImage = Image(uiImage: uiImage)
                }
            }
        }
    }
}
```

### Multiple Photo Selection

```swift
@State private var selectedItems: [PhotosPickerItem] = []

PhotosPicker("Select Photos", selection: $selectedItems, maxSelectionCount: 5, matching: .images)
```

## MapKit Integration

```swift
import MapKit

struct MapView: View {
    @State private var position: MapCameraPosition = .automatic
    let annotations: [Location]

    var body: some View {
        Map(position: $position) {
            ForEach(annotations) { location in
                Marker(location.name, coordinate: location.coordinate)
            }
        }
        .mapControls {
            MapUserLocationButton()
            MapCompass()
            MapScaleView()
        }
    }
}
```

### Map with Custom Annotations

```swift
Map(position: $position) {
    ForEach(places) { place in
        Annotation(place.name, coordinate: place.coordinate) {
            Image(systemName: "mappin.circle.fill")
                .foregroundStyle(.red)
                .font(.title)
        }
    }
}
```

## Location Services

```swift
import CoreLocation

@Observable
@MainActor
final class LocationManager: NSObject, CLLocationManagerDelegate {
    private let manager = CLLocationManager()
    var location: CLLocation?
    var authorizationStatus: CLAuthorizationStatus = .notDetermined

    override init() {
        super.init()
        manager.delegate = self
    }

    func requestPermission() {
        manager.requestWhenInUseAuthorization()
    }

    nonisolated func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        Task { @MainActor in
            location = locations.last
        }
    }

    nonisolated func locationManagerDidChangeAuthorization(_ manager: CLLocationManager) {
        Task { @MainActor in
            authorizationStatus = manager.authorizationStatus
        }
    }
}
```

## Camera Access

```swift
struct CameraView: UIViewControllerRepresentable {
    @Binding var image: UIImage?
    @Environment(\.dismiss) private var dismiss

    func makeUIViewController(context: Context) -> UIImagePickerController {
        let picker = UIImagePickerController()
        picker.sourceType = .camera
        picker.delegate = context.coordinator
        return picker
    }

    func updateUIViewController(_ uiViewController: UIImagePickerController, context: Context) {}

    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }

    class Coordinator: NSObject, UIImagePickerControllerDelegate, UINavigationControllerDelegate {
        let parent: CameraView
        init(_ parent: CameraView) { self.parent = parent }

        func imagePickerController(_ picker: UIImagePickerController, didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey: Any]) {
            parent.image = info[.originalImage] as? UIImage
            parent.dismiss()
        }
    }
}
```
