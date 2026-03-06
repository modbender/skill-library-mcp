# Unity Level Design - API Reference

## Core Unity APIs for Level Design

### Terrain System (UnityEngine.Terrain)

**Key Classes:**
- `Terrain` - The main terrain component
- `TerrainData` - Stores heightmap, splatmaps, trees, details
- `TerrainCollider` - Collision for terrain

**TerrainData Properties:**
```csharp
// Heightmap resolution (power of 2 + 1: 65, 129, 257, 513, 1025...)
terrainData.heightmapResolution = 513;

// Size in world units (width, height, length)
terrainData.size = new Vector3(512, 50, 512);

// Get/set heightmap data (0-1 range)
float[,] heights = terrainData.GetHeights(0, 0, width, height);
terrainData.SetHeights(0, 0, heights);
```

**Terrain Creation:**
```csharp
// Create terrain data asset
var terrainData = new TerrainData();
AssetDatabase.CreateAsset(terrainData, "Assets/TerrainData.asset");

// Create terrain game object
Terrain terrain = Terrain.CreateTerrainGameObject(terrainData);
```

### Mesh Generation (UnityEngine.Mesh)

**Creating meshes at runtime:**
```csharp
Mesh mesh = new Mesh();

// Define vertices
Vector3[] vertices = new Vector3[4];
vertices[0] = new Vector3(0, 0, 0);
vertices[1] = new Vector3(1, 0, 0);
vertices[2] = new Vector3(0, 0, 1);
vertices[3] = new Vector3(1, 0, 1);

// Define triangles (clockwise winding)
int[] triangles = new int[] { 0, 2, 1, 2, 3, 1 };

// Assign to mesh
mesh.vertices = vertices;
mesh.triangles = triangles;
mesh.RecalculateNormals();

// Create game object
GameObject go = new GameObject("ProceduralMesh");
go.AddComponent<MeshFilter>().mesh = mesh;
go.AddComponent<MeshRenderer>().material = new Material(Shader.Find("Standard"));
go.AddComponent<MeshCollider>().sharedMesh = mesh;
```

### Editor Scripting (UnityEditor)

**Menu Items:**
```csharp
[MenuItem("Level Design/Tools/My Tool")]
static void MyTool()
{
    // Code here
}

// Validate menu item (grayed out if returns false)
[MenuItem("Level Design/Tools/My Tool", true)]
static bool ValidateMyTool()
{
    return Selection.activeGameObject != null;
}
```

**Asset Database:**
```csharp
// Create asset
AssetDatabase.CreateAsset(myObject, "Assets/MyAsset.asset");

// Load asset
var asset = AssetDatabase.LoadAssetAtPath<Material>("Assets/Materials/MyMat.mat");

// Refresh
AssetDatabase.Refresh();

// Save assets
AssetDatabase.SaveAssets();
```

**Scene Management:**
```csharp
// Create new scene
var newScene = EditorSceneManager.NewScene(NewSceneSetup.DefaultGameObjects);

// Open scene
EditorSceneManager.OpenScene("Assets/Scenes/MyScene.unity");

// Save scene
EditorSceneManager.SaveScene(EditorSceneManager.GetActiveScene());
```

### Noise Functions

**Perlin Noise:**
```csharp
float height = Mathf.PerlinNoise(x * frequency, y * frequency);
```

**Multi-octave (fbm):**
```csharp
float GetNoise(float x, float y, int octaves, float persistence)
{
    float total = 0;
    float frequency = 1;
    float amplitude = 1;
    float maxValue = 0;
    
    for(int i = 0; i < octaves; i++)
    {
        total += Mathf.PerlinNoise(x * frequency, y * frequency) * amplitude;
        maxValue += amplitude;
        amplitude *= persistence;
        frequency *= 2;
    }
    
    return total / maxValue;
}
```

### Render Pipeline Detection

```csharp
using UnityEngine.Rendering;

// Check current render pipeline
var pipelineAsset = GraphicsSettings.defaultRenderPipeline;

if (pipelineAsset == null)
    Debug.Log("Built-in Render Pipeline");
else if (pipelineAsset is UniversalRenderPipelineAsset)
    Debug.Log("Universal Render Pipeline (URP)");
else if (pipelineAsset is HDRenderPipelineAsset)
    Debug.Log("High Definition Render Pipeline (HDRP)");
```

### Lighting & Atmosphere

**Render Settings:**
```csharp
// Ambient light
RenderSettings.ambientMode = AmbientMode.Flat; // or Skybox, Trilight, Gradient
RenderSettings.ambientLight = Color.gray;
RenderSettings.ambientIntensity = 1f;

// Fog
RenderSettings.fog = true;
RenderSettings.fogMode = FogMode.Exponential; // or Linear, ExponentialSquared
RenderSettings.fogColor = Color.gray;
RenderSettings.fogDensity = 0.01f;
RenderSettings.fogStartDistance = 10f;
RenderSettings.fogEndDistance = 100f;

// Skybox
RenderSettings.skybox = mySkyboxMaterial;
```

**Light Component:**
```csharp
Light light = gameObject.AddComponent<Light>();
light.type = LightType.Directional; // or Point, Spot, Area
light.color = Color.white;
light.intensity = 1f;
light.range = 10f; // for point/spot
light.spotAngle = 30f; // for spot
light.shadows = LightShadows.Soft; // or Hard, None
```

## URP-Specific APIs

### Universal Render Pipeline

**UniversalAdditionalLightData:**
```csharp
var additionalData = light.gameObject.AddComponent<UniversalAdditionalLightData>();
additionalData.renderingLayerMask = 1;
```

**Volume & Post-Processing:**
```csharp
// Create global volume
var volumeGO = new GameObject("Global Volume");
var volume = volumeGO.AddComponent<Volume>();
volume.isGlobal = true;

// Load or create profile
var profile = AssetDatabase.LoadAssetAtPath<VolumeProfile>("Assets/Settings/MyProfile.asset");
volume.profile = profile;
```

## Common Patterns

### Object Placement
```csharp
// Raycast to place on terrain
Ray ray = new Ray(spawnPosition + Vector3.up * 100, Vector3.down);
if (Physics.Raycast(ray, out RaycastHit hit))
{
    object.transform.position = hit.point;
}
```

### Batch Processing
```csharp
// Process multiple objects
var objects = Selection.gameObjects;
Undo.RecordObjects(objects, "Batch Operation");

foreach (var obj in objects)
{
    // Modify obj
}
```

### Undo Support
```csharp
// Register for undo
Undo.RegisterCreatedObjectUndo(newGameObject, "Create Object");
Undo.RecordObject(targetObject, "Modify Property");
Undo.DestroyObjectImmediate(gameObject);
```