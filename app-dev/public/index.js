const width = window.innerWidth * 0.45;
const height = window.innerHeight * 0.45;

/*
SVG elements and borders
*/
const usaSvg = d3.select("#usa-container")
	.append("svg")
	.attr("width", width)
	.attr("height", height)
	.attr("id", "usa-map")
	.attr("class", "map-svg");
const usaG = usaSvg.append("g");
const stateSvg = d3.select("#state-container")
	.append("svg")
	.attr("width", width)
	.attr("height", height)
	.attr("id", "state-map")
	.attr("class", "map-svg");
const stateG = stateSvg.append("g")
const borderRect = d3.selectAll(".map-svg")
	.append("rect")
	.attr("width", "100%")
	.attr("height", "100%")
	.attr("class", "border")
	.attr("fill", "none")
	.attr("stroke", "black")
	.attr("border", 5);

/*
Color schemes
*/
const stateColors = d3.scaleOrdinal().domain([0, 51]).range([
	"#855C75", "#D9AF6B", "#AF6458", "#736F4C", "#526A83", "#625377",
	"#68855C", "#9C9C5E", "#A06177", "#8C785D", "#467378", "#7C7C7C"
]);
const cdColors = [
	"#88CCEE", "#CC6677", "#DDCC77", "#117733", "#332288", "#AA4499",
	"#44AA99", "#999933", "#882255", "#661100", "#6699CC", "#888888"
];

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
		// .attr("stroke", "black")
		.attr("id", (d) => d.properties.id)
		.on("mouseover", mouseOverHandler)
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
var stateID = "AL";
const defaultStateTopo = d3.json(`data/${stateID}.topo.json`);
defaultStateTopo.then((state) => {
	var cds = topojson.feature(state, state.objects.data);
	var projState = d3.geoIdentity().reflectY(true);
	var cdPath = d3.geoPath(projState);
	var b = cdPath.bounds(cds);
	var s = .95 / Math.max((b[1][0] - b[0][0]) / width, (b[1][1] - b[0][1]) / height);
  var t = [(width - s * (b[1][0] + b[0][0])) / 2, (height - s * (b[1][1] + b[0][1])) / 2];
	projState.scale(s).translate(t);
	const stateColor = d3.scaleOrdinal().domain(cds).range(cdColors);

	stateG.selectAll("path")
		.data(cds.features)
		.enter()
		.append("path")
		.attr("d", cdPath)
		.attr("class", "cd")
		.attr("fill", (d, i) => stateColor(i))
		// .attr("stroke", "black")
		.attr("id", (d) => d.properties.cd + stateID);
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
function mouseOverHandler() {
	d3.select(this).attr("fill", "black");
}
function mouseOutHandler(d, i) {
	d3.select(this).attr("fill", stateColors(i));
};
function clickHandler(d) {
	var stateID = d.properties.id;
	var stateTopo = d3.json(`data/${stateID}.topo.json`);
	stateTopo.then((state) => {
		var cds = topojson.feature(state, state.objects.data);
		var projState = d3.geoIdentity().reflectY(true);
		var cdPath = d3.geoPath(projState);
		var b = cdPath.bounds(cds);
		var s = .95 / Math.max((b[1][0] - b[0][0]) / width, (b[1][1] - b[0][1]) / height);
		var t = [(width - s * (b[1][0] + b[0][0])) / 2, (height - s * (b[1][1] + b[0][1])) / 2];
		projState.scale(s).translate(t);
		const stateColor = d3.scaleOrdinal().domain(cds).range(cdColors);

		d3.selectAll(".cd").remove();
		stateG.selectAll("path")
			.data(cds.features)
			.enter()
			.append("path")
			.attr("d", cdPath)
			.attr("class", "cd")
			.attr("fill", (d, i) => stateColor(i))
			// .attr("stroke", "black")
			.attr("id", (d) => d.properties.cd + stateID);
	});
}

