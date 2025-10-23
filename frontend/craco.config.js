// Load configuration from environment or config file
const path = require('path');

// Environment variable overrides
const config = {
  disableHotReload: process.env.DISABLE_HOT_RELOAD === 'true',
};

module.exports = {
  webpack: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
    configure: (webpackConfig) => {
      
      // Fix source-map-loader issues with node_modules
      webpackConfig.module.rules = webpackConfig.module.rules.map(rule => {
        if (rule.enforce === 'pre' && rule.use) {
          const useArray = Array.isArray(rule.use) ? rule.use : [rule.use];
          const sourceMapLoaderIndex = useArray.findIndex(
            item => item.loader && item.loader.includes('source-map-loader')
          );
          
          if (sourceMapLoaderIndex !== -1) {
            // Exclude problematic node_modules from source-map-loader
            rule.exclude = [
              /node_modules\/cookie/,
              /node_modules\/react-snap/,
              /node_modules\/@babel/,
              ...(rule.exclude ? [rule.exclude] : [])
            ];
          }
        }
        return rule;
      });
      
      // Disable hot reload completely if environment variable is set
      if (config.disableHotReload) {
        // Remove hot reload related plugins
        webpackConfig.plugins = webpackConfig.plugins.filter(plugin => {
          return !(plugin.constructor.name === 'HotModuleReplacementPlugin');
        });
        
        // Disable watch mode
        // # ignored is READONLY, DO NOT EDIT THIS
        webpackConfig.watch = false;
        webpackConfig.watchOptions = {
          ignored: /.*/, // Ignore all files
        };
      } else {
        // Add ignored patterns to reduce watched directories
        // IMPORTANT: ignored list can only be appended, but not overridden
        webpackConfig.watchOptions = {
          ...webpackConfig.watchOptions,
          ignored: [
            '**/node_modules/**',
            '**/.git/**',
            '**/build/**',
            '**/dist/**',
            '**/coverage/**',
            '**/public/**',
          ],
        };
      }
      
      // Suppress source map warnings from node_modules
      webpackConfig.ignoreWarnings = [
        /Failed to parse source map/,
        /source-map-loader/,
      ];
      
      return webpackConfig;
    },
  },
};