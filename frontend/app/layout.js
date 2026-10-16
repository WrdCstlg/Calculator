import "./globals.css";

export const metadata = {
  title: "QuantumCalc | Next.js & Python Scientific Calculator Studio",
  description: "Advanced Scientific & Graphing Calculator powered by Next.js and Python (SymPy, NumPy, SciPy, Pandas)",
  keywords: ["Scientific Calculator", "Python", "Next.js", "SymPy", "Graphing", "Calculus", "Matrices", "Pandas Statistics"],
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body>{children}</body>
    </html>
  );
}
