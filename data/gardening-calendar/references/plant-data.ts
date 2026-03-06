// Bundled plant data for the Gardening Calendar skill
export const PLANTS = [
  {
    id: 'tomato',
    name: 'Tomato',
    slug: 'tomato',
    category: 'vegetable',
    sowIndoor: [{ start: { month: 2, day: 1 }, end: { month: 4, day: 30 } }],
    sowOutdoor: [{ start: { month: 5, day: 15 }, end: { month: 6, day: 30 } }],
    harvest: [{ start: { month: 7, day: 1 }, end: { month: 10, day: 31 } }],
    description: 'Popular summer crop. Start indoors in late winter, transplant after last frost.',
    tips: ['Water consistently', 'Pinch out side shoots', 'Support plants with stakes']
  },
  {
    id: 'carrot',
    name: 'Carrot',
    slug: 'carrot',
    category: 'vegetable',
    sowOutdoor: [{ start: { month: 3, day: 1 }, end: { month: 7, day: 31 } }],
    harvest: [{ start: { month: 6, day: 1 }, end: { month: 11, day: 30 } }],
    description: 'Direct sow outdoors. Succession plant every 3 weeks.',
    tips: ['Thin seedlings', 'Keep soil moist', 'Use stone-free soil']
  },
  {
    id: 'lettuce',
    name: 'Lettuce',
    slug: 'lettuce',
    category: 'vegetable',
    sowIndoor: [{ start: { month: 2, day: 1 }, end: { month: 4, day: 30 } }],
    sowOutdoor: [{ start: { month: 3, day: 15 }, end: { month: 9, day: 15 } }],
    harvest: [{ start: { month: 5, day: 1 }, end: { month: 10, day: 31 } }],
    description: 'Fast-growing salad green.',
    tips: ['Harvest outer leaves', 'Provide shade in hot weather', 'Keep soil moist']
  }
];
