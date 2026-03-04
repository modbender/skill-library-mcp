import { initializeApp } from "firebase-admin/app";

initializeApp();

export { tokenClient } from "./tokenClient";
export { authorize } from "./authorize";
export { callback } from "./callback";
export { tokenUser } from "./tokenUser";
export { tokenRefresh } from "./tokenRefresh";
