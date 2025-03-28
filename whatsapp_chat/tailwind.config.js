const path = require('path');

module.exports = {
  presets: [require('frappe-ui/src/utils/tailwind.config')],
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}',
    path.resolve(__dirname, './node_modules/frappe-ui/src/components/**/*.{vue,js,ts,jsx,tsx}'),
    path.resolve(__dirname, '../node_modules/frappe-ui/src/components/**/*.{vue,js,ts,jsx,tsx}')
  ],
  safelist: [
    { pattern: /^(text|bg)-/, variants: ['hover', 'active', 'focus'] },
    { pattern: /^grid-cols-/ },
    'bg-gray-600',
    'text-white',
    'bg-white',
    'text-gray-800',
    'text-gray-400'
  ],
  theme: {
    extend: {},
  },
  plugins: [],
};
