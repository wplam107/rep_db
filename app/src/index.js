// Firebase App (the core Firebase SDK) is always required and must be listed first

// If you are using v7 or any earlier version of the JS SDK, you should import firebase using namespace import
// import * as firebase from "firebase/app"

// If you enabled Analytics in your project, add the Firebase SDK for Analytics
// import "firebase/analytics";

// Add the Firebase products that you want to use
// import "firebase/auth";


// TODO: Replace the following with your app's Firebase project configuration
// For Firebase JavaScript SDK v7.20.0 and later, `measurementId` is an optional field


// Initialize Firebase
import { _firebase } from "./database.js"

const db = _firebase.firestore();

db.collection("reps").limit(3).get().then((querySnaphot) => {
    querySnaphot.forEach((doc) => {
        console.log(doc.data());
    });
});