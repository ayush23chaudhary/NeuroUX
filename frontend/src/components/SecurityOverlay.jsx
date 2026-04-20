import React from "react";
import { useNeuro } from "../context/NeuroProvider";

export default function SecurityOverlay() {
  const { isTrapActive, setIsTrapActive } = useNeuro();

  if (!isTrapActive) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
      <div className="bg-white rounded-lg p-8 w-96 text-center shadow-xl">
        <div className="mb-4">
          <div className="loader mb-3" />
          <h3 className="text-lg font-bold">Please verify</h3>
          <p className="text-sm text-gray-600">For security reasons, please complete the check.</p>
        </div>

        <div className="mt-4">
          <button
            className="px-4 py-2 bg-blue-600 text-white rounded mr-2"
            onClick={() => setIsTrapActive(false)}
          >
            I'm human
          </button>
          <button
            className="px-4 py-2 bg-gray-200 rounded"
            onClick={() => setIsTrapActive(false)}
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}
