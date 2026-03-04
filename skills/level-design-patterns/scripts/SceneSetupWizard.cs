using UnityEngine;
using UnityEditor;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace LevelDesignTools
{
    /// <summary>
    /// One-click scene initialization wizard
    /// Creates complete scene setup: terrain, lighting, post-processing, player
    /// </summary>
    public static class SceneSetupWizard
    {
        [MenuItem("Level Design/Quick Setup/Basic Scene", false, 1)]
        public static void CreateBasicScene()
        {
            // Create terrain
            var terrain = CreateTerrain();
            
            // Setup lighting
            SetupLighting();
            
            // Setup post-processing
            SetupPostProcessing();
            
            // Create player
            CreatePlayerController();
            
            Debug.Log("Basic scene setup complete!");
        }

        [MenuItem("Level Design/Quick Setup/Post-Apocalyptic Scene", false, 2)]
        public static void CreatePostApocalypticScene()
        {
            // Create ruined terrain
            var terrainData = CreateTerrainData(512, 512);
            AddNoiseToTerrain(terrainData, 50f, 0.01f);
            var terrain = Terrain.CreateTerrainGameObject(terrainData);
            terrain.name = "PostApocalypticTerrain";
            
            // Dramatic dark lighting
            SetupLighting(Color.gray * 0.2f);
            
            // Atmospheric fog
            SetupAtmosphericFog();
            
            // Add some ambient debris
            ScatterDebris(30);
            
            // Create player
            var player = CreatePlayerController();
            player.transform.position = new Vector3(256, 10, 256);
            
            // Position camera
            if (Camera.main != null)
            {
                Camera.main.transform.position = new Vector3(256, 15, 200);
                Camera.main.transform.LookAt(new Vector3(256, 10, 256));
            }
            
            Debug.Log("Post-apocalyptic scene setup complete!");
        }

        [MenuItem("Level Design/Quick Setup/Fantasy Forest", false, 3)]
        public static void CreateFantasyForest()
        {
            // Create rolling hills terrain
            var terrainData = CreateTerrainData(512, 512);
            AddRollingHills(terrainData, 30f, 0.005f);
            var terrain = Terrain.CreateTerrainGameObject(terrainData);
            terrain.name = "ForestTerrain";
            
            // Warm lighting with sun shafts
            SetupLighting(new Color(1f, 0.95f, 0.8f));
            
            // Add fog for atmosphere
            SetupAtmosphericFog(Color.white * 0.8f, 0.01f);
            
            // Create basic trees (if tree prototype available)
            // terrain.terrainData.treePrototypes = ...
            
            // Create player
            var player = CreatePlayerController();
            player.transform.position = new Vector3(256, 15, 256);
            
            Debug.Log("Fantasy forest scene setup complete!");
        }

        static Terrain CreateTerrain()
        {
            var terrainData = CreateTerrainData(512, 512);
            AddNoiseToTerrain(terrainData, 20f, 0.01f);
            
            var terrain = Terrain.CreateTerrainGameObject(terrainData);
            terrain.name = "Terrain";
            
            return terrain;
        }

        static TerrainData CreateTerrainData(int width, int height)
        {
            var terrainData = new TerrainData();
            terrainData.heightmapResolution = width + 1;
            terrainData.size = new Vector3(width, 50, height);
            
            AssetDatabase.CreateAsset(terrainData, "Assets/TerrainData.asset");
            
            return terrainData;
        }

        static void AddNoiseToTerrain(TerrainData terrainData, float heightScale, float frequency)
        {
            int resolution = terrainData.heightmapResolution;
            float[,] heights = new float[resolution, resolution];
            
            for (int x = 0; x < resolution; x++)
            {
                for (int y = 0; y < resolution; y++)
                {
                    float nx = x * frequency;
                    float ny = y * frequency;
                    heights[x, y] = Mathf.PerlinNoise(nx, ny) * (heightScale / terrainData.size.y);
                }
            }
            
            terrainData.SetHeights(0, 0, heights);
        }

        static void AddRollingHills(TerrainData terrainData, float heightScale, float frequency)
        {
            int resolution = terrainData.heightmapResolution;
            float[,] heights = new float[resolution, resolution];
            
            for (int x = 0; x < resolution; x++)
            {
                for (int y = 0; y < resolution; y++)
                {
                    float nx = x * frequency;
                    float ny = y * frequency;
                    float h1 = Mathf.PerlinNoise(nx, ny);
                    float h2 = Mathf.PerlinNoise(nx * 2f, ny * 2f) * 0.5f;
                    heights[x, y] = (h1 + h2) * (heightScale / terrainData.size.y) * 0.5f;
                }
            }
            
            terrainData.SetHeights(0, 0, heights);
        }

        static void SetupLighting(Color? ambientColor = null)
        {
            // Clear existing lights
            var existingLights = Object.FindObjectsOfType<Light>();
            foreach (var light in existingLights)
            {
                if (light.type == LightType.Directional)
                    Object.DestroyImmediate(light.gameObject);
            }
            
            // Create directional light (sun)
            var sunGO = new GameObject("Directional Light");
            var sun = sunGO.AddComponent<Light>();
            sun.type = LightType.Directional;
            sun.color = ambientColor ?? Color.white;
            sun.intensity = 1.0f;
            sun.shadows = LightShadows.Soft;
            sunGO.transform.rotation = Quaternion.Euler(50, -30, 0);
            
            // Set ambient light
            RenderSettings.ambientLight = ambientColor ?? new Color(0.2f, 0.2f, 0.2f);
            RenderSettings.ambientMode = AmbientMode.Flat;
            
            // Enable skybox
            RenderSettings.skybox = AssetDatabase.GetBuiltinExtraResource<Material>("Default-Skybox.mat");
        }

        static void SetupPostProcessing()
        {
            // Check if URP/HDRP is installed
            var pipelineAsset = GraphicsSettings.defaultRenderPipeline;
            
            if (pipelineAsset is UniversalRenderPipelineAsset)
            {
                // Create Global Volume for post-processing
                var volumeGO = new GameObject("Global Volume");
                var volume = volumeGO.AddComponent<Volume>();
                volume.isGlobal = true;
                
                // Create a basic profile (requires URP package)
                // Note: In real implementation, you'd create VolumeProfile assets
            }
        }

        static void SetupAtmosphericFog(Color? fogColor = null, float density = 0.02f)
        {
            RenderSettings.fog = true;
            RenderSettings.fogMode = FogMode.ExponentialSquared;
            RenderSettings.fogColor = fogColor ?? Color.gray * 0.5f;
            RenderSettings.fogDensity = density;
        }

        static void ScatterDebris(int count)
        {
            // Create simple cube debris
            for (int i = 0; i < count; i++)
            {
                var debris = GameObject.CreatePrimitive(PrimitiveType.Cube);
                debris.name = $"Debris_{i}";
                
                // Random position
                float x = Random.Range(0f, 512f);
                float z = Random.Range(0f, 512f);
                float y = Random.Range(0.5f, 2f);
                
                debris.transform.position = new Vector3(x, y, z);
                debris.transform.rotation = Random.rotation;
                debris.transform.localScale = Vector3.one * Random.Range(0.5f, 2f);
                
                // Dark material
                var renderer = debris.GetComponent<Renderer>();
                renderer.material.color = Color.gray * Random.Range(0.3f, 0.7f);
            }
        }

        static GameObject CreatePlayerController()
        {
            // Check if player already exists
            var existingPlayer = GameObject.Find("Player");
            if (existingPlayer != null)
                Object.DestroyImmediate(existingPlayer);
            
            // Create player
            var player = new GameObject("Player");
            player.tag = "Player";
            
            // Add Character Controller
            var cc = player.AddComponent<CharacterController>();
            cc.height = 2f;
            cc.radius = 0.5f;
            
            // Add camera
            var cameraGO = new GameObject("PlayerCamera");
            cameraGO.transform.SetParent(player.transform);
            cameraGO.transform.localPosition = new Vector3(0, 1.6f, 0);
            
            var camera = cameraGO.AddComponent<Camera>();
            camera.tag = "MainCamera";
            
            // Add basic movement script (would need actual implementation)
            // player.AddComponent<BasicFPSController>();
            
            // Position player
            player.transform.position = new Vector3(0, 5, 0);
            
            return player;
        }
    }
}