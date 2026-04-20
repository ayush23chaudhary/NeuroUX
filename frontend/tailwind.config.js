module.exports = {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        neuroPurple: "#7c3aed",
        neuroBlue: "#3b82f6",
      },
      animation: {
        fadeIn: "fadeIn 0.3s ease-in",
        slideIn: "slideIn 0.4s ease-out",
      },
    },
  },
  plugins: [],
};
