/** @type {import('tailwindcss').Config} */
// Tailwind v3 config. Mirrors the defaults the Play CDN used (no custom theme).
module.exports = {
  content: ['./index.html', './js/**/*.js'],
  theme: {
    extend: {},
  },
  plugins: [],
};
