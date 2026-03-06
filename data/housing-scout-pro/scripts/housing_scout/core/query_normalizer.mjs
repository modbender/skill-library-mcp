const DEFAULT_SOUTH_BAY_CITIES = [
  "Mountain View",
  "Cupertino",
  "Los Altos",
  "Sunnyvale",
  "Palo Alto",
];

export function defaultBuyQuery() {
  return {
    queryId: "south-bay-buy-default",
    area: {
      mode: "city_set",
      cities: DEFAULT_SOUTH_BAY_CITIES,
      state: "CA",
    },
    intent: "buy",
    constraints: {
      hard: {
        priceMax: 3200000,
        bedsMin: 4,
        bathsMin: 2.5,
        homeTypes: ["single_family"],
        schoolScoreMin: 8,
        maxDriveMinutesToGoogleplex: 25,
      },
      soft: {
        preferBackyardForKids: true,
      },
    },
    notify: {
      channel: "telegram",
      to: "YOUR_CHAT_ID",
    },
  };
}

export function defaultRentQuery() {
  return {
    queryId: "south-bay-rent-default",
    area: {
      mode: "city_set",
      cities: DEFAULT_SOUTH_BAY_CITIES,
      state: "CA",
    },
    intent: "rent",
    constraints: {
      hard: {
        bedsMin: 4,
        bathsMin: 2.5,
        homeTypes: ["single_family"],
        schoolScoreMin: 8,
        maxDriveMinutesToGoogleplex: 25,
      },
      soft: {
        preferBackyardForKids: true,
      },
    },
    notify: {
      channel: "telegram",
      to: "YOUR_CHAT_ID",
    },
  };
}

export function normalizeQuery(input = {}) {
  const base = input.intent === "rent" ? defaultRentQuery() : defaultBuyQuery();
  return {
    ...base,
    ...input,
    area: {
      ...base.area,
      ...(input.area || {}),
    },
    constraints: {
      hard: {
        ...base.constraints.hard,
        ...(input.constraints?.hard || {}),
      },
      soft: {
        ...base.constraints.soft,
        ...(input.constraints?.soft || {}),
      },
    },
    notify: {
      ...base.notify,
      ...(input.notify || {}),
    },
  };
}
