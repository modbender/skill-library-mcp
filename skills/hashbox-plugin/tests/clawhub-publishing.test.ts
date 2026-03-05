import { describe, it, expect } from 'vitest';
import { readFileSync } from 'fs';
import { join } from 'path';

const ROOT = join(__dirname, '..');

describe('SKILL.md', () => {
  const content = readFileSync(join(ROOT, 'SKILL.md'), 'utf-8');

  it('exists and is non-empty', () => {
    expect(content.length).toBeGreaterThan(0);
  });

  it('contains the plugin name', () => {
    expect(content).toContain('hashbox-plugin');
  });

  it('contains a description', () => {
    expect(content).toContain(
      'OpenClaw plugin that connects an AI agent to the HashBox iOS app'
    );
  });

  it('contains installation instructions', () => {
    expect(content).toContain('## Installation');
    expect(content).toContain('npm install hashbox-plugin');
  });

  it('documents configure_hashbox usage', () => {
    expect(content).toContain('### configure_hashbox');
    expect(content).toContain('configure_hashbox(');
  });

  it('documents send_hashbox_notification usage', () => {
    expect(content).toContain('### send_hashbox_notification');
    expect(content).toContain('send_hashbox_notification(');
  });

  it('documents HB- token requirement', () => {
    expect(content).toContain('HB-');
    expect(content).toContain('token');
  });

  it('contains dependencies section', () => {
    expect(content).toContain('## Dependencies');
  });

  it('contains setup section', () => {
    expect(content).toContain('## Setup');
  });
});

describe('package.json openclaw field', () => {
  const pkg = JSON.parse(
    readFileSync(join(ROOT, 'package.json'), 'utf-8')
  ) as {
    main: string;
    openclaw: {
      extensions: string;
      slots: string[];
      catalog: {
        name: string;
        description: string;
      };
    };
    files: string[];
  };

  it('has main pointing to root index.js', () => {
    expect(pkg.main).toBe('index.js');
  });

  it('has an openclaw field', () => {
    expect(pkg.openclaw).toBeDefined();
  });

  it('points extensions to ./dist/openclaw-entry.js', () => {
    expect(pkg.openclaw.extensions).toBe('./dist/openclaw-entry.js');
  });

  it('declares the tool slot', () => {
    expect(pkg.openclaw.slots).toEqual(['tool']);
  });

  it('includes catalog name', () => {
    expect(pkg.openclaw.catalog.name).toBe('hashbox-plugin');
  });

  it('includes catalog description', () => {
    expect(pkg.openclaw.catalog.description).toBeTruthy();
    expect(pkg.openclaw.catalog.description.length).toBeGreaterThan(10);
  });

  it('includes index.js in the files array', () => {
    expect(pkg.files).toContain('index.js');
  });

  it('includes SKILL.md in the files array', () => {
    expect(pkg.files).toContain('SKILL.md');
  });

  it('includes index.ts in the files array for OpenClaw TS runtime', () => {
    expect(pkg.files).toContain('index.ts');
  });

  it('includes src directory in the files array for OpenClaw TS runtime', () => {
    expect(pkg.files).toContain('src');
  });
});
