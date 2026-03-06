#!/usr/bin/env node

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

import { athleticsTools, handleAthleticsTool } from "./athletics.js";
import { busTools, handleBusTool } from "./bus.js";
import { buildingTools, handleBuildingTool } from "./buildings.js";
import { calendarTools, handleCalendarTool } from "./calendar.js";
import { classTools, handleClassTool } from "./classes.js";
import { diningTools, handleDiningTool } from "./dining.js";
import { directoryTools, handleDirectoryTool } from "./directory.js";
import { eventsTools, handleEventsTool } from "./events.js";
import { foodtruckTools, handleFoodtruckTool } from "./foodtrucks.js";
import { libraryTools, handleLibraryTool } from "./library.js";
import { merchantTools, handleMerchantTool } from "./merchants.js";
import { parkingTools, handleParkingTool } from "./parking.js";
import { recsportsTools, handleRecsportsTool } from "./recsports.js";
import { studentorgTools, handleStudentorgTool } from "./studentorgs.js";

const server = new Server(
  {
    name: "osu-mcp-server",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

const allTools = [
  ...athleticsTools,
  ...busTools,
  ...buildingTools,
  ...calendarTools,
  ...classTools, 
  ...diningTools,
  ...directoryTools,
  ...eventsTools,
  ...foodtruckTools,
  ...libraryTools,
  ...merchantTools,
  ...parkingTools,
  ...recsportsTools,
  ...studentorgTools
];

server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: allTools,
  };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    if (athleticsTools.some(tool => tool.name === name)) {
      return await handleAthleticsTool(name, args || {});
    }
    
    if (busTools.some(tool => tool.name === name)) {
      return await handleBusTool(name, args || {});
    }
    
    if (buildingTools.some(tool => tool.name === name)) {
      return await handleBuildingTool(name, args || {});
    }
    
    if (calendarTools.some(tool => tool.name === name)) {
      return await handleCalendarTool(name, args || {});
    }
    
    if (classTools.some(tool => tool.name === name)) {
      return await handleClassTool(name, args || {});
    }
    
    if (diningTools.some(tool => tool.name === name)) {
      return await handleDiningTool(name, args || {});
    }
    
    if (directoryTools.some(tool => tool.name === name)) {
      return await handleDirectoryTool(name, args || {});
    }
    
    if (eventsTools.some(tool => tool.name === name)) {
      return await handleEventsTool(name, args || {});
    }
    
    if (foodtruckTools.some(tool => tool.name === name)) {
      return await handleFoodtruckTool(name, args || {});
    }
    
    if (libraryTools.some(tool => tool.name === name)) {
      return await handleLibraryTool(name, args || {});
    }
    
    if (merchantTools.some(tool => tool.name === name)) {
      return await handleMerchantTool(name, args || {});
    }
    
    if (parkingTools.some(tool => tool.name === name)) {
      return await handleParkingTool(name, args || {});
    }
    
    if (recsportsTools.some(tool => tool.name === name)) {
      return await handleRecsportsTool(name, args || {});
    }
    
    if (studentorgTools.some(tool => tool.name === name)) {
      return await handleStudentorgTool(name, args || {});
    }

    throw new Error(`Unknown tool: ${name}`);
  } catch (error) {
    return {
      content: [{
        type: "text",
        text: `Error: ${error instanceof Error ? error.message : String(error)}`
      }],
      isError: true
    };
  }
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("OSU MCP Server running on stdio");
}

main().catch((error) => {
  console.error("Server error:", error);
  process.exit(1);
});