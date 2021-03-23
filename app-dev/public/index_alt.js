
const db = firebase.firestore();

const width = window.innerWidth * 0.45;
const height = window.innerHeight * 0.45;

/*
Text Label and SVG elements and borders
*/
const stateClickLabel = d3.select("#state-click-label")
	.text(`State Selected: ${stateId}`);
const usaSvg = d3.select("#usa-container")
	.append("svg")
	.attr("width", width)
	.attr("height", height)
	.attr("id", "usa-map")
	.attr("class", "map-svg")
	.attr("preserveAspectRatio", "xMinYMin meet")
  .attr("viewBox", "0 0 300 300")
  .classed("svg-content", true);
const usaG = usaSvg.append("g");
const stateSvg = d3.select("#state-container")
	.append("svg")
	.attr("width", width)
	.attr("height", height)
	.attr("id", "state-map")
	.attr("class", "map-svg")
	.attr("preserveAspectRatio", "xMinYMin meet")
  .attr("viewBox", "0 0 300 300")
  .classed("svg-content", true);
const stateG = stateSvg.append("g");
const repsBox = d3.select("#reps");

/*
Color schemes
*/
const colors = [
	"#855C75", "#D9AF6B", "#AF6458", "#736F4C", "#526A83", "#625377",
	"#68855C", "#9C9C5E", "#A06177", "#8C785D", "#467378", "#7C7C7C"
];
function colorScale(t) {
  return d3.interpolateCividis(t);
}

/*
Data
*/
const reps = window.sessionStorage;
const genderData = Array();
const getGenderData = db.collection("state_gender").get().then((snapshot) => {
  snapshot.docs.forEach((doc) => {
    var m = doc.data()["M"];
    var f = doc.data()["F"];
    var total = m + f;
    m = m / total;
    f = f / total;
    genderData[doc.data()["_id"]] = {"M": m, "F": f};
  });
});
const eduData = Array();
const getEduData = db.collection("state_edu").get().then((snapshot) => {
  snapshot.docs.forEach((doc) => {
    const total = doc.data()["count"];
    const state = doc.data()["_id"];
    eduData[state] = {};
    const eduDegrees = Object.keys(doc.data());
    eduDegrees.forEach((degree) => {
      if (degree !== "_id" && degree !== "count") {
        const count = doc.data()[degree];
        eduData[state][degree] = count / total;
      } else if (degree == "count") {
        const count = doc.data()[degree];
        eduData[state][degree] = count;
      };
    });
  });
});

/*
Defaults
*/
var stateId = "AL";

/*
National map
*/
Promise.all([getGenderData]).then(nationalMap);
function nationalMap() {
	const projCountry = d3.geoIdentity()
	const statePath = d3.geoPath(projCountry);
	const usaTopo = d3.json("data/usa.topo.json");
	usaTopo.then((usa) => {
		var states = topojson.feature(usa, usa.objects.data);
		projCountry.fitSize([width*0.85, height*0.85], states);
		usaG.selectAll("path")
			.data(states.features)
			.enter()
			.append("path")
			.attr("d", statePath)
			.attr("class", "state")
			.attr("fill", (d, i) => colorScale(genderData[d.properties.id]["M"]))
			.attr("id", (d) => d.properties.id)
			.attr("data", "none")
			.attr("transform", "translate(0, 10)")
			.on("mouseover", mouseOverHandler)
			.on("mousemove", mouseMoveHandler)
			.on("mouseout", mouseOutHandler)
			.on("click", clickHandler);
	});
}

/*
Zoom for national map
*/
const nationZoom = d3.zoom()
    .scaleExtent([1, 8])
    .on("zoom", nationZoomed);
function nationZoomed() {
	usaG.selectAll("path")
		.attr("transform", d3.event.transform);
}
usaSvg.call(nationZoom);

/*
State map
*/
Promise.all([nationalMap]).then(stateMap);
function stateMap() {
  const stateTopo = d3.json(`data/${stateId}.topo.json`);
  stateTopo.then((state) => {
    stateClickLabel.text(`State Selected: ${stateId}`);
    var cds = topojson.feature(state, state.objects.data);
    var projState = d3.geoMercator();
    var cdPath = d3.geoPath(projState);
    projState.fitSize([width*0.8, height*0.8], cds);
    Promise.all([getReps])
      .then(function() {
        stateG.selectAll("path")
          .data(cds.features)
          .enter()
          .append("path")
          .attr("d", cdPath)
          .attr("class", "cd")
          .attr("id", (d) => {
            if (d.properties.cd116 == "98") {
              return "cd00";
            } else {
              return `cd${d.properties.cd116}`;
            };
          })
          .attr("data", "none")
          .attr("transform", "translate(10, 10)")
          .on("mouseover", mouseOverHandler)
          .on("mousemove", mouseMoveHandler)
          .on("mouseout", mouseOutHandler)
          .on("click", districtClick);
      })
      .then(fillDistricts);
  });
}

function getReps() {
  if (reps.getItem(stateId) === null) {
    db.collection("reps").where("state", "==", `${stateId}`)
      .get()
      .then((snapshot) => {
        var stateReps = {};
        snapshot.forEach((doc) => {
          if (doc.data()['district'] == "At-Large") {
            var district = "00";
          } else {
            var district = doc.data()['district'].toLocaleString('en-US', {
              minimumIntegerDigits: 2,
              useGrouping: false
            });
          };
          stateReps[`cd${district}`] = doc.data();
        });
        reps.setItem(`${stateId}`, JSON.stringify(stateReps));
      });
  };
}

function fillDistricts() {
  var stateReps = JSON.parse(reps[stateId]);
  for (var key in stateReps) {
    d3.select(`#${key}`)
      .attr("fill", colorScale(stateReps[key]["gender"] == "M" ? 1 : 0));
  };
}

/*
Zoom for state map
*/
const stateZoom = d3.zoom()
    .scaleExtent([1, 10])
    .on("zoom", stateZoomed);
function stateZoomed() {
	stateG.selectAll("path")
		.attr("transform", d3.event.transform);
}
stateSvg.call(stateZoom);

/*
Event handlers
*/
var tooltip = d3.select("body").append("div")	
    .attr("class", "tooltip")				
    .style("opacity", 0);
function mouseOverHandler(d) {
	d3.select(this).style("opacity", 1);
	tooltip.style("hidden", false);
}
function mouseMoveHandler(d) {
	tooltip.transition()
		.duration(50)
		.style("opacity", 0.9);
	tooltip.html(d.id)
		.style("left", `${d3.event.pageX}px`)
		.style("top", `${d3.event.pageY - 25}px`);
	if (d.properties.cd116) {
		var region = "District";
	} else {
		var region = "State";
	};
	if (this.id == "cd00") {
		var regionId = "At-Large";
	} else {
		var regionId = `${this.id}`;
	};
	if (region == "District" && regionId !== "At-Large") {regionId = regionId.slice(2)};
	tooltip.html(d.id)
		.style("width", `${(region.length + regionId.length + 4) * 8}px`);
	tooltip.text(`${region}: ${regionId}\n${stateData[this.id]}`);
}
function mouseOutHandler() {
	var ifClicked = d3.select(this).attr("data");
	tooltip.transition()
		.duration(50)
		.style("opacity", 0);
}
function clickHandler(d, i) {
	d3.selectAll(".state")
		.attr("data", "none")
		.attr("stroke", "none");
	d3.select(this)
		.attr("data", "clicked")
		.attr("stroke", "white")
		.attr("stroke-width", "0.2%");
	stateId = d.properties.id;
  d3.selectAll(".cd").remove();
  stateMap();
}

function districtClick(d) {
	var stateReps = JSON.parse(reps.getItem(stateId));
	d3.selectAll(".cd")
		.attr("data", "none")
		.attr("stroke", "none")
	d3.select(this)
		.attr("data", "clicked")
		.attr("stroke", "white")
		.attr("stroke-width", "0.2%")
	d3.select(".district-member").remove();
	var district = this.id;
	repsBox.append("h3")
		.attr("class", "district-member")
		.text(stateReps[district].name);
}

/*
Selections
*/
Promise.all([getEduData]).then(makeEduDropdown);
function makeEduDropdown() {
  d3.select("#edu-dropdown")
    .selectAll("options")
    .data(Object.keys(eduData["AL"]))
    .enter()
    .append("option")
    .text((d) => d)
    .attr("value", (d) => d);
};
function updateFill() {
  
}