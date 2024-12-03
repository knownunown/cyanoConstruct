module.exports = {
  purge: ['/index.html', './src/**/*.{ts,tsx,vue}'],
  darkMode: false, // or 'media' or 'class'
  theme: {
    extend: {
        minHeight: {
            '16': '4rem',
        }
    },
  },
  variants: {
    extend: {},
  },
  plugins: [],
}
