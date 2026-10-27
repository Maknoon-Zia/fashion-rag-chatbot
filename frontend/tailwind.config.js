/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#fbf5f6", 100: "#f5e6e9", 200: "#ebcdd3", 300: "#dca9b3", 400: "#c97b8b",
          500: "#b45a6e", 600: "#9a4559", 700: "#7e384a", 800: "#672f3f", 900: "#552a37",
        },
      },
      fontFamily: { display: ["Georgia", "Cambria", "Times New Roman", "serif"] },
    },
  },
  plugins: [],
};
