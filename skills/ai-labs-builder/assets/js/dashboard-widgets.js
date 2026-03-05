// Dashboard Widget System
// Inspired by Anselmo's Daily Brief Dashboard

class WidgetSystem {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.widgets = new Map();
    this.layout = JSON.parse(localStorage.getItem('dashboard-layout') || '[]');
  }

  // Register a widget
  register(name, config) {
    this.widgets.set(name, {
      name,
      title: config.title || name,
      render: config.render,
      refresh: config.refresh || null,
      interval: config.interval || null,
      ...config
    });
  }

  // Add widget to dashboard
  add(widgetName, position = null) {
    const widget = this.widgets.get(widgetName);
    if (!widget) {
      console.error(`Widget '${widgetName}' not found`);
      return;
    }

    const id = `widget-${Date.now()}`;
    const el = document.createElement('div');
    el.className = 'widget';
    el.id = id;
    el.innerHTML = `
      <div class="widget-header">
        <span class="widget-title">${widget.title}</span>
        <div class="widget-actions">
          ${widget.refresh ? '<button onclick="refreshWidget(\'' + id + '\')">↻</button>' : ''}
          <button onclick="removeWidget(\'' + id + '\')">×</button>
        </div>
      </div>
      <div class="widget-content" id="${id}-content"></div>
    `;

    if (position !== null && this.container.children[position]) {
      this.container.insertBefore(el, this.container.children[position]);
    } else {
      this.container.appendChild(el);
    }

    // Render widget content
    const contentEl = document.getElementById(`${id}-content`);
    widget.render(contentEl);

    // Set up auto-refresh
    if (widget.interval) {
      setInterval(() => {
        if (widget.refresh) {
          widget.refresh(contentEl);
        }
      }, widget.interval);
    }

    this.saveLayout();
    return id;
  }

  // Remove widget
  remove(id) {
    const el = document.getElementById(id);
    if (el) {
      el.remove();
      this.saveLayout();
    }
  }

  // Refresh widget
  refresh(id) {
    // Implementation depends on widget type
  }

  // Save layout to localStorage
  saveLayout() {
    const layout = Array.from(this.container.children).map(el => ({
      id: el.id,
      name: el.dataset.widgetName
    }));
    localStorage.setItem('dashboard-layout', JSON.stringify(layout));
  }

  // Load saved layout
  loadLayout() {
    const layout = JSON.parse(localStorage.getItem('dashboard-layout') || '[]');
    layout.forEach(item => {
      if (item.name && this.widgets.has(item.name)) {
        this.add(item.name);
      }
    });
  }
}

// Pre-built Widgets

const WeatherWidget = {
  title: '🌤️ Weather',
  interval: 60000, // 1 minute
  render: (el) => {
    el.innerHTML = '<div class="weather-loading">Loading...</div>';
    fetchWeather().then(data => {
      el.innerHTML = `
        <div class="weather-main">
          <span class="weather-temp">${data.temp}°</span>
          <span class="weather-desc">${data.description}</span>
        </div>
        <div class="weather-details">
          <span>💧 ${data.humidity}%</span>
          <span>💨 ${data.wind} km/h</span>
        </div>
      `;
    });
  },
  refresh: (el) => {
    // Re-render
  }
};

const ClockWidget = {
  title: '🕐 Clock',
  interval: 1000, // 1 second
  render: (el) => {
    const update = () => {
      const now = new Date();
      el.innerHTML = `
        <div class="clock-time">${now.toLocaleTimeString()}</div>
        <div class="clock-date">${now.toLocaleDateString()}</div>
      `;
    };
    update();
    setInterval(update, 1000);
  }
};

const TodoWidget = {
  title: '✅ Tasks',
  render: (el) => {
    const todos = JSON.parse(localStorage.getItem('todos') || '[]');
    el.innerHTML = `
      <ul class="todo-list">
        ${todos.map(todo => `<li>${todo}</li>`).join('')}
      </ul>
      <input type="text" class="todo-input" placeholder="Add task...">
    `;
    
    const input = el.querySelector('.todo-input');
    input.addEventListener('keypress', (e) => {
      if (e.key === 'Enter' && input.value) {
        todos.push(input.value);
        localStorage.setItem('todos', JSON.stringify(todos));
        input.value = '';
      }
    });
  }
};

// Helper functions
async function fetchWeather() {
  // Mock implementation
  return {
    temp: 22,
    description: 'Partly cloudy',
    humidity: 65,
    wind: 12
  };
}

// Export
if (typeof module !== 'undefined') {
  module.exports = { WidgetSystem, WeatherWidget, ClockWidget, TodoWidget };
}
