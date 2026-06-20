import React, { useState } from "react";
import SearchBar from "../components/SearchBar.jsx";
import ProductCard from "../components/ProductCard.jsx";

export default function Home() {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async (query) => {
    if (!query.trim()) return;
    setLoading(true);

    try {
      const res = await fetch("http://127.0.0.1:8000/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query })
      });

      const data = await res.json();
      setResults(data.results || []);
    } catch (error) {
      console.error(error);
      alert("Backend not reachable");
    }

    setLoading(false);
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#f8fafc",
        padding: "40px",
        fontFamily: "Arial"
      }}
    >
      <h1 style={{ fontSize: "42px", marginBottom: "8px" }}>🛍️ SmartBuy AI</h1>
      <p style={{ color: "#475569", marginBottom: "20px" }}>
        Compare live prices across Amazon, Flipkart, Myntra, Ajio & Meesho
      </p>

      <SearchBar onSearch={handleSearch} />

      {loading && <p style={{ marginTop: "20px" }}>Loading best deals...</p>}

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
          gap: "20px",
          marginTop: "30px"
        }}
      >
        {results.map((item, i) => (
          <ProductCard key={i} item={item} best={i === 0} />
        ))}
      </div>
    </div>
  );
}



