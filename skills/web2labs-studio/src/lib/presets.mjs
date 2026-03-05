export class PresetCatalog {
  static PRESETS = {
    quick: {
      name: "Quick Cleanup",
      description: "Fast silence removal, no extras",
      configuration: {
        subtitle: false,
        shorts: false,
        musicEnabled: false,
        zoom: true,
        thumbnailVariantsRequested: 0,
      },
    },
    youtube: {
      name: "YouTube Ready",
      description: "Full production with subtitles, shorts, and music",
      configuration: {
        subtitle: true,
        subtitlesOnVideo: true,
        shorts: true,
        shortsConfig: { amount: 3, minLength: 30, maxLength: 60 },
        musicEnabled: true,
        musicType: null,
        musicVolume: 15,
        zoom: true,
        thumbnailVariantsRequested: 2,
        thumbnailAutoGenerate: true,
      },
    },
    "shorts-only": {
      name: "Shorts Machine",
      description: "Generate shorts only",
      configuration: {
        onlyShorts: true,
        subtitle: true,
        subtitlesOnShorts: true,
        shorts: true,
        shortsConfig: { amount: 5, minLength: 15, maxLength: 60 },
        zoom: true,
        zoomsOnShorts: true,
        musicEnabled: true,
        musicOnShorts: true,
      },
    },
    podcast: {
      name: "Podcast Cleanup",
      description: "Talking-head cleanup with soft cuts",
      configuration: {
        subtitle: true,
        subtitlesOnVideo: true,
        shorts: false,
        musicEnabled: false,
        zoom: false,
        cutHardness: "soft",
        thumbnailVariantsRequested: 0,
      },
    },
    gaming: {
      name: "Gaming Montage",
      description: "Fast cuts with dynamic zoom",
      configuration: {
        gamingMode: true,
        subtitle: true,
        subtitlesOnShorts: true,
        shorts: true,
        shortsLayout: "split",
        shortsConfig: { amount: 3, minLength: 20, maxLength: 45 },
        zoom: true,
        zoomConfig: { frequency: 3, intensity: 3 },
        musicEnabled: true,
        musicType: "upbeat",
      },
    },
    tutorial: {
      name: "Tutorial",
      description: "Educational workflow with gentle edits",
      configuration: {
        subtitle: true,
        subtitlesOnVideo: true,
        shorts: false,
        musicEnabled: false,
        zoom: true,
        zoomConfig: { frequency: 1, intensity: 1 },
        cutHardness: "soft",
        thumbnailVariantsRequested: 1,
      },
    },
    vlog: {
      name: "Vlog Style",
      description: "Balanced editing with shorts and music",
      configuration: {
        subtitle: true,
        shorts: true,
        shortsConfig: { amount: 3, minLength: 30, maxLength: 60 },
        musicEnabled: true,
        musicType: "chill",
        musicVolume: 10,
        zoom: true,
        thumbnailVariantsRequested: 1,
      },
    },
    cinematic: {
      name: "Cinematic",
      description: "High-production settings",
      configuration: {
        premiumCut: true,
        subtitle: true,
        subtitlesOnVideo: true,
        shorts: true,
        shortsConfig: { amount: 2, minLength: 30, maxLength: 60 },
        musicEnabled: true,
        musicType: "cinematic",
        musicVolume: 20,
        zoom: true,
        zoomConfig: { frequency: 2, intensity: 2, animationDuration: 0.5 },
        thumbnailVariantsRequested: 2,
        thumbnailPremiumQuality: true,
      },
    },
  }

  static listPresets() {
    return Object.entries(PresetCatalog.PRESETS).map(([name, value]) => ({
      name,
      title: value.name,
      description: value.description,
    }))
  }

  static resolvePreset(name) {
    if (!name) {
      return null
    }
    const preset = PresetCatalog.PRESETS[name]
    if (!preset) {
      const available = Object.keys(PresetCatalog.PRESETS).join(", ")
      throw new Error(`Unknown preset \"${name}\". Available: ${available}`)
    }
    return PresetCatalog.cloneObject(preset.configuration)
  }

  static mergeConfigurations(baseConfig, overrideConfig) {
    const base = PresetCatalog.cloneObject(baseConfig || {})
    const override = overrideConfig || {}
    return PresetCatalog.deepMerge(base, override)
  }

  static cloneObject(value) {
    return JSON.parse(JSON.stringify(value || {}))
  }

  static deepMerge(target, source) {
    const result = target
    for (const key of Object.keys(source || {})) {
      const sourceValue = source[key]
      const targetValue = result[key]

      if (Array.isArray(sourceValue)) {
        result[key] = sourceValue.slice()
        continue
      }

      if (
        sourceValue &&
        typeof sourceValue === "object" &&
        !Array.isArray(sourceValue)
      ) {
        const nextTarget =
          targetValue && typeof targetValue === "object" && !Array.isArray(targetValue)
            ? targetValue
            : {}
        result[key] = PresetCatalog.deepMerge(nextTarget, sourceValue)
        continue
      }

      result[key] = sourceValue
    }
    return result
  }
}
