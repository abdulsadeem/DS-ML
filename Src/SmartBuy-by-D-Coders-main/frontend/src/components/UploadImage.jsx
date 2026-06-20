import React from "react";

export default function UploadImage({ onUpload }) {
  return (
    <input
      type="file"
      accept="image/*"
      onChange={(e) => onUpload(e.target.files[0])}
    />
  );
}