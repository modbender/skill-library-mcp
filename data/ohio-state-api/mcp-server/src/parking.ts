import { Tool } from "@modelcontextprotocol/sdk/types.js";
import { addLocalTimeToResponse, getCurrentEasternTime } from "./utils.js";

const BASE_URL = "https://content.osu.edu/v2/parking/garages";

export const parkingTools: Tool[] = [
  {
    name: "get_parking_availability",
    description: "Get real-time parking availability for all OSU parking garages",
    inputSchema: {
      type: "object",
      properties: {},
      required: []
    }
  }
];

export async function handleParkingTool(name: string, args: any): Promise<any> {
  try {
    switch (name) {
      case "get_parking_availability":
        const response = await fetch(`${BASE_URL}/availability`);
        const data = await response.json();
        const processedData = addLocalTimeToResponse(data);
        
        return {
          content: [{
            type: "text",
            text: `OSU Parking Garage Availability (Retrieved at ${getCurrentEasternTime()} Eastern Time):\n${JSON.stringify(processedData, null, 2)}`
          }]
        };

      default:
        throw new Error(`Unknown parking tool: ${name}`);
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