import firebase from "firebase/app";
import "firebase/firestore";
import { firebaseConfig } from "./config.js";
firebase.initializeApp(firebaseConfig);

export const _firebase = firebase;