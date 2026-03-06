---
name: aioz-ui-charts
description: Chart component reference for AIOZ UI V3. Covers LineChart, AreaChart, BarChart, and DonutChart from @aioz-ui/core/components, plus the useSeriesVisibility hook and CustomLegend component. Read this file whenever you need to build any chart, graph, or data visualization. All charts import from @aioz-ui/core/components (NOT @aioz-ui/core-v3/components).
---

# AIOZ UI V3 — Charts Reference

## ⚠️ Important: Different Import Path

Charts use a **different package** from other UI components:

```tsx
// ✅ Charts — import from @aioz-ui/core/components
import {
  LineChart,
  AreaChart,
  BarChart,
  DonutChart,
  CustomLegend,
  Separator,
  useSeriesVisibility,
} from '@aioz-ui/core/components'

// ✅ Other UI components — import from @aioz-ui/core-v3/components
import { Button, Input, Badge } from '@aioz-ui/core-v3/components'
```

---

## Available Chart Components

| Component             | Use For                                    |
| --------------------- | ------------------------------------------ |
| `LineChart`           | Trends over time, continuous data          |
| `AreaChart`           | Trends with volume emphasis (filled area)  |
| `BarChart`            | Category comparisons, grouped/stacked bars |
| `DonutChart`          | Part-to-whole proportions                  |
| `CustomLegend`        | Interactive toggle legend for multi-series |
| `useSeriesVisibility` | Hook — manages series show/hide state      |

---

## Core Concepts

### Series Format

**LineChart, AreaChart, BarChart** — array of objects:

```tsx
const series = [
  { name: 'Series Name', type: 'line' | 'area' | 'bar', data: number[] }
]
```

**DonutChart** — flat array of numbers (no `type` field):

```tsx
const series = [44, 55, 41, 17, 15]
```

### xaxis — Always provide both `categories` and `overwriteCategories`

```tsx
options={{
  xaxis: {
    categories: ['Monday', 'Tuesday', 'Wednesday', ...],  // full labels (used for tooltip)
    overwriteCategories: ['Mon', 'Tue', 'Wed', ...],      // short labels (shown on axis)
  }
}}
```

### Common Props (LineChart, AreaChart, BarChart)

| Prop      | Type     | Description                              |
| --------- | -------- | ---------------------------------------- |
| `width`   | `number` | Chart width in px                        |
| `height`  | `number` | Chart height in px                       |
| `series`  | `array`  | Data series (see format above)           |
| `options` | `object` | ApexCharts options (stroke, xaxis, etc.) |

### DonutChart Props

| Prop      | Type       | Description                         |
| --------- | ---------- | ----------------------------------- |
| `width`   | `number`   | Chart width in px                   |
| `series`  | `number[]` | Data values (flat array)            |
| `options` | `object`   | ApexCharts options (`labels`, etc.) |

---

## useSeriesVisibility Hook

Manages toggle visibility state for multi-series charts and feeds data to `CustomLegend`.

```tsx
import { useSeriesVisibility } from '@aioz-ui/core/components'

const { seriesVisibility, legendData, handleToggleVisibility } =
  useSeriesVisibility(series)
```

| Return Value             | Type        | Description                                          |
| ------------------------ | ----------- | ---------------------------------------------------- |
| `seriesVisibility`       | `boolean[]` | Index-matched visibility flags for each series       |
| `legendData`             | `object`    | Data passed to `<CustomLegend>`                      |
| `handleToggleVisibility` | `function`  | Called by `<CustomLegend>` to toggle a series on/off |

### Hiding a Series (when `seriesVisibility[index]` is false)

Different charts handle hidden series differently — **this is important**:

| Chart Type           | Hidden series data              |
| -------------------- | ------------------------------- |
| `LineChart`          | `curr.data.map(() => null)`     |
| `AreaChart`          | `curr.data.map(() => null)`     |
| `BarChart` (grouped) | `[]` (empty array)              |
| `BarChart` (stacked) | `curr.data.map(() => null)`     |
| `DonutChart`         | `seriesVisibility[i] ? val : 0` |

### Hook Input for DonutChart

For DonutChart, wrap the flat series array into the object format the hook expects:

```tsx
const series = [44, 55, 41, 17, 15]
const labels = ['Apple', 'Mango', 'Orange', 'Watermelon', 'Banana']

useSeriesVisibility(series.map((val, i) => ({ name: labels[i], data: [val] })))
```

---

## CustomLegend

An interactive legend that lets users toggle individual series on/off.

```tsx
import { CustomLegend } from '@aioz-ui/core/components'

{
  legendData && (
    <CustomLegend
      data={legendData}
      onToggleVisibility={handleToggleVisibility}
    />
  )
}
```

Always guard with `legendData &&` before rendering. Place it below the chart inside a `flex-col items-center gap-2` container.

---

## Chart Card Shell Pattern

All chart stories wrap charts in this standard card shell. Always use this layout:

```tsx
<div className="flex flex-col rounded-3xl border">
  {/* Header */}
  <div className="flex w-full flex-row items-center justify-between px-6 py-4">
    <span className="text-subheadline-01">Chart Title</span>
  </div>
  <Separator className="h-px w-full" />
  {/* Chart body */}
  <div className="flex w-full px-6 py-6">
    <LineChart ... />
  </div>
</div>
```

For charts with a legend, add `flex-col items-center gap-2` to the chart body div:

```tsx
<div className="flex w-full px-6 py-6 flex-col items-center gap-2">
  <LineChart ... />
  {legendData && (
    <CustomLegend data={legendData} onToggleVisibility={handleToggleVisibility} />
  )}
</div>
```

---

## 1. LineChart

### Variants

| Variant              | Key `options` prop                               |
| -------------------- | ------------------------------------------------ |
| Default (smooth)     | _(no stroke option needed)_                      |
| Linear (straight)    | `stroke: { curve: 'straight' }`                  |
| Step                 | `stroke: { curve: 'linestep' }`                  |
| Multiple series      | Pass multiple objects in `series`                |
| Multiple with dots   | `markers: { size: 6, hover: { sizeOffset: 2 } }` |
| Multiple with dashes | `stroke: { dashArray: [4, 12, 0] }`              |

> `dashArray` is per-series: index 0 = 4px dash, index 1 = 12px dash, index 2 = solid (0 = no dash).

### Single Series Example

```tsx
'use client'
import { LineChart, Separator } from '@aioz-ui/core/components'

const SERIES = [
  { name: 'Line 1', type: 'line', data: [0, 432, 212, 124, 354, 412, 754] },
]

const DefaultLineChart = () => {
  return (
    <div className="flex flex-col rounded-3xl border">
      <div className="flex w-full flex-row items-center justify-between px-6 py-4">
        <span className="text-subheadline-01">Line Chart</span>
      </div>
      <Separator className="h-px w-full" />
      <div className="flex w-full px-6 py-6">
        <LineChart
          width={500}
          height={300}
          series={SERIES}
          options={{
            xaxis: {
              categories: [
                'Monday',
                'Tuesday',
                'Wednesday',
                'Thursday',
                'Friday',
                'Saturday',
                'Sunday',
              ],
              overwriteCategories: [
                'Mon',
                'Tue',
                'Wed',
                'Thu',
                'Fri',
                'Sat',
                'Sun',
              ],
            },
          }}
        />
      </div>
    </div>
  )
}
```

### Multi-Series with Legend (full pattern)

```tsx
'use client'
import React from 'react'
import {
  LineChart,
  Separator,
  CustomLegend,
  useSeriesVisibility,
} from '@aioz-ui/core/components'

const SERIES = [
  { name: 'Line 1', type: 'line', data: [0, 432, 212, 124, 354, 412, 754] },
  { name: 'Line 2', type: 'line', data: [200, 50, 237, 546, 123, 675, 40] },
  { name: 'Line 3', type: 'line', data: [600, 214, 120, 750, 432, 624, 846] },
]

const MultipleLineChart = () => {
  const { seriesVisibility, legendData, handleToggleVisibility } =
    useSeriesVisibility(SERIES)

  const displaySeries = React.useMemo(() => {
    return SERIES.map((curr, index) => ({
      ...curr,
      data: seriesVisibility[index] ? curr.data : curr.data.map(() => null),
    }))
  }, [seriesVisibility])

  return (
    <div className="flex flex-col rounded-3xl border">
      <div className="flex w-full flex-row items-center justify-between px-6 py-4">
        <span className="text-subheadline-01">Line Chart - Multiple</span>
      </div>
      <Separator className="h-px w-full" />
      <div className="flex w-full flex-col items-center gap-2 px-6 py-6">
        <LineChart
          width={500}
          height={300}
          series={displaySeries}
          options={{
            xaxis: {
              categories: [
                'Monday',
                'Tuesday',
                'Wednesday',
                'Thursday',
                'Friday',
                'Saturday',
                'Sunday',
              ],
              overwriteCategories: [
                'Mon',
                'Tue',
                'Wed',
                'Thu',
                'Fri',
                'Sat',
                'Sun',
              ],
            },
          }}
        />
        {legendData && (
          <CustomLegend
            data={legendData}
            onToggleVisibility={handleToggleVisibility}
          />
        )}
      </div>
    </div>
  )
}
```

### With Dots

```tsx
options={{
  xaxis: { categories: [...], overwriteCategories: [...] },
  markers: { size: 6, hover: { sizeOffset: 2 } },
}}
```

### With Dashes (per-series dash pattern)

```tsx
options={{
  xaxis: { categories: [...], overwriteCategories: [...] },
  stroke: { dashArray: [4, 12, 0] }, // index-matched: series[0]=dash4, series[1]=dash12, series[2]=solid
}}
```

---

## 2. AreaChart

Identical API to LineChart, but `series[].type` is `'area'` instead of `'line'`.

### Variants

| Variant          | Key `options` prop                                  |
| ---------------- | --------------------------------------------------- |
| Default (smooth) | _(no stroke option needed)_                         |
| Linear           | `stroke: { curve: 'straight' }`                     |
| Stepped          | `stroke: { curve: 'linestep' }`                     |
| Multiple         | Pass multiple objects, use `null` for hidden series |

> Note: Area Stepped uses `'linestep'` (same as Line Step). The Storybook label says "stepline" but the actual code uses `'linestep'`.

### Single Series Example

```tsx
'use client'
import { AreaChart, Separator } from '@aioz-ui/core/components'

const SERIES = [
  { name: 'Area 1', type: 'area', data: [0, 432, 212, 124, 354, 412, 754] },
]

const DefaultAreaChart = () => {
  return (
    <div className="flex flex-col rounded-3xl border">
      <div className="flex w-full flex-row items-center justify-between px-6 py-4">
        <span className="text-subheadline-01">Area Chart</span>
      </div>
      <Separator className="h-px w-full" />
      <div className="flex w-full px-6 py-6">
        <AreaChart
          width={500}
          height={300}
          series={SERIES}
          options={{
            xaxis: {
              categories: [
                'Monday',
                'Tuesday',
                'Wednesday',
                'Thursday',
                'Friday',
                'Saturday',
                'Sunday',
              ],
              overwriteCategories: [
                'Mon',
                'Tue',
                'Wed',
                'Thu',
                'Fri',
                'Sat',
                'Sun',
              ],
            },
          }}
        />
      </div>
    </div>
  )
}
```

### Multi-Series with Legend

Same pattern as LineChart multi-series, but use `type: 'area'` in series and `AreaChart` component.

---

## 3. BarChart

### Variants

| Variant    | Key `options` prop                                                                    |
| ---------- | ------------------------------------------------------------------------------------- |
| Default    | _(no extra options needed)_                                                           |
| Grouped    | Multiple series, hidden series use `[]` (empty array, not null)                       |
| Stacked    | `chart: { stacked: true, animations: { enabled: false } }` + `plotOptions.bar` radius |
| Horizontal | `plotOptions: { bar: { horizontal: true } }`                                          |

### Single Series (Default)

```tsx
'use client'
import { BarChart, Separator } from '@aioz-ui/core/components'

const SERIES = [
  { name: 'Sales', type: 'bar', data: [44, 55, 41, 67, 22, 43, 21] },
]

const DefaultBarChart = () => {
  return (
    <div className="flex flex-col rounded-3xl border">
      <div className="flex w-full flex-row items-center justify-between px-6 py-4">
        <span className="text-subheadline-01">Bar Chart</span>
      </div>
      <Separator className="h-px w-full" />
      <div className="flex w-full px-6 py-6">
        <BarChart
          width={500}
          height={300}
          series={SERIES}
          options={{
            xaxis: {
              categories: [
                'Monday',
                'Tuesday',
                'Wednesday',
                'Thursday',
                'Friday',
                'Saturday',
                'Sunday',
              ],
              overwriteCategories: [
                'Mon',
                'Tue',
                'Wed',
                'Thu',
                'Fri',
                'Sat',
                'Sun',
              ],
            },
          }}
        />
      </div>
    </div>
  )
}
```

### Grouped (Multi-Series)

```tsx
'use client'
import React from 'react'
import {
  BarChart,
  Separator,
  CustomLegend,
  useSeriesVisibility,
} from '@aioz-ui/core/components'

const SERIES = [
  { name: 'Product A', type: 'bar', data: [44, 55, 41, 67, 22, 43, 21] },
  { name: 'Product B', type: 'bar', data: [13, 23, 20, 8, 13, 27, 33] },
  { name: 'Product C', type: 'bar', data: [11, 17, 15, 15, 21, 14, 15] },
]

const GroupedBarChart = () => {
  const { seriesVisibility, legendData, handleToggleVisibility } =
    useSeriesVisibility(SERIES)

  const displaySeries = React.useMemo(() => {
    return SERIES.map((curr, index) => ({
      ...curr,
      data: seriesVisibility[index] ? curr.data : [], // ← [] not null for grouped
    }))
  }, [seriesVisibility])

  return (
    <div className="flex flex-col rounded-3xl border">
      <div className="flex w-full flex-row items-center justify-between px-6 py-4">
        <span className="text-subheadline-01">Bar Chart - Grouped</span>
      </div>
      <Separator className="h-px w-full" />
      <div className="flex w-full flex-col items-center gap-2 px-6 py-6">
        <BarChart
          width={500}
          height={300}
          series={displaySeries}
          options={{
            xaxis: {
              categories: [
                'Monday',
                'Tuesday',
                'Wednesday',
                'Thursday',
                'Friday',
                'Saturday',
                'Sunday',
              ],
              overwriteCategories: [
                'Mon',
                'Tue',
                'Wed',
                'Thu',
                'Fri',
                'Sat',
                'Sun',
              ],
            },
          }}
        />
        {legendData && (
          <CustomLegend
            data={legendData}
            onToggleVisibility={handleToggleVisibility}
          />
        )}
      </div>
    </div>
  )
}
```

### Stacked

```tsx
// displaySeries uses null (not []) for hidden series in stacked mode
const displaySeries = React.useMemo(() => {
  return SERIES.map((curr, index) => ({
    ...curr,
    data: seriesVisibility[index] ? curr.data : curr.data.map(() => null), // ← null for stacked
  }))
}, [seriesVisibility])

// Options for stacked bar:
options={{
  chart: {
    stacked: true,
    animations: { enabled: false },
  },
  plotOptions: {
    bar: {
      borderRadiusWhenStacked: 'all',
      borderRadiusApplication: 'end',
    },
  },
  xaxis: {
    categories: [...],
    overwriteCategories: [...],
  },
}}
```

### Horizontal

```tsx
options={{
  plotOptions: { bar: { horizontal: true } },
  xaxis: {
    categories: [...],
    overwriteCategories: [...],
  },
}}
```

---

## 4. DonutChart

### Default (with Legend)

```tsx
'use client'
import React from 'react'
import {
  DonutChart,
  Separator,
  CustomLegend,
  useSeriesVisibility,
} from '@aioz-ui/core/components'

const SERIES = [44, 55, 41, 17, 15]
const LABELS = ['Apple', 'Mango', 'Orange', 'Watermelon', 'Banana']

const DefaultDonutChart = () => {
  const { seriesVisibility, legendData, handleToggleVisibility } =
    useSeriesVisibility(
      SERIES.map((val, i) => ({ name: LABELS[i], data: [val] })), // ← wrap for hook
    )

  const displaySeries = React.useMemo(() => {
    return SERIES.map((val, index) => (seriesVisibility[index] ? val : 0)) // ← 0 for hidden
  }, [seriesVisibility])

  return (
    <div className="flex flex-col rounded-3xl border">
      <div className="flex w-full flex-row items-center justify-between px-6 py-4">
        <span className="text-subheadline-01">Donut Chart</span>
      </div>
      <Separator className="h-px w-full" />
      <div className="flex w-full flex-col items-center gap-2 px-6 py-6">
        <DonutChart
          width={400}
          series={displaySeries}
          options={{ labels: LABELS }}
        />
        {legendData && (
          <CustomLegend
            data={legendData}
            onToggleVisibility={handleToggleVisibility}
          />
        )}
      </div>
    </div>
  )
}
```

> Note: `DonutChart` does **not** take a `height` prop — only `width`.

---

## Quick Decision Guide

| Goal                        | Chart      | Series type  | Hidden value    |
| --------------------------- | ---------- | ------------ | --------------- |
| Trend line over time        | LineChart  | `'line'`     | `null` per item |
| Trend with area fill        | AreaChart  | `'area'`     | `null` per item |
| Category comparison         | BarChart   | `'bar'`      | `[]`            |
| Stacked category comparison | BarChart   | `'bar'`      | `null` per item |
| Horizontal bars             | BarChart   | `'bar'`      | `[]`            |
| Part-to-whole proportions   | DonutChart | flat numbers | `0`             |
| Add dot markers to line     | LineChart  | `'line'`     | `null` per item |
| Add per-series dash styles  | LineChart  | `'line'`     | `null` per item |

---

## Common Mistakes to Avoid

```tsx
// ❌ Wrong import path for charts
import { LineChart } from '@aioz-ui/core-v3/components'

// ✅ Correct
import { LineChart } from '@aioz-ui/core/components'

// ❌ DonutChart with height prop
<DonutChart width={400} height={300} series={...} />

// ✅ DonutChart — no height
<DonutChart width={400} series={...} />

// ❌ Using [] for hidden series in stacked bar (breaks stacking)
data: seriesVisibility[index] ? curr.data : []

// ✅ Use null for stacked bar
data: seriesVisibility[index] ? curr.data : curr.data.map(() => null)

// ❌ Using null for hidden series in grouped bar (leaves gap placeholder)
data: seriesVisibility[index] ? curr.data : curr.data.map(() => null)

// ✅ Use [] for grouped bar
data: seriesVisibility[index] ? curr.data : []

// ❌ Missing overwriteCategories (axis shows full long labels)
options={{ xaxis: { categories: ['Monday', 'Tuesday', ...] } }}

// ✅ Always provide both
options={{ xaxis: { categories: ['Monday', ...], overwriteCategories: ['Mon', ...] } }}

// ❌ Rendering CustomLegend without guard
<CustomLegend data={legendData} onToggleVisibility={handleToggleVisibility} />

// ✅ Always guard with &&
{legendData && <CustomLegend data={legendData} onToggleVisibility={handleToggleVisibility} />}
```
