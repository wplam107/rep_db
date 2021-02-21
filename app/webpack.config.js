const path = require('path');

module.exports = {
  entry: {
    database: ['firebase/app', 'firebase/firestore'],
    index: {
      import: './src/index.js',
      dependOn: 'database',
    },
  },
  output: {
    filename: '[name].bundle.js',
    path: path.resolve(__dirname, 'public'),
  },
};