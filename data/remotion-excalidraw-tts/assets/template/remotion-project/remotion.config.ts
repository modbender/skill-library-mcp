/**
 * Note: When using the Node.JS APIs, the config file
 * doesn't apply. Instead, pass options directly to the APIs.
 *
 * All configuration options: https://remotion.dev/docs/config
 */

import {Config} from '@remotion/cli/config';
import {enableTailwind} from '@remotion/tailwind-v4';
import type {WebpackOverrideFn} from 'remotion';

Config.setVideoImageFormat('jpeg');
Config.setOverwriteOutput(true);

const override: WebpackOverrideFn = (current) => {
  // Tailwind
  const withTailwind = enableTailwind(current);

  // Fix ESM fully-specified import used by Excalidraw (roughjs/bin/rough)
  // by disabling `fullySpecified` for JS/ESM resolution.
  withTailwind.module = withTailwind.module ?? {rules: []};
  withTailwind.module.rules = withTailwind.module.rules ?? [];
  withTailwind.module.rules.push({
    test: /\.m?js$/,
    resolve: {
      fullySpecified: false,
    },
  });

  return withTailwind;
};

Config.overrideWebpackConfig(override);
