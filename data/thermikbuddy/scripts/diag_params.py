import urllib.request
import json

# URL für Werdenfels (47.5, 11.1)
# Teste verschiedene Modelle und Variablennamen
models = ["icon_d2", "ecmwf_ifs04", "gfs_seamless"]
vars = ["boundary_layer_height", "cape", "lifted_index"]

print("--- Diagnose Start ---")

for model in models:
    print(f"\nPrüfe Modell: {model}")
    url = f"https://api.open-meteo.com/v1/forecast?latitude=47.5&longitude=11.1&hourly={','.join(vars)}&models={model}&forecast_days=1"
    
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read())
            
            # Check hourly data
            hourly = data.get("hourly", {})
            for var in vars:
                values = hourly.get(var, [])
                # Zeige die ersten 5 Werte (nicht null)
                non_zero = [v for v in values if v is not None and v > 0]
                print(f"  {var}: {len(non_zero)}/{len(values)} Werte > 0. Bsp: {values[:3]}")
                
    except Exception as e:
        print(f"  Fehler bei {model}: {e}")

print("\n--- Diagnose Ende ---")
