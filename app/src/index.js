import * as d3 from "d3";
import { _firebase } from "./database.js"

const db = _firebase.firestore();

window._data = [];

async function getReps() {
  const snapshot = await db.collection("reps").get();
  snapshot.docs.forEach((doc) => {
    const rep = doc.data();
    const newDate = new Date(doc.data()['dob']['seconds'] * 1000);
    rep['dob'] = newDate.toUTCString();
    _data.push(rep);
  });
};

// async function newText() {
//     await getReps();
//     for (const [key, value] of Object.entries(_data[0])) {
//         var body = document.querySelector("body");
//         var text = document.createElement("div");
//         var string = `${key}: ${value}`;
//         text.innerText = string;
//         body.appendChild(text);
//     };
// };

// newText();

async function getStates() {
  await getReps();
  var states = {};
  _data.forEach((rep) => {
    var state = rep['state'];
    states[state] === undefined ? states[state] = 1 : states[state] += 1;
  });
  return states;
}

async function barPlot() {
  const statesObj = await getStates();
  const dataset = [];
  for (const [key, value] of Object.entries(statesObj)) {
    dataset.push([key, value]);
  };
  dataset.sort((a, b) => b[1] - a[1]);

  const margin = ({top: 20, right: 0, bottom: 30, left: 40});
  const width = 400;
  const height = 200;
  const yScale = d3.scaleLinear()
    .domain([0, d3.max(dataset, d => d[1])])
    .range([height - margin.bottom, margin.top]);
  const xScale = d3.scaleBand()
    .domain(dataset.map(d => d[0]))
    .rangeRound([margin.left, width - margin.right])
    .padding(0.1)
    .attr();

  const svg = d3.select("body").append("svg")
    .attr("viewBox", [0, 0, width, height]);

  svg.append("g")
    .attr("transform", `translate(0,${height - margin.bottom})`)
    .call(d3.axisBottom(xScale));

  svg.append("g")
    .attr("transform", `translate(${margin.left},0)`)
    .call(d3.axisLeft(yScale));
  
  const yTitle = g => g.append("text")
    .attr("font-family", "sans-serif")
    .attr("font-size", 10)
    .attr("y", 10)
    .text("Number of Reps");

  const yAxis = g => g
    .attr("transform", `translate(${margin.left},0)`)
    .call(d3.axisLeft(yScale).ticks(null))
    .call(g => g.select(".domain").remove());

  const xAxis = g => g
    .attr("transform", `translate(0,${height - margin.bottom})`)
    .call(d3.axisBottom(xScale).tickSizeOuter(0).attr("font-size", 5));

  svg.append("g")
      .attr("fill", "steelblue")
    .selectAll("rect")
    .data(dataset)
    .join("rect")
      .attr("x", d => xScale(d[0]))
      .attr("y", d => yScale(d[1]))
      .attr("height", d => yScale(0) - yScale(d[1]))
      .attr("width", xScale.bandwidth());

  svg.append("g")
      .call(xAxis);

  svg.append("g")
      .call(yAxis);

  svg.call(yTitle);

  // const svg = d3.select("body").append("svg")
  //   .attr("width", width)
  //   .attr("height", yScale.range()[1])
  //   .attr("font-family", "sans-serif")
  //   .attr("font-size", "10")
  //   .attr("text-anchor", "end");

  // const bar = svg.selectAll("g")
  //   .data(dataset)
  //   .join("g")
  //     .attr("transform", (d, i) => `translate(0,${yScale(i)})`);

  // bar.append("rect")
  //   .attr("fill", "steelblue")
  //   .attr("width", d => xScale(d[1]))
  //   .attr("height", yScale.bandwidth() - 1);

  // bar.append("text")
  //   .attr("fill", "white")
  //   .attr("x", d => xScale(d[1]) - 3)
  //   .attr("y", yScale.bandwidth() / 2)
  //   .attr("dy", "0.35em")
  //   .text(d => d[0]);

  return svg.node();
}

barPlot();

// const margin = ({top: 20, right: 0, bottom: 30, left: 40});


// async function makePlot() {
//     const statesObj = await getStates();
//     const dataset = [];
//     for (const [key, value] of Object.entries(statesObj)) {
//         dataset.push([key, value]);
//     };
//     dataset.sort((a, b) => b[1] - a[1]);
//     const h = 500;
//     const w = 1000;
//     const stateLength = dataset.length;
//     const padding = 50;
//     const spacing = 3;
//     const xScale = d3.scaleLinear()
//                      .domain([0, stateLength - 1])
//                      .range([padding, w - padding]);
//     const yScale = d3.scaleLinear()
//                      .domain([0, d3.max(dataset, (d, i) => d[1])])
//                      .range([h - padding, padding]);
//     const svg = d3.select("body")
//                   .append("svg")
//                   .attr("width", w)
//                   .attr("height", h);

//     svg.selectAll("rect")
//        .data(dataset)
//        .enter()
//        .append("rect")
//        .attr("x", (d, i) => xScale(i))
//        .attr("y", (d, i) => yScale(d[1] + spacing / 4))
//        .attr("width", w / stateLength - spacing)
//        .attr("height", (d, i) => h - yScale(d[1]));
//     svg.selectAll("text")
//        .data(dataset)
//        .enter()
//        .append("text")
//        .attr("x", (d, i) => xScale(i) + spacing / 4)
//        .attr("y", (d, i) => h)
//        .text((d, i) => d[0])
//        .style("font-size", 8)
//        .style("font-family", "monospace");
    
// }

// makePlot();