using UnityEngine;
using UnityEditor;

namespace LevelDesignTools
{
    /// <summary>
    /// Procedural terrain generation tools
    /// Supports multiple noise algorithms and terrain types
    /// </summary>
    public static class TerrainGenerator
    {
        [MenuItem("Level Design/Terrain/Create Flat Terrain")]
        public static Terrain CreateFlatTerrain()
        {
            var terrainData = new TerrainData();
            terrainData.heightmapResolution = 513;
            terrainData.size = new Vector3(512, 50, 512);
            
            AssetDatabase.CreateAsset(terrainData, "Assets/FlatTerrainData.asset");
            
            return Terrain.CreateTerrainGameObject(terrainData);
        }

        [MenuItem("Level Design/Terrain/Create Hills Terrain")]
        public static Terrain CreateHillsTerrain()
        {
            var terrainData = CreateTerrainWithNoise(512, 512, 30f, 0.005f);
            AssetDatabase.CreateAsset(terrainData, "Assets/HillsTerrainData.asset");
            
            var terrain = Terrain.CreateTerrainGameObject(terrainData);
            terrain.name = "HillsTerrain";
            return terrain;
        }

        [MenuItem("Level Design/Terrain/Create Mountains")]
        public static Terrain CreateMountains()
        {
            var terrainData = CreateTerrainWithNoise(512, 512, 80f, 0.003f);
            AddDetailNoise(terrainData, 20f, 0.02f);
            
            AssetDatabase.CreateAsset(terrainData, "Assets/MountainTerrainData.asset");
            
            var terrain = Terrain.CreateTerrainGameObject(terrainData);
            terrain.name = "MountainTerrain";
            return terrain;
        }

        [MenuItem("Level Design/Terrain/Create Islands")]
        public static Terrain CreateIslands()
        {
            var terrainData = CreateIslandTerrain(512, 512, 40f);
            AssetDatabase.CreateAsset(terrainData, "Assets/IslandTerrainData.asset");
            
            var terrain = Terrain.CreateTerrainGameObject(terrainData);
            terrain.name = "IslandTerrain";
            return terrain;
        }

        public static TerrainData CreateTerrainWithNoise(int width, int height, float heightScale, float frequency)
        {
            var terrainData = new TerrainData();
            terrainData.heightmapResolution = width + 1;
            terrainData.size = new Vector3(width, heightScale * 2, height);
            
            float[,] heights = new float[width + 1, height + 1];
            
            for (int x = 0; x <= width; x++)
            {
                for (int y = 0; y <= height; y++)
                {
                    float nx = x * frequency;
                    float ny = y * frequency;
                    
                    // Multi-octave noise for detail
                    float h = 0;
                    float amp = 1f;
                    float freq = frequency;
                    
                    for (int o = 0; o < 4; o++)
                    {
                        h += Mathf.PerlinNoise(nx * freq, ny * freq) * amp;
                        amp *= 0.5f;
                        freq *= 2f;
                    }
                    
                    heights[x, y] = h * 0.5f;
                }
            }
            
            terrainData.SetHeights(0, 0, heights);
            return terrainData;
        }

        public static TerrainData CreateIslandTerrain(int width, int height, float heightScale)
        {
            var terrainData = new TerrainData();
            terrainData.heightmapResolution = width + 1;
            terrainData.size = new Vector3(width, heightScale * 2, height);
            
            float[,] heights = new float[width + 1, height + 1];
            float centerX = width / 2f;
            float centerY = height / 2f;
            float maxDist = Mathf.Sqrt(centerX * centerX + centerY * centerY);
            
            for (int x = 0; x <= width; x++)
            {
                for (int y = 0; y <= height; y++)
                {
                    float dist = Mathf.Sqrt((x - centerX) * (x - centerX) + (y - centerY) * (y - centerY));
                    float falloff = 1f - (dist / maxDist);
                    falloff = Mathf.Pow(falloff, 2f);
                    
                    float nx = x * 0.005f;
                    float ny = y * 0.005f;
                    float h = Mathf.PerlinNoise(nx, ny);
                    
                    heights[x, y] = h * falloff * 0.8f;
                }
            }
            
            terrainData.SetHeights(0, 0, heights);
            return terrainData;
        }

        static void AddDetailNoise(TerrainData terrainData, float heightScale, float frequency)
        {
            int resolution = terrainData.heightmapResolution;
            float[,] heights = terrainData.GetHeights(0, 0, resolution, resolution);
            
            for (int x = 0; x < resolution; x++)
            {
                for (int y = 0; y < resolution; y++)
                {
                    float nx = x * frequency + 1000;
                    float ny = y * frequency + 1000;
                    float detail = Mathf.PerlinNoise(nx, ny) * (heightScale / terrainData.size.y);
                    heights[x, y] += detail * 0.1f;
                }
            }
            
            terrainData.SetHeights(0, 0, heights);
        }

        public static void FlattenTerrain(Terrain terrain, float height = 0.5f)
        {
            int resolution = terrain.terrainData.heightmapResolution;
            float[,] heights = new float[resolution, resolution];
            
            for (int x = 0; x < resolution; x++)
            {
                for (int y = 0; y < resolution; y++)
                {
                    heights[x, y] = height;
                }
            }
            
            terrain.terrainData.SetHeights(0, 0, heights);
        }

        public static void SmoothTerrain(Terrain terrain, int iterations = 1)
        {
            int resolution = terrain.terrainData.heightmapResolution;
            
            for (int i = 0; i < iterations; i++)
            {
                float[,] heights = terrain.terrainData.GetHeights(0, 0, resolution, resolution);
                float[,] smoothed = new float[resolution, resolution];
                
                for (int x = 1; x < resolution - 1; x++)
                {
                    for (int y = 1; y < resolution - 1; y++)
                    {
                        float avg = 0;
                        avg += heights[x - 1, y];
                        avg += heights[x + 1, y];
                        avg += heights[x, y - 1];
                        avg += heights[x, y + 1];
                        avg += heights[x, y];
                        avg /= 5f;
                        
                        smoothed[x, y] = avg;
                    }
                }
                
                terrain.terrainData.SetHeights(0, 0, smoothed);
            }
        }

        [MenuItem("Level Design/Terrain/Export Heightmap")]
        public static void ExportHeightmap()
        {
            var terrain = Selection.activeGameObject?.GetComponent<Terrain>();
            if (terrain == null)
            {
                Debug.LogError("Please select a terrain object");
                return;
            }
            
            string path = EditorUtility.SaveFilePanel("Export Heightmap", "Assets", "Heightmap", "png");
            if (string.IsNullOrEmpty(path))
                return;
            
            int resolution = terrain.terrainData.heightmapResolution;
            float[,] heights = terrain.terrainData.GetHeights(0, 0, resolution, resolution);
            
            Texture2D tex = new Texture2D(resolution, resolution, TextureFormat.R16, false);
            Color[] colors = new Color[resolution * resolution];
            
            for (int x = 0; x < resolution; x++)
            {
                for (int y = 0; y < resolution; y++)
                {
                    float h = heights[x, y];
                    colors[x + y * resolution] = new Color(h, h, h);
                }
            }
            
            tex.SetPixels(colors);
            tex.Apply();
            
            byte[] bytes = tex.EncodeToPNG();
            System.IO.File.WriteAllBytes(path, bytes);
            
            Debug.Log($"Heightmap exported to: {path}");
        }
    }
}