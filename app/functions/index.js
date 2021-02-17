// const functions = require("firebase-functions");
const admin = require("firebase-admin");

const serviceAccount = require(
    "./auth/rep-database-firebase-adminsdk-5mjsx-1632bf8f78.json"
);

admin.initializeApp({
    credential: admin.credential.cert(serviceAccount)
});

const db = admin.firestore();
const repsRef = db.collection("reps");

const docsSnapshot = repsRef.limit(3).get();
const repsData = docsSnapshot.map(doc => {
    doc.data();
});

repsData.forEach(rep => {
    console.log(rep);
});