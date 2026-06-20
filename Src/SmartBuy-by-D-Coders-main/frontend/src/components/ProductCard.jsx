import React from "react";

export default function ProductCard({ item, best }) {
  return (
    <div
      style={{
        border: best ? "2px solid #10b981" : "1px solid #e5e7eb",
        borderRadius: "18px",
        padding: "20px",
        boxShadow: "0 8px 24px rgba(0,0,0,0.08)",
        background: "white"
      }}
    >
      {best && (
        <div style={{ color: "#10b981", fontWeight: "bold", marginBottom: "10px" }}>
          🔥 Best Deal
        </div>
      )}

      {item.image_url && (
        <img
          src={item.image_url}
          alt={item.product_name}
          style={{
            width: "100%",
            height: "180px",
            objectFit: "cover",
            borderRadius: "12px",
            marginBottom: "12px"
          }}
        />
      )}

      <h3 style={{ fontSize: "18px", marginBottom: "10px" }}>{item.product_name}</h3>
      <p><b>Platform:</b> {item.platform}</p>
      <p><b>Price:</b> ₹ {item.current_price}</p>
      <p><b>Rating:</b> ⭐ {item.rating}</p>
      <p><b>Score:</b> {item.smartbuy_score}</p>

      <div style={{ marginTop: "10px", marginBottom: "14px" }}>
        <span
          style={{
            background: item.recommendation === "BUY NOW" ? "#dcfce7" : "#fee2e2",
            padding: "6px 12px",
            borderRadius: "20px",
            fontWeight: "bold"
          }}
        >
          {item.recommendation}
        </span>
      </div>

      {item.product_url && (
        <a href={item.product_url} target="_blank" rel="noreferrer">
          <button
            style={{
              width: "100%",
              padding: "12px",
              borderRadius: "12px",
              border: "none",
              background: "black",
              color: "white",
              cursor: "pointer"
            }}
          >
            Buy Now 🔗
          </button>
        </a>
      )}
    </div>
  );
}