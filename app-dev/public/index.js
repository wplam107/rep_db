const width = window.innerWidth * 0.45;
const height = window.innerHeight * 0.45;
var stateId = "AL";

/*
Text Label and SVG elements and borders
*/
const stateClickLabel = d3.select("#state-click-label")
	.text(`State Selected: ${stateId}`);
const districtClickLabel = d3.select("#district-click-label")
	.text("District Selected:");
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
const stateG = stateSvg.append("g")

/*
Color schemes
*/
const colors = [
	"#855C75", "#D9AF6B", "#AF6458", "#736F4C", "#526A83", "#625377",
	"#68855C", "#9C9C5E", "#A06177", "#8C785D", "#467378", "#7C7C7C"
];
const stateColors = d3.scaleOrdinal().domain([0, 51]).range(colors);

/*
National map
*/
const projCountry = d3.geoIdentity()
const statePath = d3.geoPath(projCountry);
const usaTopo = d3.json("data/USA.topo.json");
usaTopo.then((usa) => {
	var states = topojson.feature(usa, usa.objects.data);
	projCountry.fitSize([width*0.9, height*0.9], states);
	usaG.selectAll("path")
		.data(states.features)
		.enter()
		.append("path")
		.attr("d", statePath)
		.attr("class", "state")
		.attr("fill", (d, i) => stateColors(i))
		.attr("id", (d) => d.properties.id)
		.attr("data", "none")
		.style("opacity", 0.7)
		.on("mouseover", mouseOverHandler)
		.on("mousemove", mouseMoveHandler)
		.on("mouseout", mouseOutHandler)
		.on("click", clickHandler);
});

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
Default state map
*/
const defaultStateTopo = d3.json(`data/${stateId}.topo.json`);
defaultStateTopo.then((state) => {
	var cds = topojson.feature(state, state.objects.data);
	var projState = d3.geoIdentity().reflectY(true);
	var cdPath = d3.geoPath(projState);
	var b = cdPath.bounds(cds);
	var s = .95 / Math.max((b[1][0] - b[0][0]) / width, (b[1][1] - b[0][1]) / height);
  var t = [(width - s * (b[1][0] + b[0][0])) / 2, (height - s * (b[1][1] + b[0][1])) / 2];
	projState.scale(s).translate(t);
	var districtColors = d3.scaleOrdinal().domain(cds).range(colors);

	stateG.selectAll("path")
		.data(cds.features)
		.enter()
		.append("path")
		.attr("d", cdPath)
		.attr("class", "cd")
		.attr("fill", (d, i) => districtColors(i))
		.attr("id", (d) => d.properties.cd)
		.attr("data", "none")
		.style("opacity", 0.7)
		.on("mouseover", mouseOverHandler)
		.on("mousemove", mouseMoveHandler)
		.on("mouseout", mouseOutHandler);
});

/*
Zoom for state map
*/
const stateZoom = d3.zoom()
    .scaleExtent([1, 8])
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
	if (d.properties.cd) {
		var region = "District";
	} else {
		var region = "State";
	};
	if (this.id == "98") {
		var regionId = "At-Large";
	} else {
		var regionId = `${this.id}`;
	};
	tooltip.html(d.id)
		.style("width", `${(region.length + regionId.length + 4) * 8}px`);
	tooltip.text(`${region}: ${regionId}`);
}
function mouseOutHandler() {
	var ifClicked = d3.select(this).attr("data");
	if (ifClicked == "none") {
		d3.select(this).style("opacity", 0.7);
	};
	console.log(ifClicked);
	tooltip.transition()
		.duration(50)
		.style("opacity", 0);
}
function clickHandler(d, i) {
	d3.selectAll(".state")
		.attr("data", "none")
		.attr("stroke", "none")
		.style("opacity", 0.7);
	d3.select(this)
		.attr("data", "clicked")
		.attr("stroke", "black")
		.attr("stroke-width", "0.1%")
		.style("opacity", 1);
	var stateId = d.properties.id;
	stateClickLabel.text(`State Selected: ${stateId}`);
	var stateTopo = d3.json(`data/${stateId}.topo.json`);
	stateTopo.then((state) => {
		var cds = topojson.feature(state, state.objects.data);
		var projState = d3.geoIdentity().reflectY(true);
		var cdPath = d3.geoPath(projState);
		var b = cdPath.bounds(cds);
		var s = .95 / Math.max((b[1][0] - b[0][0]) / width, (b[1][1] - b[0][1]) / height);
		var t = [(width - s * (b[1][0] + b[0][0])) / 2, (height - s * (b[1][1] + b[0][1])) / 2];
		projState.scale(s).translate(t);
		var districtColors = d3.scaleOrdinal().domain(cds).range(colors);

		d3.selectAll(".cd").remove();
		stateG.selectAll("path")
			.data(cds.features)
			.enter()
			.append("path")
			.attr("d", cdPath)
			.attr("class", "cd")
			.attr("fill", (d, i) => districtColors(i))
			.attr("id", (d) => d.properties.cd)
			.attr("data", "none")
			.style("opacity", 0.7)
			.on("mouseover", mouseOverHandler)
			.on("mousemove", mouseMoveHandler)
			.on("mouseout", mouseOutHandler);
	});
}
