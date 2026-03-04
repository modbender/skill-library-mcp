---
name: swift-programming
version: 1.0.0
---

# Swift Programming Skill

Learn and program in Swift - Apple's programming language for iOS, macOS, watchOS, and tvOS.

## Quick Reference

### Variables & Constants
```swift
var nombre = "Juan"          // Variable
let edad = 25                 // Constante
var mensaje: String = "Hola"  // Con tipo explícito
```

### Tipos de Datos
```swift
String       // Texto
Int           // Entero
Double        // Decimal
Bool          // true/false
Array         // Lista
Dictionary    // clave-valor
Optional      // puede ser nil
```

### Funciones
```swift
func saludar(nombre: String) -> String {
    return "Hola, \(nombre)!"
}

// Parametro con valor por defecto
func greet(_ name: String = "Mundo") -> String {
    return "Hola, \(name)"
}
```

### Clases
```swift
class Persona {
    var nombre: String
    var edad: Int
    
    init(nombre: String, edad: Int) {
        self.nombre = nombre
        self.edad = edad
    }
    
    func presentar() -> String {
        return "Soy \(nombre) y tengo \(edad) años"
    }
}
```

### Estructuras
```swift
struct Punto {
    var x: Double
    var y: Double
    
    func distancia() -> Double {
        return sqrt(x*x + y*y)
    }
}
```

### Enums
```swift
enum Direction {
    case north, south, east, west
}

enum Status {
    case success(String)
    case failure(Error)
}
```

### Optionals
```swift
var nombre: String? = nil  // Puede ser nil

// unwrap seguro
if let nombre = nombre {
    print(nombre)
}

// nil coalescing
let nombreDefecto = nombre ?? "Anonimo"

// optional chaining
let longitud = nombre?.count ?? 0
```

### Closures
```swift
let suma = { (a: Int, b: Int) -> Int in
    return a + b
}

// Syntaxis reducida
let multiplicar: (Int, Int) -> Int = { $0 * $1 }
```

### Protocolos
```swift
protocol Naming {
    var name: String { get }
    func greet() -> String
}

struct User: Naming {
    var name: String
    
    func greet() -> String {
        return "Hola, \(name)!"
    }
}
```

### Async/Await
```swift
func fetchData() async throws -> Data {
    let url = URL(string: "https://api.example.com")!
    let (data, _) = try await URLSession.shared.data(from: url)
    return data
}

// Llamar
Task {
    do {
        let data = try await fetchData()
    } catch {
        print("Error: \(error)")
    }
}
```

### SwiftUI Basics
```swift
import SwiftUI

struct ContentView: View {
    @State private var count = 0
    
    var body: some View {
        VStack {
            Text("Contador: \(count)")
            Button("Incrementar") {
                count += 1
            }
        }
    }
}
```

## Recursos
- Apple Swift Docs: https://docs.swift.org/swift-book/
- Hacking with Swift: https://www.hackingwithswift.com
