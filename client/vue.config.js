const path = require('path');
const WebpackAssetsManifest = require('webpack-assets-manifest');

module.exports = {
  outputDir: path.resolve(__dirname, '../indice_pollution/static'),
  configureWebpack: config => {
    config.plugins = config.plugins.concat(
      new WebpackAssetsManifest()
    )
  }
};
