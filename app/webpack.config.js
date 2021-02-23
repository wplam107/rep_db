const path = require('path');

module.exports = {
  entry: {
    database: './src/database.js',
    index: {
      import: './src/index.js',
      dependOn: ['database'],
    },
  },
  output: {
    filename: '[name].bundle.js',
    path: path.resolve(__dirname, 'public'),
  },
};