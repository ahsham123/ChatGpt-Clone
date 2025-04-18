/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./public/index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#343541',
        sidebar: '#202123',
        accent: '#10a37f',
        assistant: '#444654',
      },
    },
  },
  plugins: [],
};
