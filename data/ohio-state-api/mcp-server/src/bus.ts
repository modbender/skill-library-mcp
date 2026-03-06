import { Tool } from "@modelcontextprotocol/sdk/types.js";
import { addLocalTimeToResponse, getCurrentEasternTime } from "./utils.js";

const BASE_URL = "https://content.osu.edu/v2/bus";

const BUS_ROUTES = {
  "ACK": "Ackerman Shuttle",
  "BE": "Buckeye Express",
  "CC": "Campus Connector",
  "CLS": "Campus Loop South",
  "ER": "East Residential",
  "MC": "Medical Center",
  "MM": "Morehouse to Med Center Shuttle",
  "NWC": "Northwest Connector",
  "WMC": "Wexner Medical Center Shuttle"
};

export const busTools: Tool[] = [
  {
    name: "get_bus_routes",
    description: "Get information about all OSU bus routes/lines",
    inputSchema: {
      type: "object",
      properties: {},
      required: []
    }
  },
  {
    name: "get_bus_stops",
    description: "Get all stops and route information for a specific bus line",
    inputSchema: {
      type: "object",
      properties: {
        route_code: {
          type: "string",
          description: "Bus route code (ACK, BE, CC, CLS, ER, MC, MM, NWC, WMC)",
          enum: ["ACK", "BE", "CC", "CLS", "ER", "MC", "MM", "NWC", "WMC"]
        }
      },
      required: ["route_code"]
    }
  },
  {
    name: "get_bus_vehicles",
    description: "Get real-time vehicle/bus locations for a specific route",
    inputSchema: {
      type: "object",
      properties: {
        route_code: {
          type: "string",
          description: "Bus route code (ACK, BE, CC, CLS, ER, MC, MM, NWC, WMC)",
          enum: ["ACK", "BE", "CC", "CLS", "ER", "MC", "MM", "NWC", "WMC"]
        }
      },
      required: ["route_code"]
    }
  }
];

export async function handleBusTool(name: string, args: any): Promise<any> {
  try {
    switch (name) {
      case "get_bus_routes":
        const routesResponse = await fetch(`${BASE_URL}/routes/`);
        const routesData = await routesResponse.json();
        const processedRoutesData = addLocalTimeToResponse(routesData);
        
        return {
          content: [{
            type: "text",
            text: `OSU Bus Routes (Retrieved at ${getCurrentEasternTime()} Eastern Time):\n${JSON.stringify(processedRoutesData, null, 2)}`
          }]
        };

      case "get_bus_stops":
        const { route_code } = args;
        if (!BUS_ROUTES[route_code as keyof typeof BUS_ROUTES]) {
          throw new Error(`Invalid route code: ${route_code}`);
        }
        
        const stopsResponse = await fetch(`${BASE_URL}/routes/${route_code}`);
        const stopsData = await stopsResponse.json();
        const processedStopsData = addLocalTimeToResponse(stopsData);
        
        return {
          content: [{
            type: "text", 
            text: `Bus stops for ${BUS_ROUTES[route_code as keyof typeof BUS_ROUTES]} (${route_code}) - Retrieved at ${getCurrentEasternTime()} Eastern Time:\n${JSON.stringify(processedStopsData, null, 2)}`
          }]
        };

      case "get_bus_vehicles":
        const { route_code: vehicleRoute } = args;
        if (!BUS_ROUTES[vehicleRoute as keyof typeof BUS_ROUTES]) {
          throw new Error(`Invalid route code: ${vehicleRoute}`);
        }
        
        const vehiclesResponse = await fetch(`${BASE_URL}/routes/${vehicleRoute}/vehicles`);
        const vehiclesData = await vehiclesResponse.json();
        const processedVehiclesData = addLocalTimeToResponse(vehiclesData);
        
        return {
          content: [{
            type: "text",
            text: `Current vehicles on ${BUS_ROUTES[vehicleRoute as keyof typeof BUS_ROUTES]} (${vehicleRoute}) - Retrieved at ${getCurrentEasternTime()} Eastern Time:\n${JSON.stringify(processedVehiclesData, null, 2)}`
          }]
        };

      default:
        throw new Error(`Unknown bus tool: ${name}`);
    }
  } catch (error) {
    return {
      content: [{
        type: "text",
        text: `Error: ${error instanceof Error ? error.message : String(error)}`
      }],
      isError: true
    };
  }
}