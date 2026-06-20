import React, { useState } from "react";

export default function SearchBar({ onSearch }) {
  const [query, setQuery] = useState("");

  return (
    <div style={{ display: "flex", gap: "12px", marginTop: "20px" }}>
      <input
        type="text"
        placeholder="Search product or paste product URL..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        style={{
          flex: 1,
          padding: "14px",
          borderRadius: "12px",
          border: "1px solid #ddd",
          fontSize: "16px"
        }}
      />
      <button
        onClick={() => onSearch(query)}
        style={{
          padding: "14px 22px",
          borderRadius: "12px",
          border: "none",
          background: "black",
          color: "white",
          cursor: "pointer"
        }}
      >
        Compare
      </button>
    </div>
  );
}