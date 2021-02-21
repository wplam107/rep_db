import { _firebase } from "./database.js"

const db = _firebase.firestore();

window._data = [];

async function getReps() {
    const snapshot = await db.collection("reps").limit(3).get();
    snapshot.docs.forEach((doc) => {
        _data.push(doc.data());
        console.log(doc.data());
    });
};

async function newText() {
    const result = await getReps();
    for (const [key, value] of Object.entries(_data[0])) {
        var body = document.querySelector("body");
        var text = document.createElement("div");
        var string = `${key}: ${key == "dob" ? new Date(value['seconds']*1000): value}`;
        text.innerText = string;
        body.appendChild(text);
    };
};

newText();