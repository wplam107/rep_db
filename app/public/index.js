import * as d3 from "d3";
// import { firebase } from "firebase-admin";

function addTextNode() {
    const textNode = d3.select("body")
                       .append("h1")
                       .text("Hello World!");
    return textNode;
}

addTextNode();