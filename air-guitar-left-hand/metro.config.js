const { getDefaultConfig } = require("expo/metro-config");
const { withNativeWind } = require("nativewind/metro");

const config = getDefaultConfig(__dirname);

// Add resolver extra options for react-native-webrtc and react-native-peerjs
config.resolver.resolverMainFields = ['react-native', 'browser', 'main'];
config.resolver.sourceExts = [...config.resolver.sourceExts, 'mjs', 'cjs'];
config.resolver.assetExts = [...config.resolver.assetExts, 'bcn'];

// Add extraNodeModules for peerjs dependencies
config.resolver.extraNodeModules = {
  ...config.resolver.extraNodeModules,
  'peerjs': require.resolve('peerjs'),
  'react-native-peerjs': require.resolve('react-native-peerjs'),
};

// Ensure proper blocklist for native modules
config.resolver.blockList = [
  /node_modules\/.*\/node_modules\/react-native\/.*/,
];

module.exports = withNativeWind(config, {
  input: "./global.css",
  // Force write CSS to file system instead of virtual modules
  // This fixes iOS styling issues in development mode
  forceWriteFileSystem: true,
});
