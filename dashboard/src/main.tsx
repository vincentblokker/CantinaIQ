import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import * as Tooltip from "@radix-ui/react-tooltip";
import App from "./App";
import "./i18n";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <Tooltip.Provider delayDuration={150}>
        <App />
      </Tooltip.Provider>
    </BrowserRouter>
  </React.StrictMode>,
);
