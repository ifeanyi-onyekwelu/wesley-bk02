/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/**/*.html"],
  theme: {
    extend: {
      colors: {
        text: "#0971FE",
        background_primary: "#101924",
        background_hover: "#162332",
      },
    },
  },
  plugins: [],
};
