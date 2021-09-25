const path = require('path');

module.exports = {
  outputDir: path.resolve(__dirname, '../static'),
  assetsDir: '../static',
  output: {
    filename: 'index.html',
    path: path.resolve(__dirname, '../templates'),
  },
};
