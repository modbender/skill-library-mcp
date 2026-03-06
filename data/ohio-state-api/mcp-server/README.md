# OSU MCP Server

A comprehensive MCP (Model Context Protocol) server that provides access to The Ohio State University's content APIs across multiple campus services including transportation, academics, dining, recreation, libraries, events, and more.

## Features

This server provides **50+ tools** across **14 different service categories** for LLMs:

### Athletics
- **get_athletics_all**: Get information about all OSU athletics programs and schedules
- **search_sports**: Search for specific sports or teams
- **get_sport_by_gender**: Find sports programs by gender
- **get_upcoming_games**: Get upcoming games and events across all sports

### Buildings
- **get_buildings**: Get information about all OSU buildings
- **search_buildings**: Search for buildings by name or building number
- **get_building_details**: Get detailed information about a specific building
- **find_room_type**: Find buildings with specific room types (lactation, sanctuary, wellness, gender inclusive restrooms)

### Bus Transportation
- **get_bus_routes**: Get information about all OSU bus routes
- **get_bus_stops**: Get stops and route information for a specific bus line
- **get_bus_vehicles**: Get real-time vehicle locations for a specific route

### Academic Calendar & Holidays
- **get_academic_calendar**: Get the academic calendar with important dates
- **get_university_holidays**: Get university holidays
- **search_calendar_events**: Search for specific events in the academic calendar
- **get_holidays_by_year**: Get holidays for a specific year

### Classes
- **search_classes**: Search for OSU classes by keyword, subject, instructor, etc.

### Campus Events
- **get_campus_events**: Get information about all campus events
- **search_campus_events**: Search for campus events by title or description
- **get_events_by_tag**: Find events by specific tags or categories
- **get_events_by_location**: Find events at a specific location
- **get_events_by_date_range**: Find events within a specific date range

### Dining
- **get_dining_locations**: Get all OSU dining locations with basic information
- **get_dining_locations_with_menus**: Get dining locations with menu section information
- **get_dining_menu**: Get detailed menu items for a specific dining location section

### University Directory & People Search
- **get_university_directory**: Get the university directory information
- **search_people**: Search for people in the OSU directory by first and/or last name

### Food Trucks
- **get_foodtruck_events**: Get information about all food truck events on campus
- **search_foodtrucks**: Search for food trucks by name or cuisine type
- **get_foodtrucks_by_location**: Find food trucks at a specific location

### Library Services
- **get_library_locations**: Get information about all OSU library locations
- **search_library_locations**: Search for library locations by name
- **get_library_rooms**: Get information about all available library study rooms
- **search_library_rooms**: Search for library study rooms by name or location
- **get_rooms_by_capacity**: Find library study rooms by capacity
- **get_rooms_with_amenities**: Find library study rooms with specific amenities

### BuckID Merchants
- **get_buckid_merchants**: Get information about all merchants that accept BuckID
- **search_merchants**: Search for merchants by name or category
- **get_merchants_by_food_type**: Find merchants by food/cuisine type
- **get_merchants_with_meal_plan**: Find merchants that accept meal plans

### Parking
- **get_parking_availability**: Get real-time parking availability for all OSU parking garages

### Recreation Sports
- **get_recsports_facilities**: Get information about all OSU recreation sports facilities
- **search_recsports_facilities**: Search for recreation sports facilities by name
- **get_facility_details**: Get detailed information about a specific recreation facility
- **get_facility_hours**: Get current operating hours for all recreation facilities
- **get_facility_events**: Get scheduled events for recreation sports facilities

### Student Organizations
- **get_student_organizations**: Get information about all student organizations
- **search_student_orgs**: Search for student organizations by name or keywords
- **get_orgs_by_type**: Find student organizations by type or category
- **get_orgs_by_career_level**: Find organizations for specific career levels

## Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   npm install
   ```
3. Build the server:
   ```bash
   npm run build
   ```

## Usage

### With Claude Desktop

Add this server to your Claude Desktop configuration file:

**On macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

**On Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "osu": {
      "command": "node",
      "args": ["/path/to/ohio-state-mcp-server/build/index.js"]
    }
  }
}
```

### Standalone Usage

You can also run the server directly:

```bash
npm start
```

## Development

To run in development mode with automatic rebuilding:

```bash
npm run dev
```

## API Information

This server uses The Ohio State University's content APIs.

## License

MIT
