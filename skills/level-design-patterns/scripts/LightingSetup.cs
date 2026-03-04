using UnityEngine;
using UnityEditor;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace LevelDesignTools
{
    /// <summary>
    /// Automated lighting and atmosphere setup
    /// Supports Built-in, URP, and HDRP render pipelines
    /// </summary>
    public static class LightingSetup
    {
        [MenuItem("Level Design/Lighting/Clear Lighting")]
        public static void ClearAllLighting()
        {
            // Remove all lights
            var lights = Object.FindObjectsOfType<Light>();
            foreach (var light in lights)
            {
                if (light.gameObject.name.Contains("Sun") || light.gameObject.name.Contains("Light"))
                    Object.DestroyImmediate(light.gameObject);
            }
            
            // Remove reflection probes
            var probes = Object.FindObjectsOfType<ReflectionProbe>();
            foreach (var probe in probes)
                Object.DestroyImmediate(probe.gameObject);
            
            Debug.Log("Lighting cleared");
        }

        [MenuItem("Level Design/Lighting/Day Lighting")]
        public static void SetupDayLighting()
        {
            ClearAllLighting();
            
            // Main sun
            var sun = CreateDirectionalLight("Sun", new Color(1f, 0.96f, 0.84f), 1.2f);
            sun.transform.rotation = Quaternion.Euler(45, -30, 0);
            
            // Ambient
            RenderSettings.ambientMode = AmbientMode.Skybox;
            RenderSettings.ambientIntensity = 1f;
            
            // Skybox
            RenderSettings.skybox = AssetDatabase.GetBuiltinExtraResource<Material>("Default-Skybox.mat");
            
            // Fog
            RenderSettings.fog = true;
            RenderSettings.fogMode = FogMode.Exponential;
            RenderSettings.fogColor = new Color(0.8f, 0.9f, 1f);
            RenderSettings.fogDensity = 0.005f;
            
            Debug.Log("Day lighting setup complete");
        }

        [MenuItem("Level Design/Lighting/Night Lighting")]
        public static void SetupNightLighting()
        {
            ClearAllLighting();
            
            // Moon
            var moon = CreateDirectionalLight("Moon", new Color(0.6f, 0.7f, 0.9f), 0.4f);
            moon.transform.rotation = Quaternion.Euler(-45, 30, 0);
            
            // Ambient
            RenderSettings.ambientMode = AmbientMode.Flat;
            RenderSettings.ambientLight = new Color(0.1f, 0.15f, 0.25f);
            
            // Dark sky
            RenderSettings.skybox = null;
            RenderSettings.ambientIntensity = 0.5f;
            
            // Fog
            RenderSettings.fog = true;
            RenderSettings.fogMode = FogMode.Exponential;
            RenderSettings.fogColor = new Color(0.05f, 0.05f, 0.1f);
            RenderSettings.fogDensity = 0.02f;
            
            Debug.Log("Night lighting setup complete");
        }

        [MenuItem("Level Design/Lighting/Post-Apocalyptic")]
        public static void SetupPostApocalypticLighting()
        {
            ClearAllLighting();
            
            // Harsh sun
            var sun = CreateDirectionalLight("Harsh Sun", new Color(1f, 0.9f, 0.7f), 1.5f);
            sun.transform.rotation = Quaternion.Euler(60, -15, 0);
            
            // Dark ambient
            RenderSettings.ambientMode = AmbientMode.Flat;
            RenderSettings.ambientLight = new Color(0.15f, 0.15f, 0.15f);
            
            // Gray fog
            RenderSettings.fog = true;
            RenderSettings.fogMode = FogMode.ExponentialSquared;
            RenderSettings.fogColor = new Color(0.3f, 0.3f, 0.3f);
            RenderSettings.fogDensity = 0.015f;
            
            // Overcast sky
            if (RenderSettings.skybox != null)
                RenderSettings.skybox.SetColor("_SkyTint", Color.gray * 0.5f);
            
            Debug.Log("Post-apocalyptic lighting setup complete");
        }

        [MenuItem("Level Design/Lighting/Indoor/Cozy")]
        public static void SetupIndoorCozy()
        {
            ClearAllLighting();
            
            // Warm point lights would be added by user
            RenderSettings.ambientMode = AmbientMode.Flat;
            RenderSettings.ambientLight = new Color(0.2f, 0.15f, 0.1f);
            
            // No fog indoors
            RenderSettings.fog = false;
            
            Debug.Log("Indoor cozy lighting setup complete. Add point lights as needed.");
        }

        [MenuItem("Level Design/Lighting/Indoor/Dungeon")]
        public static void SetupDungeonLighting()
        {
            ClearAllLighting();
            
            // Very dark
            RenderSettings.ambientMode = AmbientMode.Flat;
            RenderSettings.ambientLight = new Color(0.02f, 0.02f, 0.03f);
            
            RenderSettings.fog = true;
            RenderSettings.fogMode = FogMode.Exponential;
            RenderSettings.fogColor = Color.black;
            RenderSettings.fogDensity = 0.05f;
            
            Debug.Log("Dungeon lighting setup complete. Add torches/lights as needed.");
        }

        static Light CreateDirectionalLight(string name, Color color, float intensity)
        {
            var go = new GameObject(name);
            var light = go.AddComponent<Light>();
            light.type = LightType.Directional;
            light.color = color;
            light.intensity = intensity;
            light.shadows = LightShadows.Soft;
            return light;
        }

        [MenuItem("Level Design/Atmosphere/Disable Fog")]
        public static void DisableFog()
        {
            RenderSettings.fog = false;
        }

        [MenuItem("Level Design/Atmosphere/Heavy Fog")]
        public static void SetupHeavyFog()
        {
            RenderSettings.fog = true;
            RenderSettings.fogMode = FogMode.ExponentialSquared;
            RenderSettings.fogDensity = 0.03f;
            RenderSettings.fogColor = Color.gray * 0.5f;
        }

        [MenuItem("Level Design/Atmosphere/Dust Storm")]
        public static void SetupDustStorm()
        {
            RenderSettings.fog = true;
            RenderSettings.fogMode = FogMode.Exponential;
            RenderSettings.fogDensity = 0.05f;
            RenderSettings.fogColor = new Color(0.6f, 0.5f, 0.4f);
        }

        public static void SetupURPPostProcessing()
        {
            // Check if URP is active
            if (GraphicsSettings.defaultRenderPipeline is not UniversalRenderPipelineAsset)
            {
                Debug.LogWarning("URP is not the active render pipeline");
                return;
            }
            
            // Create global volume
            var volumeGO = new GameObject("Global Volume");
            var volume = volumeGO.AddComponent<Volume>();
            volume.isGlobal = true;
            
            // Profile needs to be created via asset
            // volume.profile = ... (would need to create asset)
            
            Debug.Log("URP Global Volume created. Add VolumeProfile asset to configure effects.");
        }

        [MenuItem("Level Design/Baking/Bake Lighting")]
        public static void BakeLighting()
        {
            Lightmapping.BakeAsync();
            Debug.Log("Started lightmap bake...");
        }

        [MenuItem("Level Design/Baking/Clear Baked Lighting")]
        public static void ClearBakedLighting()
        {
            Lightmapping.Clear();
            Debug.Log("Baked lighting cleared");
        }
    }
}